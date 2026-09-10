import { Component, OnInit, computed, effect, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { forkJoin } from 'rxjs';
import { environment } from '../../../environments/environment';
import { friendlyMessage, normalizeError } from '../../core/api/api-error';
import {
  BrandDto,
  CategoryDto,
  CreateProductCommand,
  ProductDto,
  UpdateProductCommand,
} from '../../shared/types';
import { formatPrice } from '../../shared/utils/format.utils';
import { exportRowsToCsv } from '../../shared/utils/csv-export';
import { loadSavedView, persistSavedView } from '../../shared/utils/saved-view';
import { ToastService } from '../../shared/ui/toast/toast.service';
import { ConfirmDialogComponent } from '../../shared/ui/confirm/confirm-dialog.component';
import { DrawerKeysDirective } from '../../shared/ui/drawer/drawer-keys.directive';

interface ProductsView {
  query: string;
  brandFilter: string;
  categoryFilter: string;
  page: number;
}

const VIEW_KEY = 'products';
const DEFAULT_VIEW: ProductsView = { query: '', brandFilter: 'all', categoryFilter: 'all', page: 1 };

type FeedbackKind = 'success' | 'inactive' | 'warning' | 'danger';

@Component({
  selector: 'app-products',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule, ConfirmDialogComponent, DrawerKeysDirective],
  templateUrl: './products.component.html',
  styleUrl: './products.component.scss',
})
export class ProductsComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly toasts = inject(ToastService);
  private readonly base = environment.apiUrl;
  readonly confirmDiscard = signal(false);

  readonly products = signal<ProductDto[]>([]);
  readonly brands = signal<BrandDto[]>([]);
  readonly categories = signal<CategoryDto[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly actionError = signal<string | null>(null);
  readonly feedback = signal<{ kind: FeedbackKind; title: string; message: string } | null>(null);

  private readonly initialView = loadSavedView<ProductsView>(VIEW_KEY, DEFAULT_VIEW);
  readonly query = signal(this.initialView.query);
  readonly brandFilter = signal(this.initialView.brandFilter);
  readonly categoryFilter = signal(this.initialView.categoryFilter);
  readonly pageSize = 20;
  readonly currentPage = signal(this.initialView.page);
  readonly drawerOpen = signal(false);
  readonly editing = signal<ProductDto | null>(null);

  readonly hasActiveFilters = computed(() =>
    !!this.query().trim() || this.brandFilter() !== 'all' || this.categoryFilter() !== 'all'
  );

  constructor() {
    effect(() => {
      persistSavedView(VIEW_KEY, {
        query: this.query(),
        brandFilter: this.brandFilter(),
        categoryFilter: this.categoryFilter(),
        page: this.currentPage(),
      });
    });
  }

  readonly form = new FormGroup({
    product_name: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    brand_id: new FormControl<number | null>(null, { validators: [Validators.required] }),
    category_id: new FormControl<number | null>(null, { validators: [Validators.required] }),
    model_year: new FormControl(new Date().getFullYear(), {
      nonNullable: true,
      validators: [Validators.required, Validators.min(1900)],
    }),
    list_price: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
  });

  readonly filtered = computed(() => {
    const q = this.query().trim().toLowerCase();
    const brand = this.brandFilter();
    const category = this.categoryFilter();
    return this.products().filter((item) => {
      const matchesQuery = item.product_name.toLowerCase().includes(q);
      const matchesBrand = brand === 'all' || String(item.brand_id) === brand;
      const matchesCategory = category === 'all' || String(item.category_id) === category;
      return matchesQuery && matchesBrand && matchesCategory;
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
    if (this.route.snapshot.queryParamMap.get('create')) {
      // Defer until brands/categories load so dropdowns have defaults.
      const sub = setInterval(() => {
        if (!this.loading()) {
          this.openCreate();
          this.router.navigate([], { queryParams: { create: null }, queryParamsHandling: 'merge', replaceUrl: true });
          clearInterval(sub);
        }
      }, 80);
    }
  }

  clearFilters(): void {
    this.query.set('');
    this.brandFilter.set('all');
    this.categoryFilter.set('all');
    this.resetPagination();
  }

  exportCsv(): void {
    const rows = this.filtered();
    if (!rows.length) {
      this.toasts.info('Nothing to export — list is empty.');
      return;
    }
    exportRowsToCsv('products', rows, [
      { header: 'ID', value: (r) => r.product_id },
      { header: 'Product name', value: (r) => r.product_name },
      { header: 'Brand', value: (r) => this.brandName(r.brand_id) },
      { header: 'Category', value: (r) => this.categoryName(r.category_id) },
      { header: 'Model year', value: (r) => r.model_year },
      { header: 'List price', value: (r) => r.list_price },
      { header: 'Active', value: (r) => (r.is_active ? 'yes' : 'no') },
    ]);
    this.toasts.success(`Exported ${rows.length} products.`);
  }

  requestDrawerClose(): void {
    if (this.form.dirty && !this.saving()) {
      this.confirmDiscard.set(true);
    } else {
      this.closeDrawer();
    }
  }

  confirmDiscardClose(): void {
    this.confirmDiscard.set(false);
    this.closeDrawer();
  }

  cancelDiscard(): void {
    this.confirmDiscard.set(false);
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    forkJoin({
      products: this.http.get<ProductDto[]>(`${this.base}/products/?limit=500`),
      brands: this.http.get<BrandDto[]>(`${this.base}/brands/?limit=500`),
      categories: this.http.get<CategoryDto[]>(`${this.base}/categories/?limit=500`),
    }).subscribe({
      next: ({ products, brands, categories }) => {
        this.products.set(this.sortById(products));
        this.brands.set(brands);
        this.categories.set(categories);
        this.ensurePageInRange();
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(this.message(err, 'Failed to load products.'));
        this.loading.set(false);
      },
    });
  }

  setQuery(value: string): void {
    this.query.set(value);
    this.resetPagination();
  }

  setBrandFilter(value: string): void {
    this.brandFilter.set(value);
    this.resetPagination();
  }

  setCategoryFilter(value: string): void {
    this.categoryFilter.set(value);
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
    this.form.reset({
      product_name: '',
      brand_id: this.brands()[0]?.brand_id ?? null,
      category_id: this.categories()[0]?.category_id ?? null,
      model_year: new Date().getFullYear(),
      list_price: '',
    });
    this.drawerOpen.set(true);
  }

  openEdit(item: ProductDto): void {
    this.editing.set(item);
    this.actionError.set(null);
    this.form.reset({
      product_name: item.product_name,
      brand_id: item.brand_id,
      category_id: item.category_id,
      model_year: item.model_year,
      list_price: String(item.list_price),
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
    const payload: CreateProductCommand = {
      product_name: raw.product_name,
      brand_id: raw.brand_id!,
      category_id: raw.category_id!,
      model_year: raw.model_year,
      list_price: raw.list_price,
    };
    const editing = this.editing();
    const request = editing
      ? this.http.put<ProductDto>(`${this.base}/products/${editing.product_id}`, payload as UpdateProductCommand)
      : this.http.post<ProductDto>(`${this.base}/products/`, payload);

    this.saving.set(true);
    this.actionError.set(null);
    request.subscribe({
      next: (saved) => {
        this.saving.set(false);
        this.closeDrawer();
        this.upsertProduct(saved);
        this.toasts.success(`${editing ? 'Updated' : 'Created'}: ${saved.product_name}`);
      },
      error: (err) => {
        this.actionError.set(this.message(err, 'Failed to save product.'));
        this.saving.set(false);
      },
    });
  }

  toggleActive(item: ProductDto): void {
    const action = item.is_active ? 'deactivate' : 'activate';
    const nextActive = !item.is_active;
    this.http.post<ProductDto>(`${this.base}/products/${item.product_id}/${action}`, {}).subscribe({
      next: (updated) => {
        const product = { ...item, ...updated, is_active: nextActive };
        this.upsertProduct(product);
        this.showFeedback(
          nextActive ? 'success' : 'inactive',
          nextActive ? 'Product activated' : 'Product deactivated',
          `${product.product_name} is now ${nextActive ? 'active' : 'inactive'}.`
        );
      },
      error: (err) => this.showFeedback('danger', 'Product update failed', this.message(err, `Failed to ${action} product.`)),
    });
  }

  closeFeedback(): void {
    this.feedback.set(null);
  }

  brandName(id: number): string {
    return this.brands().find((brand) => brand.brand_id === id)?.brand_name ?? `Brand #${id}`;
  }

  categoryName(id: number): string {
    return this.categories().find((category) => category.category_id === id)?.category_name ?? `Category #${id}`;
  }

  formatPrice(value: string | number): string {
    return formatPrice(value);
  }

  private message(err: unknown, fallback: string): string {
    const appError = normalizeError(err);
    const raw = JSON.stringify(appError.raw ?? '').toLowerCase();
    if (raw.includes('foreignkey') || raw.includes('foreign key') || raw.includes('still referenced')) {
      return 'This product is still referenced by stock or sales records. Keep it deactivated instead of deleting it.';
    }
    return friendlyMessage(appError.code, appError.message || fallback);
  }

  private upsertProduct(product: ProductDto): void {
    this.products.update((products) => {
      const exists = products.some((item) => item.product_id === product.product_id);
      const next = exists
        ? products.map((item) => item.product_id === product.product_id ? product : item)
        : [...products, product];
      return this.sortById(next);
    });
    this.ensurePageInRange();
  }

  private sortById(products: ProductDto[]): ProductDto[] {
    return [...products].sort((a, b) => a.product_id - b.product_id);
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
