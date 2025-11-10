/**
 * Ball class encapsulating position, velocity, and movement logic.
 * @module ball
 */
import { randomAngle, clamp } from './utils.js';

export default class Ball {
  /**
   * @param {Object} opts
   * @param {number} opts.radius
   * @param {number} opts.speed
   * @param {number} opts.canvasWidth
   * @param {number} opts.canvasHeight
   */
  constructor(opts) {
    this.radius = opts.radius;
    this.speed = opts.speed;
    this.canvasWidth = opts.canvasWidth;
    this.canvasHeight = opts.canvasHeight;
    this.reset();
  }

  /**
   * Reset ball to center with a random direction.
   */
  reset() {
    this.x = this.canvasWidth / 2;
    this.y = this.canvasHeight / 2;
    const angle = randomAngle();
    const dir = Math.random() < 0.5 ? -1 : 1;
    this.velocityX = dir * this.speed * Math.cos(angle);
    this.velocityY = this.speed * Math.sin(angle);
  }

  /**
   * Update ball position based on velocity and delta time.
   * @param {number} deltaTime
   */
  update(deltaTime) {
    this.x += this.velocityX * deltaTime;
    this.y += this.velocityY * deltaTime;

    // Top/bottom wall collision
    if (this.y - this.radius <= 0) {
      this.y = this.radius;
      this.velocityY = -this.velocityY;
    } else if (this.y + this.radius >= this.canvasHeight) {
      this.y = this.canvasHeight - this.radius;
      this.velocityY = -this.velocityY;
    }
  }
}
