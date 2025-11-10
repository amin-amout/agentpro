/**
 * Simple publish/subscribe event bus.
 * @module eventBus
 */

class EventBus {
  constructor() {
    this.listeners = new Map();
  }

  /**
   * Register a listener for an event.
   * @param {string} event
   * @param {(payload: any) => void} handler
   */
  on(event, handler) {
    if (!this.listeners.has(event)) this.listeners.set(event, []);
    this.listeners.get(event).push(handler);
  }

  /**
   * Emit an event to all listeners.
   * @param {string} event
   * @param {any} payload
   */
  emit(event, payload) {
    const handlers = this.listeners.get(event);
    if (handlers) handlers.forEach((h) => h(payload));
  }
}

export const eventBus = new EventBus();
