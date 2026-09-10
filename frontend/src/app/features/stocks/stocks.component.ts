import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { EMPTY, Observable, expand, forkJoin, reduce } from 'rxjs';
import { environment } from '../../../environments/environment';
import { friendlyMessage, normalizeError } from '../../core/api/api-error';
import { ProductDto, StockDto, StoreDto } from '../../shared/types';
import { formatDateTime } from '../../shared/utils/format.utils';
import { exportRowsToCsv } from '../../shared/utils/csv-export';
import { ToastService } from '../../shared/ui/toast/toast.service';
import { AlertsService } from '../../shared/state/alerts.service';

type FeedbackKind = 'success' | 'danger';

@Component({
  selector: 'app-stocks',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './stocks.component.html',
  styleUrl: './stocks.component.scss',
})
export class StocksComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly toasts = inject(ToastService);
  private readonly alerts = inject(AlertsService);
  private readonly base = environment.apiUrl;

  readonly LOW_STOCK_THRESHOLD = 5;

  exportCsv(): void {
    const rows = this.filtered();
    if (!rows.length) { this.toasts.info('Nothing to export.'); return; }
    exportRowsToCsv('stock', rows, [
      { header: 'Store', value: (r) => this.storeName(r.store_id) },
      { header: 'Product', value: (r) => this.productName(r.product_id) },
      { header: 'Quantity', value: (r) => r.quantity },
      { header: 'Updated', value: (r) => r.updated_at },
    ]);
    this.toasts.success(`Exported ${rows.length} stock rows.`);
  }

  readonly stocks = signal<StockDto[]>([]);
  readonly stores = signal<StoreDto[]>([]);
  readonly products = signal<ProductDto[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly feedback = signal<{ kind: FeedbackKind; title: string; message: string } | null>(null);
  readonly savingKey = signal<string | null>(null);
  readonly storeFilter = signal('all');
  readonly productFilter = signal('all');
  readonly pageSize = 20;
  readonly currentPage = signal(1);
  readonly drafts = signal<Record<string, number>>({});
  readonly editingStock = signal<StockDto | null>(null);
  readonly editQuantity = signal(0);

  readonly filtered = computed(() => {
    const store = this.storeFilter();
    const product = this.productFilter();
    return this.stocks().filter((stock) => {
      const matchesStore = store === 'all' || String(stock.store_id) === store;
      const matchesProduct = product === 'all' || String(stock.product_id) === product;
      return matchesStore && matchesProduct;
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

  readonly lowStockCount = computed(() => this.stocks().filter((stock) => stock.quantity < 5).length);

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    forkJoin({
      stocks: this.listAll<StockDto>('/stocks/'),
      stores: this.listAll<StoreDto>('/stores/'),
      products: this.listAll<ProductDto>('/products/'),
    }).subscribe({
      next: ({ stocks, stores, products }) => {
        this.stocks.set(stocks);
        this.stores.set(stores);
        this.products.set(products);
        this.drafts.set(Object.fromEntries(stocks.map((stock) => [this.key(stock), stock.quantity])));
        this.ensurePageInRange();
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(this.message(err, 'Failed to load stock.'));
        this.loading.set(false);
      },
    });
  }

  setStoreFilter(value: string): void {
    this.storeFilter.set(value);
    this.resetPagination();
  }

  setProductFilter(value: string): void {
    this.productFilter.set(value);
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

  openEdit(stock: StockDto): void {
    this.editingStock.set(stock);
    this.editQuantity.set(stock.quantity);
  }

  closeDrawer(): void {
    if (this.savingKey()) return;
    this.editingStock.set(null);
  }

  setEditQuantity(value: number | string): void {
    this.editQuantity.set(Math.max(0, Number(value) || 0));
  }

  saveStock(): void {
    const stock = this.editingStock();
    if (!stock) return;
    const key = this.key(stock);
    const quantity = this.editQuantity();
    this.savingKey.set(key);
    this.http.put<StockDto>(`${this.base}/stocks/${stock.store_id}/${stock.product_id}`, { quantity }).subscribe({
      next: (updated) => {
        this.upsertStock(updated);
        this.drafts.update((drafts) => ({ ...drafts, [this.key(updated)]: updated.quantity }));
        this.editingStock.set(null);
        this.savingKey.set(null);
        this.alerts.refresh();
        this.toasts.success(`${this.productName(stock.product_id)} → ${updated.quantity} units at ${this.storeName(stock.store_id)}.`);
      },
      error: (err) => {
        this.showFeedback('danger', 'Stock update failed', this.message(err, 'Failed to update stock.'));
        this.savingKey.set(null);
      },
    });
  }

  storeName(id: number): string {
    return this.stores().find((store) => store.store_id === id)?.store_name ?? `Store #${id}`;
  }

  productName(id: number): string {
    return this.products().find((product) => product.product_id === id)?.product_name ?? `Product #${id}`;
  }

  formatDate(value: string): string {
    return formatDateTime(value);
  }

  key(stock: StockDto): string {
    return `${stock.store_id}:${stock.product_id}`;
  }

  closeFeedback(): void {
    this.feedback.set(null);
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

  private upsertStock(stock: StockDto): void {
    this.stocks.update((stocks) =>
      stocks.map((item) => this.key(item) === this.key(stock) ? stock : item)
    );
    this.ensurePageInRange();
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
