// src/app/core/layout/top-header/top-header.component.ts
import { ChangeDetectionStrategy, Component, OnInit, computed, inject, signal } from '@angular/core';
import { NavigationEnd, Router, RouterLink } from '@angular/router';
import { filter, map } from 'rxjs';
import { toSignal } from '@angular/core/rxjs-interop';
import { AuthService } from '../../auth/auth.service';
import { getInitials } from '../../../shared/utils/format.utils';
import { CommandPaletteService } from '../../../shared/ui/command-palette/command-palette.service';
import { AlertsService } from '../../../shared/state/alerts.service';

interface RouteMeta {
  title: string;
  group?: string;
  groupRoute?: string;
}

const ROUTE_META: Record<string, RouteMeta> = {
  '/dashboard':  { title: 'Dashboard', group: 'Overview' },
  '/brands':     { title: 'Brands', group: 'Catalog', groupRoute: '/products' },
  '/categories': { title: 'Categories', group: 'Catalog', groupRoute: '/products' },
  '/products':   { title: 'Products', group: 'Catalog', groupRoute: '/products' },
  '/stores':     { title: 'Stores', group: 'Operations', groupRoute: '/stores' },
  '/staffs':     { title: 'Staff', group: 'Operations', groupRoute: '/stores' },
  '/stocks':     { title: 'Stock & Inventory', group: 'Operations', groupRoute: '/stores' },
  '/customers':  { title: 'Customers', group: 'Sales', groupRoute: '/orders' },
  '/orders':     { title: 'Orders', group: 'Sales', groupRoute: '/orders' },
  '/orders/new': { title: 'New Order', group: 'Sales', groupRoute: '/orders' },
  '/settings':   { title: 'Settings', group: 'Profile' },
};

@Component({
  selector: 'app-top-header',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './top-header.component.html',
  styleUrl: './top-header.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TopHeaderComponent implements OnInit {
  private readonly router = inject(Router);
  private readonly auth = inject(AuthService);
  private readonly palette = inject(CommandPaletteService);
  private readonly alerts = inject(AlertsService);

  readonly user = this.auth.user;
  readonly menuOpen = signal(false);
  readonly bellOpen = signal(false);
  readonly lowStock = this.alerts.lowStock;
  readonly lowStockCount = computed(() => this.lowStock().length);

  readonly initials = computed(() => {
    const u = this.user();
    return u ? getInitials(u.fullname) : '?';
  });

  readonly isMac = typeof navigator !== 'undefined' && /Mac|iPod|iPhone|iPad/.test(navigator.platform);
  readonly metaKeyLabel = this.isMac ? '⌘' : 'Ctrl';

  private readonly currentUrl = toSignal(
    this.router.events.pipe(
      filter((e): e is NavigationEnd => e instanceof NavigationEnd),
      map((e) => e.urlAfterRedirects)
    ),
    { initialValue: this.router.url }
  );

  readonly currentMeta = computed<RouteMeta>(() => {
    const clean = (this.currentUrl() ?? '').split('?')[0];
    return ROUTE_META[clean] ?? { title: 'VeloShop' };
  });

  readonly pageTitle = computed(() => this.currentMeta().title);

  readonly breadcrumbs = computed(() => {
    const meta = this.currentMeta();
    const crumbs: { label: string; route?: string }[] = [{ label: 'Home', route: '/dashboard' }];
    if (meta.group) crumbs.push({ label: meta.group, route: meta.groupRoute });
    crumbs.push({ label: meta.title });
    return crumbs;
  });

  ngOnInit(): void {
    this.alerts.refresh();
  }

  openPalette(): void {
    this.palette.show();
  }

  toggleMenu(): void {
    this.menuOpen.update((v) => !v);
    if (this.menuOpen()) this.bellOpen.set(false);
  }

  toggleBell(): void {
    this.bellOpen.update((v) => !v);
    if (this.bellOpen()) this.menuOpen.set(false);
  }

  closeMenus(): void {
    this.menuOpen.set(false);
    this.bellOpen.set(false);
  }

  logout(): void {
    this.closeMenus();
    this.auth.logout();
  }
}
