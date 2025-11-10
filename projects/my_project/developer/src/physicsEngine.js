/**
 * Physics engine handling ball movement and collision.
 * @module physicsEngine
 */
import { clamp } from './utils.js';

export default class PhysicsEngine {
  /**
   * Update ball physics and handle collisions.
   * @param {Object} state
   * @param {number} deltaTime
   */
  updateBall(state, deltaTime) {
    state.ball.update(deltaTime);

    // Paddle collision
    [state.players[0], state.players[1]].forEach((player) => {
      const bounds = player.paddle.getBounds();
      if (
        state.ball.x - state.ball.radius <= bounds.x + bounds.width &&
        state.ball.x + state.ball.radius >= bounds.x &&
        state.ball.y >= bounds.y &&
        state.ball.y <= bounds.y + bounds.height
      ) {
        // Reflect ball
        const relativeY = (state.ball.y - bounds.y) / bounds.height;
        const bounceAngle = (relativeY - 0.5) * Math.PI / 3; // +/- 60deg
        const speed = Math.hypot(state.ball.velocityX, state.ball.velocityY);
        const dir = state.ball.x < state.canvasWidth / 2 ? 1 : -1;
        state.ball.velocityX = dir * speed * Math.cos(bounceAngle);
        state.ball.velocityY = speed * Math.sin(bounceAngle);
        // Visual feedback could be added here
      }
    });

    // Net collision (center line)
    const netX = state.canvasWidth / 2;
    if (
      Math.abs(state.ball.x - netX) <= state.ball.radius &&
      state.ball.y >= 0 &&
      state.ball.y <= state.canvasHeight
    ) {
      // Fault: point to opponent
      const winner = state.players.find((p) => p.id === 'player1').id;
      eventBus.emit('pointScored', { player: winner, score: 0 });
      state.ball.reset();
    }

    // Score detection
    if (state.ball.x < 0) {
      eventBus.emit('pointScored', { player: 'player2', score: 0 });
      state.ball.reset();
    } else if (state.ball.x > state.canvasWidth) {
      eventBus.emit('pointScored', { player: 'player1', score: 0 });
      state.ball.reset();
    }
  }
}
