import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';
import { normalizeError, friendlyMessage } from '../../core/api/api-error';
import { BrandDto, CreateBrandCommand, UpdateBrandCommand } from '../../shared/types';
import { formatDate } from '../../shared/utils/format.utils';
import { exportRowsToCsv } from '../../shared/utils/csv-export';
import { ToastService } from '../../shared/ui/toast/toast.service';

type FeedbackKind = 'success' | 'inactive' | 'danger';

@Component({
  selector: 'app-brands',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule],
  templateUrl: './brands.component.html',
  styleUrl: './brands.component.scss',
})
export class BrandsComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly toasts = inject(ToastService);
  private readonly base = environment.apiUrl;

  exportCsv(): void {
    const rows = this.filtered();
    if (!rows.length) { this.toasts.info('Nothing to export.'); return; }
    exportRowsToCsv('brands', rows, [
      { header: 'ID', value: (r) => r.brand_id },
      { header: 'Brand name', value: (r) => r.brand_name },
      { header: 'Active', value: (r) => (r.is_active ? 'yes' : 'no') },
      { header: 'Created', value: (r) => r.created_at },
    ]);
    this.toasts.success(`Exported ${rows.length} brands.`);
  }

  readonly items = signal<BrandDto[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly actionError = signal<string | null>(null);
  readonly feedback = signal<{ kind: FeedbackKind; title: string; message: string } | null>(null);
  readonly query = signal('');
  readonly drawerOpen = signal(false);
  readonly editing = signal<BrandDto | null>(null);

  readonly form = new FormGroup({
    brand_name: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
  });

  readonly filtered = computed(() => {
    const q = this.query().trim().toLowerCase();
    return this.items().filter((item) => item.brand_name.toLowerCase().includes(q));
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.http.get<BrandDto[]>(`${this.base}/brands/?limit=500`).subscribe({
      next: (items) => {
        this.items.set(this.sortById(items));
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(this.message(err, 'Failed to load brands.'));
        this.loading.set(false);
      },
    });
  }

  openCreate(): void {
    this.editing.set(null);
    this.actionError.set(null);
    this.form.reset({ brand_name: '' });
    this.drawerOpen.set(true);
  }

  openEdit(item: BrandDto): void {
    this.editing.set(item);
    this.actionError.set(null);
    this.form.reset({ brand_name: item.brand_name });
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

    const editing = this.editing();
    const payload = this.form.getRawValue();
    const request = editing
      ? this.http.put<BrandDto>(`${this.base}/brands/${editing.brand_id}`, payload as UpdateBrandCommand)
      : this.http.post<BrandDto>(`${this.base}/brands/`, payload as CreateBrandCommand);

    this.saving.set(true);
    this.actionError.set(null);
    request.subscribe({
      next: (saved) => {
        this.saving.set(false);
        this.closeDrawer();
        this.upsert(saved);
        this.showFeedback('success', editing ? 'Brand updated' : 'Brand created', `${saved.brand_name} is saved.`);
      },
      error: (err) => {
        this.actionError.set(this.message(err, 'Failed to save brand.'));
        this.saving.set(false);
      },
    });
  }

  toggleActive(item: BrandDto): void {
    const action = item.is_active ? 'deactivate' : 'activate';
    const nextActive = !item.is_active;
    this.http.post<BrandDto>(`${this.base}/brands/${item.brand_id}/${action}`, {}).subscribe({
      next: (updated) => {
        const brand = { ...item, ...updated, is_active: nextActive };
        this.upsert(brand);
        this.showFeedback(nextActive ? 'success' : 'inactive', nextActive ? 'Brand activated' : 'Brand deactivated', `${brand.brand_name} is now ${nextActive ? 'active' : 'inactive'}.`);
      },
      error: (err) => this.showFeedback('danger', 'Brand update failed', this.message(err, `Failed to ${action} brand.`)),
    });
  }

  delete(item: BrandDto): void {
    if (!confirm(`Delete ${item.brand_name}?`)) return;
    this.http.delete<BrandDto>(`${this.base}/brands/${item.brand_id}`).subscribe({
      next: () => this.load(),
      error: (err) => this.error.set(this.message(err, 'Failed to delete brand. Deactivate it first if needed.')),
    });
  }

  formatDate(value: string): string {
    return formatDate(value);
  }

  closeFeedback(): void {
    this.feedback.set(null);
  }

  private message(err: unknown, fallback: string): string {
    const appError = normalizeError(err);
    return friendlyMessage(appError.code, appError.message || fallback);
  }

  private upsert(item: BrandDto): void {
    this.items.update((items) => this.sortById(items.some((current) => current.brand_id === item.brand_id)
      ? items.map((current) => current.brand_id === item.brand_id ? item : current)
      : [...items, item]));
  }

  private sortById(items: BrandDto[]): BrandDto[] {
    return [...items].sort((a, b) => a.brand_id - b.brand_id);
  }

  private showFeedback(kind: FeedbackKind, title: string, message: string): void {
    this.feedback.set({ kind, title, message });
  }
}
