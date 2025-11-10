/**
 * AI module controlling opponent paddle.
 * @module ai
 */
import { clamp } from './utils.js';

export default class AI {
  /**
   * @param {Object} opts
   * @param {string} opts.difficulty
   * @param {number} opts.speedMultiplier
   */
  constructor(opts) {
    this.setDifficulty(opts.difficulty);
  }

  /**
   * Set difficulty level.
   * @param {string} level
   */
  setDifficulty(level) {
    this.level = level;
    switch (level) {
      case 'easy':
        this.speed = 0.5;
        this.delay = 300;
        break;
      case 'hard':
        this.speed = 1.5;
        this.delay = 100;
        break;
      default:
        this.speed = 1;
        this.delay = 200;
    }
  }

  /**
   * Update AI paddle position based on ball.
   * @param {Object} state
   */
  update(state) {
    const paddle = state.players[1].paddle;
    const targetY = state.ball.y;
    const diff = targetY - paddle.y;
    const move = clamp(diff * this.speed, -20, 20);
    paddle.moveTo(paddle.y + move);
  }
}
