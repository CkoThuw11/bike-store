import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { StockDto } from '../types';

const LOW_STOCK_THRESHOLD = 5;

@Injectable({ providedIn: 'root' })
export class AlertsService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiUrl;

  readonly lowStock = signal<StockDto[]>([]);
  readonly loaded = signal(false);

  refresh(): void {
    this.http.get<StockDto[]>(`${this.base}/stocks/?limit=500`).subscribe({
      next: (rows) => {
        this.lowStock.set(rows.filter((r) => r.quantity < LOW_STOCK_THRESHOLD));
        this.loaded.set(true);
      },
      error: () => this.loaded.set(true),
    });
  }
}
