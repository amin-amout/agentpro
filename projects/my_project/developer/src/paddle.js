/**
 * Paddle class representing a player paddle.
 * @module paddle
 */
import { clamp } from './utils.js';

export default class Paddle {
  /**
   * @param {Object} opts
   * @param {number} opts.x
   * @param {number} opts.y
   * @param {number} opts.width
   * @param {number} opts.height
   * @param {number} opts.canvasHeight
   * @param {string} opts.color
   */
  constructor(opts) {
    this.x = opts.x;
    this.y = opts.y;
    this.width = opts.width;
    this.height = opts.height;
    this.canvasHeight = opts.canvasHeight;
    this.color = opts.color;
    this.targetY = opts.y;
  }

  /**
   * Move paddle to a new Y position (target for AI or input).
   * @param {number} y
   */
  moveTo(y) {
    this.targetY = y;
    this.clamp();
  }

  /**
   * Ensure paddle stays within canvas bounds.
   */
  clamp() {
    const half = this.height / 2;
    this.y = clamp(this.targetY, half, this.canvasHeight - half);
  }

  /**
   * Get bounding box for collision detection.
   * @returns {{x:number, y:number, width:number, height:number}}
   */
  getBounds() {
    return {
      x: this.x,
      y: this.y - this.height / 2,
      width: this.width,
      height: this.height,
    };
  }
}
