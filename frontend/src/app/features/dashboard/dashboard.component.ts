// src/app/features/dashboard/dashboard.component.ts
import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterLink } from '@angular/router';
import { EMPTY, Observable, expand, forkJoin, reduce } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  BrandDto, CategoryDto, ProductDto, CustomerDto,
  OrderDto, StockDto, ORDER_STATUS_LABELS
} from '../../shared/types';
import { formatDate } from '../../shared/utils/format.utils';

type StatColor = 'orange' | 'blue' | 'green' | 'yellow' | 'purple' | 'red';

interface StatCard {
  label: string;
  value: number;
  delta: number;
  icon: string;
  color: StatColor;
  route: string;
}

interface LowStockRow {
  product_id: number;
  store_id: number;
  quantity: number;
  product_name: string;
}

const LOW_STOCK_THRESHOLD = 5;
const SEVEN_DAYS_MS = 7 * 24 * 60 * 60 * 1000;

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiUrl;

  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly products = signal<ProductDto[]>([]);
  readonly brands = signal<BrandDto[]>([]);
  readonly categories = signal<CategoryDto[]>([]);
  readonly customers = signal<CustomerDto[]>([]);
  readonly orders = signal<OrderDto[]>([]);
  readonly stocks = signal<StockDto[]>([]);

  readonly statCards = computed((): StatCard[] => {
    const now = Date.now();
    const cutoff = now - SEVEN_DAYS_MS;
    const since = (arr: ReadonlyArray<{ created_at?: string }>): number =>
      arr.filter((x) => x.created_at && new Date(x.created_at).getTime() >= cutoff).length;

    return [
      { label: 'Products',    value: this.products().length,   delta: 0,
        icon: 'bike',          color: 'orange', route: '/products' },
      { label: 'Brands',      value: this.brands().length,     delta: since(this.brands()),
        icon: 'bookmark',      color: 'blue',   route: '/brands' },
      { label: 'Categories',  value: this.categories().length, delta: since(this.categories()),
        icon: 'tag',           color: 'green',  route: '/categories' },
      { label: 'Customers',   value: this.customers().length,  delta: since(this.customers()),
        icon: 'user-heart',    color: 'yellow', route: '/customers' },
      { label: 'Orders',      value: this.orders().length,     delta: since(this.orders()),
        icon: 'shopping-cart', color: 'purple', route: '/orders' },
      { label: 'Stock Items', value: this.stocks().length,     delta: 0,
        icon: 'package',       color: 'red',    route: '/stocks' },
    ];
  });

  readonly recentOrders = computed(() =>
    [...this.orders()]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 8)
  );

  readonly lowStock = computed<LowStockRow[]>(() => {
    const productNameById = new Map(this.products().map((p) => [p.product_id, p.product_name]));
    return this.stocks()
      .filter((s) => s.quantity < LOW_STOCK_THRESHOLD)
      .sort((a, b) => a.quantity - b.quantity)
      .slice(0, 6)
      .map((s) => ({
        product_id: s.product_id,
        store_id: s.store_id,
        quantity: s.quantity,
        product_name: productNameById.get(s.product_id) ?? `Product #${s.product_id}`,
      }));
  });

  readonly quickActions = [
    { label: 'New Product', route: '/products', queryParams: { create: 1 }, color: 'orange' as const },
    { label: 'New Order', route: '/orders/new', queryParams: undefined, color: 'purple' as const },
    { label: 'New Customer', route: '/customers', queryParams: { create: 1 }, color: 'yellow' as const },
    { label: 'Adjust Stock', route: '/stocks', queryParams: undefined, color: 'red' as const },
  ];

  ngOnInit(): void {
    forkJoin({
      products:   this.http.get<ProductDto[]>(`${this.base}/products/?limit=500`),
      brands:     this.http.get<BrandDto[]>(`${this.base}/brands/?limit=500`),
      categories: this.http.get<CategoryDto[]>(`${this.base}/categories/?limit=500`),
      customers:  this.listAll<CustomerDto>('/customers/'),
      orders:     this.listAll<OrderDto>('/orders/'),
      stocks:     this.listAll<StockDto>('/stocks/'),
    }).subscribe({
      next: (data) => {
        this.products.set(data.products);
        this.brands.set(data.brands);
        this.categories.set(data.categories);
        this.customers.set(data.customers);
        this.orders.set(data.orders);
        this.stocks.set(data.stocks);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Failed to load dashboard data. Make sure the backend is running.');
        this.loading.set(false);
      },
    });
  }

  statusLabel(status: number): string {
    return ORDER_STATUS_LABELS[status as keyof typeof ORDER_STATUS_LABELS] ?? 'UNKNOWN';
  }

  formatDate(value: string): string {
    return formatDate(value);
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
