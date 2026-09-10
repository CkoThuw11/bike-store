import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';
import { friendlyMessage, normalizeError } from '../../core/api/api-error';
import { CreateStoreCommand, StoreDto, UpdateStoreCommand } from '../../shared/types';
import { exportRowsToCsv } from '../../shared/utils/csv-export';
import { ToastService } from '../../shared/ui/toast/toast.service';

type FeedbackKind = 'success' | 'inactive' | 'warning' | 'danger';

@Component({
  selector: 'app-stores',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule],
  templateUrl: './stores.component.html',
  styleUrl: './stores.component.scss',
})
export class StoresComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly toasts = inject(ToastService);
  private readonly base = environment.apiUrl;

  exportCsv(): void {
    const rows = this.filtered();
    if (!rows.length) { this.toasts.info('Nothing to export.'); return; }
    exportRowsToCsv('stores', rows, [
      { header: 'ID', value: (r) => r.store_id },
      { header: 'Store name', value: (r) => r.store_name },
      { header: 'Phone', value: (r) => r.phone },
      { header: 'Email', value: (r) => r.email },
      { header: 'City', value: (r) => r.city },
      { header: 'State', value: (r) => r.state },
      { header: 'ZIP', value: (r) => r.zip_code },
      { header: 'Active', value: (r) => (r.is_active ? 'yes' : 'no') },
    ]);
    this.toasts.success(`Exported ${rows.length} stores.`);
  }

  readonly stores = signal<StoreDto[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly actionError = signal<string | null>(null);
  readonly feedback = signal<{ kind: FeedbackKind; title: string; message: string } | null>(null);
  readonly query = signal('');
  readonly drawerOpen = signal(false);
  readonly editing = signal<StoreDto | null>(null);

  readonly form = new FormGroup({
    store_name: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    phone: new FormControl('', { nonNullable: true }),
    email: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.email] }),
    street: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    city: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    state: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    zip_code: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
  });

  readonly filtered = computed(() => {
    const q = this.query().trim().toLowerCase();
    return this.stores().filter((store) =>
      [store.store_name, store.city, store.state, store.email].some((value) =>
        value.toLowerCase().includes(q)
      )
    );
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.http.get<StoreDto[]>(`${this.base}/stores/?limit=500`).subscribe({
      next: (stores) => {
        this.stores.set(this.sortById(stores.map((store) => this.normalizeStore(store))));
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(this.message(err, 'Failed to load stores.'));
        this.loading.set(false);
      },
    });
  }

  openCreate(): void {
    this.editing.set(null);
    this.actionError.set(null);
    this.form.reset({ store_name: '', phone: '', email: '', street: '', city: '', state: '', zip_code: '' });
    this.drawerOpen.set(true);
  }

  openEdit(store: StoreDto): void {
    this.editing.set(store);
    this.actionError.set(null);
    this.form.reset({
      store_name: store.store_name,
      phone: store.phone,
      email: store.email,
      street: store.street,
      city: store.city,
      state: store.state,
      zip_code: store.zip_code,
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

    const payload = this.form.getRawValue();
    const editing = this.editing();
    const request = editing
      ? this.http.put<StoreDto>(`${this.base}/stores/${editing.store_id}`, payload as UpdateStoreCommand)
      : this.http.post<StoreDto>(`${this.base}/stores/`, payload as CreateStoreCommand);

    this.saving.set(true);
    this.actionError.set(null);
    request.subscribe({
      next: (saved) => {
        this.saving.set(false);
        this.closeDrawer();
        this.upsertStore(saved);
        this.showFeedback('success', editing ? 'Store updated' : 'Store created', `${saved.store_name} is saved.`);
      },
      error: (err) => {
        this.actionError.set(this.message(err, 'Failed to save store.'));
        this.saving.set(false);
      },
    });
  }

  toggleActive(store: StoreDto): void {
    const currentlyActive = this.isStoreActive(store);
    const action = currentlyActive ? 'deactivate' : 'activate';
    const nextActive = !currentlyActive;
    this.http.post<StoreDto>(`${this.base}/stores/${store.store_id}/${action}`, {}).subscribe({
      next: (updated) => {
        this.upsertStore(this.normalizeStore({ ...store, ...updated, is_active: nextActive }));
        this.showFeedback(
          nextActive ? 'success' : 'inactive',
          nextActive ? 'Store activated' : 'Store deactivated',
          `${store.store_name} is now ${nextActive ? 'active' : 'inactive'}.`
        );
      },
      error: (err) => this.showFeedback('danger', 'Store update failed', this.message(err, `Failed to ${action} store.`)),
    });
  }

  delete(store: StoreDto): void {
    if (!confirm(`Delete ${store.store_name}?`)) return;
    this.http.delete<StoreDto>(`${this.base}/stores/${store.store_id}`).subscribe({
      next: () => {
        this.stores.update((stores) => stores.filter((item) => item.store_id !== store.store_id));
        this.showFeedback('success', 'Store deleted', `${store.store_name} was deleted.`);
      },
      error: (err) => this.showFeedback('danger', 'Store delete failed', this.message(err, 'Failed to delete store.')),
    });
  }

  closeFeedback(): void {
    this.feedback.set(null);
  }

  isStoreActive(store: StoreDto): boolean {
    return this.toBoolean(store.is_active);
  }

  private message(err: unknown, fallback: string): string {
    const appError = normalizeError(err);
    return friendlyMessage(appError.code, appError.message || fallback);
  }

  private upsertStore(store: StoreDto): void {
    const normalizedStore = this.normalizeStore(store);
    this.stores.update((stores) => {
      const exists = stores.some((item) => item.store_id === normalizedStore.store_id);
      const next = exists
        ? stores.map((item) => item.store_id === normalizedStore.store_id ? normalizedStore : item)
        : [...stores, normalizedStore];
      return this.sortById(next);
    });
  }

  private sortById(stores: StoreDto[]): StoreDto[] {
    return [...stores].sort((a, b) => a.store_id - b.store_id);
  }

  private showFeedback(kind: FeedbackKind, title: string, message: string): void {
    this.feedback.set({ kind, title, message });
  }

  private normalizeStore(store: StoreDto): StoreDto {
    return {
      ...store,
      is_active: this.toBoolean(store.is_active),
    };
  }

  private toBoolean(value: unknown): boolean {
    if (typeof value === 'boolean') return value;
    if (typeof value === 'number') return value === 1;
    if (typeof value === 'string') return value.toLowerCase() === 'true' || value === '1';
    return Boolean(value);
  }
}
