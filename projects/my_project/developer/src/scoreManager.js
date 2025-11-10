/**
 * Score manager handles current and high scores.
 * @module scoreManager
 */
import { eventBus } from './eventBus.js';

export default class ScoreManager {
  constructor() {
    this.scores = { player1: 0, player2: 0 };
    this.highScore = this.loadHighScore();
  }

  increment(playerId) {
    this.scores[playerId] += 1;
    eventBus.emit('scoreUpdated', this.getScores());
    if (this.scores[playerId] > this.highScore) {
      this.highScore = this.scores[playerId];
      this.saveHighScore();
    }
  }

  reset() {
    this.scores = { player1: 0, player2: 0 };
    eventBus.emit('scoreUpdated', this.getScores());
  }

  getScores() {
    return { ...this.scores };
  }

  loadHighScore() {
    const val = localStorage.getItem('pingpong_highscore');
    return val ? parseInt(val, 10) : 0;
  }

  saveHighScore() {
    localStorage.setItem('pingpong_highscore', this.highScore);
  }
}
