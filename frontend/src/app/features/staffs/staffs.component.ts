import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { environment } from '../../../environments/environment';
import { friendlyMessage, normalizeError } from '../../core/api/api-error';
import { CreateStaffCommand, StaffDto, StoreDto, UpdateStaffCommand } from '../../shared/types';
import { exportRowsToCsv } from '../../shared/utils/csv-export';
import { ToastService } from '../../shared/ui/toast/toast.service';

type FeedbackKind = 'success' | 'inactive' | 'danger';

@Component({
  selector: 'app-staffs',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule],
  templateUrl: './staffs.component.html',
  styleUrl: './staffs.component.scss',
})
export class StaffsComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly toasts = inject(ToastService);
  private readonly base = environment.apiUrl;

  exportCsv(): void {
    const rows = this.filtered();
    if (!rows.length) { this.toasts.info('Nothing to export.'); return; }
    const storeName = (id: number) => this.stores().find((s) => s.store_id === id)?.store_name ?? `Store #${id}`;
    exportRowsToCsv('staff', rows, [
      { header: 'ID', value: (r) => r.staff_id },
      { header: 'First name', value: (r) => r.first_name },
      { header: 'Last name', value: (r) => r.last_name },
      { header: 'Email', value: (r) => r.email },
      { header: 'Phone', value: (r) => r.phone },
      { header: 'Store', value: (r) => storeName(r.store_id) },
      { header: 'Manager ID', value: (r) => r.manager_id ?? '' },
      { header: 'Active', value: (r) => (r.is_active ? 'yes' : 'no') },
    ]);
    this.toasts.success(`Exported ${rows.length} staff.`);
  }

  readonly staffs = signal<StaffDto[]>([]);
  readonly stores = signal<StoreDto[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly actionError = signal<string | null>(null);
  readonly feedback = signal<{ kind: FeedbackKind; title: string; message: string } | null>(null);
  readonly query = signal('');
  readonly storeFilter = signal('all');
  readonly drawerOpen = signal(false);
  readonly editing = signal<StaffDto | null>(null);

  readonly form = new FormGroup({
    first_name: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    last_name: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    email: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.email] }),
    phone: new FormControl('', { nonNullable: true }),
    store_id: new FormControl<number | null>(null, { validators: [Validators.required] }),
    manager_id: new FormControl<number | null>(null),
  });

  readonly filtered = computed(() => {
    const q = this.query().trim().toLowerCase();
    const store = this.storeFilter();
    return this.staffs().filter((staff) => {
      const name = `${staff.first_name} ${staff.last_name}`.toLowerCase();
      const matchesQuery = name.includes(q) || staff.email.toLowerCase().includes(q);
      const matchesStore = store === 'all' || String(staff.store_id) === store;
      return matchesQuery && matchesStore;
    });
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    forkJoin({
      staffs: this.http.get<StaffDto[]>(`${this.base}/staffs/?limit=500`),
      stores: this.http.get<StoreDto[]>(`${this.base}/stores/?limit=500`),
    }).subscribe({
      next: ({ staffs, stores }) => {
        this.staffs.set(this.sortById(staffs));
        this.stores.set(stores);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(this.message(err, 'Failed to load staff.'));
        this.loading.set(false);
      },
    });
  }

  openCreate(): void {
    this.editing.set(null);
    this.actionError.set(null);
    this.form.reset({
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      store_id: this.stores()[0]?.store_id ?? null,
      manager_id: null,
    });
    this.drawerOpen.set(true);
  }

  openEdit(staff: StaffDto): void {
    this.editing.set(staff);
    this.actionError.set(null);
    this.form.reset({
      first_name: staff.first_name,
      last_name: staff.last_name,
      email: staff.email,
      phone: staff.phone,
      store_id: staff.store_id,
      manager_id: staff.manager_id,
    });
    this.drawerOpen.set(true);
  }

  closeDrawer(): void {
    if (this.saving()) return;
    this.drawerOpen.set(false);
    this.editing.set(null);
    this.actionError.set(null);
  }

  save(): void {
    if (this.form.invalid || this.saving()) {
      this.form.markAllAsTouched();
      return;
    }

    const raw = this.form.getRawValue();
    const payload: CreateStaffCommand = {
      first_name: raw.first_name,
      last_name: raw.last_name,
      email: raw.email,
      phone: raw.phone,
      store_id: raw.store_id!,
      manager_id: raw.manager_id || null,
    };
    const editing = this.editing();
    const request = editing
      ? this.http.put<StaffDto>(`${this.base}/staffs/${editing.staff_id}`, payload as UpdateStaffCommand)
      : this.http.post<StaffDto>(`${this.base}/staffs/`, payload);

    this.saving.set(true);
    this.actionError.set(null);
    request.subscribe({
      next: (saved) => {
        this.saving.set(false);
        this.closeDrawer();
        this.upsert(saved);
        this.showFeedback('success', editing ? 'Staff updated' : 'Staff created', `${saved.first_name} ${saved.last_name} is saved.`);
      },
      error: (err) => {
        this.actionError.set(this.message(err, 'Failed to save staff.'));
        this.saving.set(false);
      },
    });
  }

  toggleActive(staff: StaffDto): void {
    const action = staff.is_active ? 'deactivate' : 'activate';
    const nextActive = !staff.is_active;
    this.http.post<StaffDto>(`${this.base}/staffs/${staff.staff_id}/${action}`, {}).subscribe({
      next: (updated) => {
        const nextStaff = { ...staff, ...updated, is_active: nextActive };
        this.upsert(nextStaff);
        this.showFeedback(nextActive ? 'success' : 'inactive', nextActive ? 'Staff activated' : 'Staff deactivated', `${nextStaff.first_name} ${nextStaff.last_name} is now ${nextActive ? 'active' : 'inactive'}.`);
      },
      error: (err) => this.showFeedback('danger', 'Staff update failed', this.message(err, `Failed to ${action} staff.`)),
    });
  }

  delete(staff: StaffDto): void {
    if (!confirm(`Delete ${staff.first_name} ${staff.last_name}?`)) return;
    this.http.delete<StaffDto>(`${this.base}/staffs/${staff.staff_id}`).subscribe({
      next: () => this.load(),
      error: (err) => this.error.set(this.message(err, 'Failed to delete staff.')),
    });
  }

  storeName(id: number): string {
    return this.stores().find((store) => store.store_id === id)?.store_name ?? `Store #${id}`;
  }

  managerName(id: number | null): string {
    if (!id) return 'No manager';
    const manager = this.staffs().find((staff) => staff.staff_id === id);
    return manager ? `${manager.first_name} ${manager.last_name}` : `Staff #${id}`;
  }

  closeFeedback(): void {
    this.feedback.set(null);
  }

  private message(err: unknown, fallback: string): string {
    const appError = normalizeError(err);
    return friendlyMessage(appError.code, appError.message || fallback);
  }

  private upsert(staff: StaffDto): void {
    this.staffs.update((staffs) => this.sortById(staffs.some((item) => item.staff_id === staff.staff_id)
      ? staffs.map((item) => item.staff_id === staff.staff_id ? staff : item)
      : [...staffs, staff]));
  }

  private sortById(staffs: StaffDto[]): StaffDto[] {
    return [...staffs].sort((a, b) => a.staff_id - b.staff_id);
  }

  private showFeedback(kind: FeedbackKind, title: string, message: string): void {
    this.feedback.set({ kind, title, message });
  }
}
