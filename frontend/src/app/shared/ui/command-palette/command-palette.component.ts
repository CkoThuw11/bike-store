import {
  ChangeDetectionStrategy,
  Component,
  HostListener,
  computed,
  effect,
  inject,
  signal,
} from '@angular/core';
import { Router } from '@angular/router';
import { CommandPaletteService } from './command-palette.service';

interface PaletteCommand {
  id: string;
  label: string;
  hint: string;
  section: 'Navigate' | 'Create';
  action: () => void;
  keywords?: string;
}

@Component({
  selector: 'app-command-palette',
  standalone: true,
  templateUrl: './command-palette.component.html',
  styleUrl: './command-palette.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommandPaletteComponent {
  private readonly svc = inject(CommandPaletteService);
  private readonly router = inject(Router);

  readonly open = this.svc.open;
  readonly query = signal('');
  readonly activeIndex = signal(0);

  private readonly commands: PaletteCommand[] = [
    { id: 'nav-dashboard', label: 'Go to Dashboard', hint: 'Overview', section: 'Navigate',
      action: () => this.go('/dashboard') },
    { id: 'nav-products', label: 'Go to Products', hint: 'Catalog', section: 'Navigate',
      action: () => this.go('/products'), keywords: 'bikes catalog' },
    { id: 'nav-brands', label: 'Go to Brands', hint: 'Catalog', section: 'Navigate',
      action: () => this.go('/brands') },
    { id: 'nav-categories', label: 'Go to Categories', hint: 'Catalog', section: 'Navigate',
      action: () => this.go('/categories') },
    { id: 'nav-stores', label: 'Go to Stores', hint: 'Operations', section: 'Navigate',
      action: () => this.go('/stores') },
    { id: 'nav-staffs', label: 'Go to Staff', hint: 'Operations', section: 'Navigate',
      action: () => this.go('/staffs'), keywords: 'employees' },
    { id: 'nav-stocks', label: 'Go to Stock', hint: 'Operations', section: 'Navigate',
      action: () => this.go('/stocks'), keywords: 'inventory' },
    { id: 'nav-customers', label: 'Go to Customers', hint: 'Sales', section: 'Navigate',
      action: () => this.go('/customers') },
    { id: 'nav-orders', label: 'Go to Orders', hint: 'Sales', section: 'Navigate',
      action: () => this.go('/orders') },
    { id: 'nav-settings', label: 'Go to Settings', hint: 'Profile', section: 'Navigate',
      action: () => this.go('/settings') },

    { id: 'new-order', label: 'New Order', hint: '3-step checkout flow', section: 'Create',
      action: () => this.go('/orders/new') },
    { id: 'new-product', label: 'New Product', hint: 'Open Products + create drawer', section: 'Create',
      action: () => this.go('/products', { create: 1 }) },
    { id: 'new-customer', label: 'New Customer', hint: 'Open Customers + create drawer', section: 'Create',
      action: () => this.go('/customers', { create: 1 }) },
    { id: 'new-brand', label: 'New Brand', hint: 'Open Brands + create drawer', section: 'Create',
      action: () => this.go('/brands', { create: 1 }) },
  ];

  readonly filtered = computed(() => {
    const q = this.query().trim().toLowerCase();
    if (!q) return this.commands;
    return this.commands.filter((c) => {
      const hay = `${c.label} ${c.hint} ${c.keywords ?? ''}`.toLowerCase();
      return hay.includes(q);
    });
  });

  readonly grouped = computed(() => {
    const list = this.filtered();
    const sections = new Map<string, PaletteCommand[]>();
    for (const cmd of list) {
      const arr = sections.get(cmd.section) ?? [];
      arr.push(cmd);
      sections.set(cmd.section, arr);
    }
    return Array.from(sections.entries()).map(([section, items]) => ({ section, items }));
  });

  constructor() {
    effect(() => {
      // Reset state whenever palette opens
      if (this.open()) {
        this.query.set('');
        this.activeIndex.set(0);
      }
    });
  }

  @HostListener('document:keydown', ['$event'])
  handleKey(event: KeyboardEvent): void {
    const isMeta = event.metaKey || event.ctrlKey;
    if (isMeta && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      this.svc.toggle();
      return;
    }
    if (!this.open()) return;

    if (event.key === 'Escape') {
      event.preventDefault();
      this.svc.hide();
    } else if (event.key === 'ArrowDown') {
      event.preventDefault();
      const max = this.filtered().length - 1;
      this.activeIndex.update((i) => Math.min(max, i + 1));
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      this.activeIndex.update((i) => Math.max(0, i - 1));
    } else if (event.key === 'Enter') {
      event.preventDefault();
      const cmd = this.filtered()[this.activeIndex()];
      if (cmd) cmd.action();
    }
  }

  setQuery(value: string): void {
    this.query.set(value);
    this.activeIndex.set(0);
  }

  selectByIndex(index: number): void {
    const cmd = this.filtered()[index];
    if (cmd) cmd.action();
  }

  globalIndex(section: string, localIndex: number): number {
    let offset = 0;
    for (const group of this.grouped()) {
      if (group.section === section) return offset + localIndex;
      offset += group.items.length;
    }
    return offset + localIndex;
  }

  close(): void {
    this.svc.hide();
  }

  private go(path: string, queryParams?: Record<string, unknown>): void {
    this.svc.hide();
    this.router.navigate([path], queryParams ? { queryParams } : undefined);
  }
}
