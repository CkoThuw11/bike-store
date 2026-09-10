import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { EMPTY, Observable, expand, forkJoin, reduce } from 'rxjs';
import { environment } from '../../../environments/environment';
import { friendlyMessage, normalizeError } from '../../core/api/api-error';
import { CustomerDto, ORDER_STATUS_LABELS, OrderDto, OrderStatus } from '../../shared/types';
import { formatDate } from '../../shared/utils/format.utils';
import { exportRowsToCsv } from '../../shared/utils/csv-export';
import { ToastService } from '../../shared/ui/toast/toast.service';

@Component({
  selector: 'app-orders',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './orders.component.html',
  styleUrl: './orders.component.scss',
})
export class OrdersComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly toasts = inject(ToastService);
  private readonly base = environment.apiUrl;

  exportCsv(): void {
    const rows = this.filtered();
    if (!rows.length) { this.toasts.info('Nothing to export.'); return; }
    const customerName = (id: number) => {
      const c = this.customers().find((x) => x.customer_id === id);
      return c ? `${c.first_name} ${c.last_name}` : `Customer #${id}`;
    };
    exportRowsToCsv('orders', rows, [
      { header: 'Order ID', value: (r) => r.order_id },
      { header: 'Customer', value: (r) => customerName(r.customer_id) },
      { header: 'Status', value: (r) => ORDER_STATUS_LABELS[r.order_status as OrderStatus] ?? r.order_status },
      { header: 'Order date', value: (r) => r.order_date },
      { header: 'Required date', value: (r) => r.required_date ?? '' },
      { header: 'Shipped date', value: (r) => r.shipped_date ?? '' },
      { header: 'Store', value: (r) => r.store_id },
      { header: 'Staff', value: (r) => r.staff_id },
    ]);
    this.toasts.success(`Exported ${rows.length} orders.`);
  }

  readonly orders = signal<OrderDto[]>([]);
  readonly customers = signal<CustomerDto[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly query = signal('');
  readonly statusFilter = signal('all');
  readonly pageSize = 20;
  readonly currentPage = signal(1);
  readonly savingId = signal<number | null>(null);
  readonly statuses = [1, 2, 3, 4, 5] as OrderStatus[];

  readonly filtered = computed(() => {
    const q = this.query().trim().toLowerCase();
    const status = this.statusFilter();
    return this.orders().filter((order) => {
      const customer = this.customerName(order.customer_id).toLowerCase();
      const matchesQuery = customer.includes(q) || String(order.order_id).includes(q);
      const matchesStatus = status === 'all' || String(order.order_status) === status;
      return matchesQuery && matchesStatus;
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
    forkJoin({
      orders: this.listAll<OrderDto>('/orders/'),
      customers: this.http.get<CustomerDto[]>(`${this.base}/customers/?limit=500`),
    }).subscribe({
      next: ({ orders, customers }) => {
        this.orders.set(this.sortOrders(orders));
        this.customers.set(customers);
        this.ensurePageInRange();
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(this.message(err, 'Failed to load orders.'));
        this.loading.set(false);
      },
    });
  }

  setQuery(value: string): void {
    this.query.set(value);
    this.resetPagination();
  }

  setStatusFilter(value: string): void {
    this.statusFilter.set(value);
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

  updateStatus(order: OrderDto, status: string | number): void {
    const order_status = Number(status) as OrderStatus;
    this.savingId.set(order.order_id);
    this.http.put<OrderDto>(`${this.base}/orders/${order.order_id}`, { order_status }).subscribe({
      next: () => {
        this.savingId.set(null);
        this.load();
      },
      error: (err) => {
        this.error.set(this.message(err, 'Failed to update order status.'));
        this.savingId.set(null);
      },
    });
  }

  delete(order: OrderDto): void {
    if (!confirm(`Delete order #${order.order_id}?`)) return;
    this.http.delete<OrderDto>(`${this.base}/orders/${order.order_id}`).subscribe({
      next: () => this.load(),
      error: (err) => this.error.set(this.message(err, 'Failed to delete order.')),
    });
  }

  customerName(id: number): string {
    const customer = this.customers().find((item) => item.customer_id === id);
    return customer ? `${customer.first_name} ${customer.last_name}` : `Customer #${id}`;
  }

  statusLabel(status: number): string {
    return ORDER_STATUS_LABELS[status as OrderStatus] ?? 'UNKNOWN';
  }

  formatDate(value: string | null): string {
    return formatDate(value);
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

  private sortOrders(orders: OrderDto[]): OrderDto[] {
    return [...orders].sort((a, b) => {
      const aTime = new Date(a.created_at || a.order_date).getTime();
      const bTime = new Date(b.created_at || b.order_date).getTime();
      return bTime - aTime || b.order_id - a.order_id;
    });
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
