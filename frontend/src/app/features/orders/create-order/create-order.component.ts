import { Component, OnInit, computed, effect, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { EMPTY, Observable, expand, forkJoin, reduce, switchMap } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { friendlyMessage, normalizeError } from '../../../core/api/api-error';
import { CustomerDto, OrderDto, OrderItemDto, ProductDto } from '../../../shared/types';
import { formatPrice, parseDecimal } from '../../../shared/utils/format.utils';
import { loadSavedView, persistSavedView, clearSavedView } from '../../../shared/utils/saved-view';
import { ToastService } from '../../../shared/ui/toast/toast.service';

interface OrderDraft {
  step: number;
  customerId: number | null;
  items: { productId: number; quantity: number; discountPercent: number }[];
  requiredDate: string;
}

const DRAFT_KEY = 'create-order-draft';

interface DraftItem {
  product: ProductDto;
  quantity: number;
  discountPercent: number;
}

@Component({
  selector: 'app-create-order',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './create-order.component.html',
  styleUrl: './create-order.component.scss',
})
export class CreateOrderComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly toasts = inject(ToastService);
  private readonly base = environment.apiUrl;

  private draftRestored = false;

  constructor() {
    effect(() => {
      // Persist a serializable draft on every change once loaded
      if (this.loading()) return;
      const draft: OrderDraft = {
        step: this.step(),
        customerId: this.selectedCustomer()?.customer_id ?? null,
        items: this.items().map((i) => ({
          productId: i.product.product_id,
          quantity: i.quantity,
          discountPercent: i.discountPercent,
        })),
        requiredDate: this.requiredDate(),
      };
      const hasContent = draft.customerId != null || draft.items.length > 0;
      if (hasContent) persistSavedView(DRAFT_KEY, draft);
    });
  }

  private restoreDraft(): void {
    if (this.draftRestored) return;
    this.draftRestored = true;
    const draft = loadSavedView<OrderDraft | null>(DRAFT_KEY, null as any);
    if (!draft || (!draft.customerId && (!draft.items || !draft.items.length))) return;

    let restored = 0;
    if (draft.customerId != null) {
      const customer = this.customers().find((c) => c.customer_id === draft.customerId);
      if (customer) { this.selectedCustomer.set(customer); restored++; }
    }
    if (draft.items?.length) {
      const next = draft.items
        .map((it) => {
          const product = this.products().find((p) => p.product_id === it.productId);
          return product ? { product, quantity: it.quantity, discountPercent: it.discountPercent } : null;
        })
        .filter((x): x is DraftItem => x !== null);
      if (next.length) { this.items.set(next); restored += next.length; }
    }
    if (draft.requiredDate) this.requiredDate.set(draft.requiredDate);
    if (draft.step) this.step.set(Math.min(3, Math.max(1, draft.step)));

    if (restored > 0) {
      this.toasts.info('Restored unsaved order draft.', {
        label: 'Discard',
        handler: () => {
          clearSavedView(DRAFT_KEY);
          this.selectedCustomer.set(null);
          this.items.set([]);
          this.step.set(1);
        },
      });
    }
  }

  readonly customers = signal<CustomerDto[]>([]);
  readonly products = signal<ProductDto[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly success = signal<string | null>(null);
  readonly step = signal(1);
  readonly selectedCustomer = signal<CustomerDto | null>(null);
  readonly items = signal<DraftItem[]>([]);
  readonly selectedProductId = signal<number | null>(null);
  readonly customerQuery = signal('');
  readonly productQuery = signal('');
  readonly quantity = signal(1);
  readonly discountPercent = signal(0);
  readonly requiredDate = signal(this.defaultDate());

  readonly progress = computed(() => (this.step() / 3) * 100);
  readonly total = computed(() =>
    this.items().reduce((sum, item) => sum + this.lineTotal(item), 0)
  );
  readonly filteredCustomers = computed(() => {
    const q = this.customerQuery().trim().toLowerCase();
    return this.customers().filter((customer) =>
      `${customer.customer_id} ${customer.first_name} ${customer.last_name} ${customer.email} ${customer.city}`
        .toLowerCase()
        .includes(q)
    );
  });
  readonly filteredProducts = computed(() => {
    const q = this.productQuery().trim().toLowerCase();
    return this.products().filter((product) =>
      `${product.product_id} ${product.product_name}`
        .toLowerCase()
        .includes(q)
    );
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    forkJoin({
      customers: this.listAll<CustomerDto>('/customers/'),
      products: this.http.get<ProductDto[]>(`${this.base}/products/?limit=500`),
    }).subscribe({
      next: ({ customers, products }) => {
        const activeCustomers = customers.filter((customer) => customer.is_active !== false);
        const activeProducts = products.filter((product) => product.is_active !== false);
        this.customers.set(activeCustomers);
        this.products.set(activeProducts);
        this.selectedProductId.set(activeProducts[0]?.product_id ?? null);
        this.loading.set(false);
        this.restoreDraft();
      },
      error: (err) => {
        this.error.set(this.message(err, 'Failed to load order data.'));
        this.loading.set(false);
      },
    });
  }

  selectCustomer(customer: CustomerDto): void {
    this.selectedCustomer.set(customer);
    this.step.set(2);
  }

  setProductQuery(value: string): void {
    this.productQuery.set(value);
    const firstMatch = this.filteredProducts()[0];
    this.selectedProductId.set(firstMatch?.product_id ?? null);
  }

  addItem(): void {
    const product = this.products().find((item) => item.product_id === Number(this.selectedProductId()));
    if (!product) return;
    const quantity = Math.max(1, Number(this.quantity()) || 1);
    const discountPercent = Math.min(100, Math.max(0, Number(this.discountPercent()) || 0));
    this.items.update((items) => [...items, { product, quantity, discountPercent }]);
    this.quantity.set(1);
    this.discountPercent.set(0);
  }

  removeItem(index: number): void {
    this.items.update((items) => items.filter((_, current) => current !== index));
  }

  next(): void {
    if (this.step() === 1 && !this.selectedCustomer()) return;
    if (this.step() === 2 && this.items().length === 0) return;
    this.step.update((value) => Math.min(3, value + 1));
  }

  back(): void {
    this.step.update((value) => Math.max(1, value - 1));
  }

  placeOrder(): void {
    const customer = this.selectedCustomer();
    if (!customer || this.items().length === 0 || this.saving()) return;

    this.saving.set(true);
    this.error.set(null);
    this.success.set(null);

    this.http.post<OrderDto>(`${this.base}/orders/`, { customer_id: customer.customer_id }).pipe(
      switchMap((order) =>
        forkJoin(
          this.items().map((item) =>
            this.http.post<OrderItemDto>(`${this.base}/order-items/`, {
              order_id: order.order_id,
              product_id: item.product.product_id,
              quantity: item.quantity,
              discount: String(item.discountPercent / 100),
            })
          )
        ).pipe(
          switchMap(() =>
            this.http.post<OrderDto>(`${this.base}/orders/${order.order_id}/checkout`, {
              required_date: `${this.requiredDate()}T00:00:00`,
            })
          )
        )
      )
    ).subscribe({
      next: () => {
        this.saving.set(false);
        this.success.set('Order placed successfully.');
        clearSavedView(DRAFT_KEY);
        this.toasts.success('Order placed.');
        this.router.navigate(['/orders']);
      },
      error: (err) => {
        this.error.set(this.message(err, 'Failed to place order.'));
        this.saving.set(false);
      },
    });
  }

  lineTotal(item: DraftItem): number {
    const price = parseDecimal(item.product.list_price);
    return price * item.quantity * (1 - item.discountPercent / 100);
  }

  formatLine(item: DraftItem): string {
    return formatPrice(this.lineTotal(item));
  }

  formatPrice(value: string | number): string {
    return formatPrice(value);
  }

  private defaultDate(): string {
    const date = new Date();
    date.setDate(date.getDate() + 7);
    return date.toISOString().slice(0, 10);
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
}
