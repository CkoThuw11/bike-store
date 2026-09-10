import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { EMPTY, Observable, expand, reduce } from 'rxjs';
import { environment } from '../../../environments/environment';
import { friendlyMessage, normalizeError } from '../../core/api/api-error';
import { CreateCustomerCommand, CustomerDto, UpdateCustomerCommand } from '../../shared/types';
import { exportRowsToCsv } from '../../shared/utils/csv-export';
import { ToastService } from '../../shared/ui/toast/toast.service';

type FeedbackKind = 'success' | 'inactive' | 'danger';

@Component({
  selector: 'app-customers',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule],
  templateUrl: './customers.component.html',
  styleUrl: './customers.component.scss',
})
export class CustomersComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly toasts = inject(ToastService);
  private readonly base = environment.apiUrl;

  exportCsv(): void {
    const rows = this.filtered();
    if (!rows.length) { this.toasts.info('Nothing to export.'); return; }
    exportRowsToCsv('customers', rows, [
      { header: 'ID', value: (r) => r.customer_id },
      { header: 'First name', value: (r) => r.first_name },
      { header: 'Last name', value: (r) => r.last_name },
      { header: 'Email', value: (r) => r.email },
      { header: 'Phone', value: (r) => r.phone },
      { header: 'City', value: (r) => r.city },
      { header: 'State', value: (r) => r.state },
      { header: 'ZIP', value: (r) => r.zip_code },
      { header: 'Active', value: (r) => (r.is_active ? 'yes' : 'no') },
    ]);
    this.toasts.success(`Exported ${rows.length} customers.`);
  }

  readonly customers = signal<CustomerDto[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly actionError = signal<string | null>(null);
  readonly feedback = signal<{ kind: FeedbackKind; title: string; message: string } | null>(null);
  readonly query = signal('');
  readonly pageSize = 20;
  readonly currentPage = signal(1);
  readonly drawerOpen = signal(false);
  readonly editing = signal<CustomerDto | null>(null);

  readonly form = new FormGroup({
    first_name: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    last_name: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    phone: new FormControl('', { nonNullable: true }),
    email: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.email] }),
    street: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    city: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    state: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    zip_code: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
  });

  readonly filtered = computed(() => {
    const q = this.query().trim().toLowerCase();
    return this.customers().filter((customer) => {
      const name = `${customer.first_name} ${customer.last_name}`.toLowerCase();
      return [name, customer.email.toLowerCase(), customer.city.toLowerCase()].some((value) => value.includes(q));
    });
  });
  readonly totalPages = computed(() => Math.max(1, Math.ceil(this.filtered().length / this.pageSize)));
  readonly paginated = computed(() => {
    const start = (this.currentPage() - 1) * this.pageSize;
    return this.filtered().slice(start, start + this.pageSize);
  });
  readonly visiblePages = computed(() => {
    const total = this.totalPages();
    const current = this.currentPage();
    const maxVisible = 5;
    let start = Math.max(1, current - Math.floor(maxVisible / 2));
    const end = Math.min(total, start + maxVisible - 1);
    start = Math.max(1, end - maxVisible + 1);
    return Array.from({ length: end - start + 1 }, (_, index) => start + index);
  });
  readonly pageStart = computed(() => this.filtered().length === 0 ? 0 : (this.currentPage() - 1) * this.pageSize + 1);
  readonly pageEnd = computed(() => Math.min(this.currentPage() * this.pageSize, this.filtered().length));

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.listAll<CustomerDto>('/customers/').subscribe({
      next: (customers) => {
        this.customers.set(this.sortById(customers));
        this.ensurePageInRange();
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(this.message(err, 'Failed to load customers.'));
        this.loading.set(false);
      },
    });
  }

  setQuery(value: string): void {
    this.query.set(value);
    this.resetPagination();
  }

  goToPage(page: number): void {
    this.currentPage.set(Math.min(Math.max(page, 1), this.totalPages()));
  }

  previousPage(): void {
    this.goToPage(this.currentPage() - 1);
  }

  nextPage(): void {
    this.goToPage(this.currentPage() + 1);
  }

  openCreate(): void {
    this.editing.set(null);
    this.actionError.set(null);
    this.form.reset({ first_name: '', last_name: '', phone: '', email: '', street: '', city: '', state: '', zip_code: '' });
    this.drawerOpen.set(true);
  }

  openEdit(customer: CustomerDto): void {
    this.editing.set(customer);
    this.actionError.set(null);
    this.form.reset({
      first_name: customer.first_name,
      last_name: customer.last_name,
      phone: customer.phone,
      email: customer.email,
      street: customer.street,
      city: customer.city,
      state: customer.state,
      zip_code: customer.zip_code,
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
    const payload: CreateCustomerCommand = {
      first_name: raw.first_name,
      last_name: raw.last_name,
      phone: raw.phone,
      email: raw.email,
      address: {
        street: raw.street,
        city: raw.city,
        state: raw.state,
        zip_code: raw.zip_code,
      },
    };

    const editing = this.editing();
    const request = editing
      ? this.http.put<CustomerDto>(`${this.base}/customers/${editing.customer_id}`, payload as UpdateCustomerCommand)
      : this.http.post<CustomerDto>(`${this.base}/customers/`, payload);

    this.saving.set(true);
    this.actionError.set(null);
    request.subscribe({
      next: (saved) => {
        this.saving.set(false);
        this.closeDrawer();
        this.upsert(saved);
        this.showFeedback('success', editing ? 'Customer updated' : 'Customer created', `${saved.first_name} ${saved.last_name} is saved.`);
      },
      error: (err) => {
        this.actionError.set(this.message(err, 'Failed to save customer.'));
        this.saving.set(false);
      },
    });
  }

  toggleActive(customer: CustomerDto): void {
    const action = customer.is_active ? 'deactivate' : 'activate';
    const nextActive = !customer.is_active;
    this.http.post<CustomerDto>(`${this.base}/customers/${customer.customer_id}/${action}`, {}).subscribe({
      next: (updated) => {
        const nextCustomer = { ...customer, ...updated, is_active: nextActive };
        this.upsert(nextCustomer);
        this.showFeedback(nextActive ? 'success' : 'inactive', nextActive ? 'Customer activated' : 'Customer deactivated', `${nextCustomer.first_name} ${nextCustomer.last_name} is now ${nextActive ? 'active' : 'inactive'}.`);
      },
      error: (err) => this.showFeedback('danger', 'Customer update failed', this.message(err, `Failed to ${action} customer.`)),
    });
  }

  delete(customer: CustomerDto): void {
    if (!confirm(`Delete ${customer.first_name} ${customer.last_name}?`)) return;
    this.http.delete<CustomerDto>(`${this.base}/customers/${customer.customer_id}`).subscribe({
      next: () => this.load(),
      error: (err) => this.error.set(this.message(err, 'Failed to delete customer.')),
    });
  }

  private message(err: unknown, fallback: string): string {
    const appError = normalizeError(err);
    return friendlyMessage(appError.code, appError.message || fallback);
  }

  private listAll<T>(endpoint: string, limit = 500): Observable<T[]> {
    return this.http.get<T[]>(`${this.base}${endpoint}?skip=0&limit=${limit}`).pipe(
      expand((items, index) => items.length === limit
        ? this.http.get<T[]>(`${this.base}${endpoint}?skip=${(index + 1) * limit}&limit=${limit}`)
        : EMPTY
      ),
      reduce((all, items) => [...all, ...items], [] as T[])
    );
  }

  closeFeedback(): void {
    this.feedback.set(null);
  }

  private upsert(customer: CustomerDto): void {
    this.customers.update((customers) => this.sortById(customers.some((item) => item.customer_id === customer.customer_id)
      ? customers.map((item) => item.customer_id === customer.customer_id ? customer : item)
      : [...customers, customer]));
    this.ensurePageInRange();
  }

  private sortById(customers: CustomerDto[]): CustomerDto[] {
    return [...customers].sort((a, b) => a.customer_id - b.customer_id);
  }

  private showFeedback(kind: FeedbackKind, title: string, message: string): void {
    this.feedback.set({ kind, title, message });
  }

  private resetPagination(): void {
    this.currentPage.set(1);
  }

  private ensurePageInRange(): void {
    if (this.currentPage() > this.totalPages()) {
      this.currentPage.set(this.totalPages());
    }
  }
}
