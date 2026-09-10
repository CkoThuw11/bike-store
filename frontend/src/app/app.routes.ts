// ============================================================
// FILE: src/app/app.routes.ts
// ============================================================
import { Routes } from '@angular/router';
import { adminGuard, authGuard, guestGuard } from './core/auth/guards';

export const routes: Routes = [
  // Public routes
  {
    path: 'login',
    canActivate: [guestGuard],
    loadComponent: () =>
      import('./features/auth/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'register',
    canActivate: [guestGuard],
    loadComponent: () =>
      import('./features/auth/register/register.component').then((m) => m.RegisterComponent),
  },

  // Protected routes — inside app shell
  {
    path: '',
    canActivate: [authGuard, adminGuard],
    loadComponent: () =>
      import('./core/layout/app-shell/app-shell.component').then((m) => m.AppShellComponent),
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },

      {
        path: 'dashboard',
        loadComponent: () =>
          import('./features/dashboard/dashboard.component').then((m) => m.DashboardComponent),
      },

      // Catalog
      {
        path: 'brands',
        loadComponent: () =>
          import('./features/brands/brands.component').then((m) => m.BrandsComponent),
      },
      {
        path: 'categories',
        loadComponent: () =>
          import('./features/categories/categories.component').then((m) => m.CategoriesComponent),
      },
      {
        path: 'products',
        loadComponent: () =>
          import('./features/products/products.component').then((m) => m.ProductsComponent),
      },

      // Operations
      {
        path: 'stores',
        loadComponent: () =>
          import('./features/stores/stores.component').then((m) => m.StoresComponent),
      },
      {
        path: 'staffs',
        loadComponent: () =>
          import('./features/staffs/staffs.component').then((m) => m.StaffsComponent),
      },
      {
        path: 'stocks',
        loadComponent: () =>
          import('./features/stocks/stocks.component').then((m) => m.StocksComponent),
      },

      // Sales
      {
        path: 'customers',
        loadComponent: () =>
          import('./features/customers/customers.component').then((m) => m.CustomersComponent),
      },
      {
        path: 'orders',
        loadComponent: () =>
          import('./features/orders/orders.component').then((m) => m.OrdersComponent),
      },
      {
        path: 'orders/new',
        loadComponent: () =>
          import('./features/orders/create-order/create-order.component').then(
            (m) => m.CreateOrderComponent
          ),
      },

      // Settings
      {
        path: 'settings',
        loadComponent: () =>
          import('./features/settings/settings.component').then((m) => m.SettingsComponent),
      },
    ],
  },

  // Fallback
  { path: '**', redirectTo: 'dashboard' },
];
