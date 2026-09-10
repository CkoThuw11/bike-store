import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';
import { normalizeError, friendlyMessage } from '../../core/api/api-error';
import { CategoryDto, CreateCategoryCommand, UpdateCategoryCommand } from '../../shared/types';
import { formatDate } from '../../shared/utils/format.utils';
import { exportRowsToCsv } from '../../shared/utils/csv-export';
import { ToastService } from '../../shared/ui/toast/toast.service';

type FeedbackKind = 'success' | 'inactive' | 'danger';

@Component({
  selector: 'app-categories',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule],
  templateUrl: './categories.component.html',
  styleUrl: './categories.component.scss',
})
export class CategoriesComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly toasts = inject(ToastService);
  private readonly base = environment.apiUrl;

  exportCsv(): void {
    const rows = this.filtered();
    if (!rows.length) { this.toasts.info('Nothing to export.'); return; }
    exportRowsToCsv('categories', rows, [
      { header: 'ID', value: (r) => r.category_id },
      { header: 'Category name', value: (r) => r.category_name },
      { header: 'Active', value: (r) => (r.is_active ? 'yes' : 'no') },
      { header: 'Created', value: (r) => r.created_at },
    ]);
    this.toasts.success(`Exported ${rows.length} categories.`);
  }

  readonly items = signal<CategoryDto[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly actionError = signal<string | null>(null);
  readonly feedback = signal<{ kind: FeedbackKind; title: string; message: string } | null>(null);
  readonly query = signal('');
  readonly drawerOpen = signal(false);
  readonly editing = signal<CategoryDto | null>(null);

  readonly form = new FormGroup({
    category_name: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
  });

  readonly filtered = computed(() => {
    const q = this.query().trim().toLowerCase();
    return this.items().filter((item) => item.category_name.toLowerCase().includes(q));
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.http.get<CategoryDto[]>(`${this.base}/categories/?limit=500`).subscribe({
      next: (items) => {
        this.items.set(this.sortById(items));
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(this.message(err, 'Failed to load categories.'));
        this.loading.set(false);
      },
    });
  }

  openCreate(): void {
    this.editing.set(null);
    this.actionError.set(null);
    this.form.reset({ category_name: '' });
    this.drawerOpen.set(true);
  }

  openEdit(item: CategoryDto): void {
    this.editing.set(item);
    this.actionError.set(null);
    this.form.reset({ category_name: item.category_name });
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
      ? this.http.put<CategoryDto>(`${this.base}/categories/${editing.category_id}`, payload as UpdateCategoryCommand)
      : this.http.post<CategoryDto>(`${this.base}/categories/`, payload as CreateCategoryCommand);

    this.saving.set(true);
    this.actionError.set(null);
    request.subscribe({
      next: (saved) => {
        this.saving.set(false);
        this.closeDrawer();
        this.upsert(saved);
        this.showFeedback('success', editing ? 'Category updated' : 'Category created', `${saved.category_name} is saved.`);
      },
      error: (err) => {
        this.actionError.set(this.message(err, 'Failed to save category.'));
        this.saving.set(false);
      },
    });
  }

  toggleActive(item: CategoryDto): void {
    const action = item.is_active ? 'deactivate' : 'activate';
    const nextActive = !item.is_active;
    this.http.post<CategoryDto>(`${this.base}/categories/${item.category_id}/${action}`, {}).subscribe({
      next: (updated) => {
        const category = { ...item, ...updated, is_active: nextActive };
        this.upsert(category);
        this.showFeedback(nextActive ? 'success' : 'inactive', nextActive ? 'Category activated' : 'Category deactivated', `${category.category_name} is now ${nextActive ? 'active' : 'inactive'}.`);
      },
      error: (err) => this.showFeedback('danger', 'Category update failed', this.message(err, `Failed to ${action} category.`)),
    });
  }

  delete(item: CategoryDto): void {
    if (!confirm(`Delete ${item.category_name}?`)) return;
    this.http.delete<CategoryDto>(`${this.base}/categories/${item.category_id}`).subscribe({
      next: () => this.load(),
      error: (err) => this.error.set(this.message(err, 'Failed to delete category.')),
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

  private upsert(item: CategoryDto): void {
    this.items.update((items) => this.sortById(items.some((current) => current.category_id === item.category_id)
      ? items.map((current) => current.category_id === item.category_id ? item : current)
      : [...items, item]));
  }

  private sortById(items: CategoryDto[]): CategoryDto[] {
    return [...items].sort((a, b) => a.category_id - b.category_id);
  }

  private showFeedback(kind: FeedbackKind, title: string, message: string): void {
    this.feedback.set({ kind, title, message });
  }
}
