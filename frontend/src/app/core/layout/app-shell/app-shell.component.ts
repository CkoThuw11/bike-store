// src/app/core/layout/app-shell/app-shell.component.ts
import { Component, inject, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { TopHeaderComponent } from '../top-header/top-header.component';
import { CommandPaletteComponent } from '../../../shared/ui/command-palette/command-palette.component';
import { ToastRegionComponent } from '../../../shared/ui/toast/toast-region.component';
import { AlertsService } from '../../../shared/state/alerts.service';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [
    RouterOutlet,
    SidebarComponent,
    TopHeaderComponent,
    CommandPaletteComponent,
    ToastRegionComponent,
  ],
  templateUrl: './app-shell.component.html',
  styleUrl: './app-shell.component.scss',
})
export class AppShellComponent implements OnInit {
  private readonly alerts = inject(AlertsService);

  ngOnInit(): void {
    this.alerts.refresh();
  }
}
