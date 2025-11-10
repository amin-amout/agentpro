/**
 * Input handling for mouse, touch, and keyboard.
 * @module inputHandler
 */
import { debounce } from './utils.js';

export default class InputHandler {
  constructor(canvas, state) {
    this.canvas = canvas;
    this.state = state;
    this.mouseY = null;
    this.touchY = null;
    this.boundHandleMove = this.handleMove.bind(this);
    this.boundHandleTouch = this.handleTouch.bind(this);
    this.boundHandleKey = this.handleKey.bind(this);
  }

  init() {
    this.canvas.addEventListener('mousemove', this.boundHandleMove);
    this.canvas.addEventListener('touchmove', this.boundHandleTouch, { passive: false });
    window.addEventListener('keydown', this.boundHandleKey);
  }

  destroy() {
    this.canvas.removeEventListener('mousemove', this.boundHandleMove);
    this.canvas.removeEventListener('touchmove', this.boundHandleTouch);
    window.removeEventListener('keydown', this.boundHandleKey);
  }

  handleMove(e) {
    const rect = this.canvas.getBoundingClientRect();
    this.mouseY = e.clientY - rect.top;
    this.updatePaddles();
  }

  handleTouch(e) {
    e.preventDefault();
    const rect = this.canvas.getBoundingClientRect();
    this.touchY = e.touches[0].clientY - rect.top;
    this.updatePaddles();
  }

  handleKey(e) {
    if (e.code === 'Space') eventBus.emit('pauseToggle');
    if (e.code === 'KeyR') eventBus.emit('resetGame');
  }

  updatePaddles() {
    const paddle = this.state.players[0].paddle;
    const y = this.mouseY ?? this.touchY;
    if (y != null) paddle.moveTo(y);
  }
}
