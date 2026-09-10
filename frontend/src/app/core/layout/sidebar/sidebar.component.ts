// src/app/core/layout/sidebar/sidebar.component.ts
import { Component, inject, computed } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../auth/auth.service';
import { getInitials } from '../../../shared/utils/format.utils';

interface NavItem {
  label: string;
  route: string;
  icon: string;
}

interface NavGroup {
  title: string;
  items: NavItem[];
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss',
})
export class SidebarComponent {
  private readonly auth = inject(AuthService);

  readonly user = this.auth.user;

  readonly initials = computed(() => {
    const u = this.user();
    return u ? getInitials(u.fullname) : '?';
  });

  readonly navGroups: NavGroup[] = [
    {
      title: 'Overview',
      items: [
        { label: 'Dashboard', route: '/dashboard', icon: 'grid' },
      ],
    },
    {
      title: 'Catalog',
      items: [
        { label: 'Products', route: '/products', icon: 'bike' },
        { label: 'Brands', route: '/brands', icon: 'bookmark' },
        { label: 'Categories', route: '/categories', icon: 'tag' },
      ],
    },
    {
      title: 'Operations',
      items: [
        { label: 'Stores', route: '/stores', icon: 'building-store' },
        { label: 'Staff', route: '/staffs', icon: 'users' },
        { label: 'Stock', route: '/stocks', icon: 'package' },
      ],
    },
    {
      title: 'Sales',
      items: [
        { label: 'Customers', route: '/customers', icon: 'user-heart' },
        { label: 'Orders', route: '/orders', icon: 'shopping-cart' },
      ],
    },
    {
      title: 'Settings',
      items: [
        { label: 'Profile', route: '/settings', icon: 'user' },
      ],
    },
  ];

  logout(): void {
    this.auth.logout();
  }
}
