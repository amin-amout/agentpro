/**
 * Handles drawing of all game elements.
 * @module canvasRenderer
 */
import { clamp } from './utils.js';

export default class CanvasRenderer {
  /**
   * @param {HTMLCanvasElement} canvas
   */
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.resize();
  }

  resize() {
    const parent = this.canvas.parentElement;
    const size = Math.min(parent.clientWidth, parent.clientHeight * (4 / 3));
    this.canvas.width = size;
    this.canvas.height = size * 3 / 4;
  }

  /**
   * Render current state.
   * @param {Object} state
   */
  render(state) {
    const ctx = this.ctx;
    const { canvas } = this;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Net
    ctx.fillStyle = '#fff';
    ctx.fillRect(canvas.width / 2 - 1, 0, 2, canvas.height);

    // Paddles
    state.players.forEach((p) => {
      const b = p.paddle.getBounds();
      ctx.fillStyle = p.color;
      ctx.fillRect(b.x, b.y, b.width, b.height);
    });

    // Ball
    ctx.beginPath();
    ctx.arc(state.ball.x, state.ball.y, state.ball.radius, 0, Math.PI * 2);
    ctx.fillStyle = '#fff';
    ctx.fill();

    // Scores
    ctx.fillStyle = '#fff';
    ctx.font = '24px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(
      `${state.scores.player1} : ${state.scores.player2}`,
      canvas.width / 2,
      30
    );
  }
}
