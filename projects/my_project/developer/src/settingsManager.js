/**
 * Settings manager for game mode and difficulty.
 * @module settingsManager
 */
import { eventBus } from './eventBus.js';

export default class SettingsManager {
  constructor() {
    this.settings = {
      mode: 'single', // 'single' or 'two'
      difficulty: 'medium',
      bestOf: 5,
    };
  }

  setMode(mode) {
    this.settings.mode = mode;
    eventBus.emit('settingsChanged', this.getSettings());
  }

  setDifficulty(level) {
    this.settings.difficulty = level;
    eventBus.emit('settingsChanged', this.getSettings());
  }

  getSettings() {
    return { ...this.settings };
  }
}
