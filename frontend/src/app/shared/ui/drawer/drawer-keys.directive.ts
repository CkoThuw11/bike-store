import { Directive, HostListener, input, output } from '@angular/core';

/**
 * Attach to a drawer/offcanvas root element. Adds:
 *   - Escape → emits closeRequested (caller decides whether to confirm)
 *   - Ctrl/Cmd+Enter → emits submitRequested
 *
 * Caller is responsible for the unsaved-changes check and focus management.
 */
@Directive({
  selector: '[appDrawerKeys]',
  standalone: true,
})
export class DrawerKeysDirective {
  readonly active = input<boolean>(true);

  readonly closeRequested = output<void>();
  readonly submitRequested = output<void>();

  @HostListener('document:keydown', ['$event'])
  handle(event: KeyboardEvent): void {
    if (!this.active()) return;
    if (event.key === 'Escape') {
      event.preventDefault();
      this.closeRequested.emit();
    } else if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
      event.preventDefault();
      this.submitRequested.emit();
    }
  }
}
