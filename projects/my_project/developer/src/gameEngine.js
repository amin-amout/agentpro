/**
 * Main game engine orchestrating all modules.
 * @module gameEngine
 */
import Paddle from './paddle.js';
import Ball from './ball.js';
import PhysicsEngine from './physicsEngine.js';
import AI from './ai.js';
import InputHandler from './inputHandler.js';
import ScoreManager from './scoreManager.js';
import SettingsManager from './settingsManager.js';
import CanvasRenderer from './canvasRenderer.js';
import { eventBus } from './eventBus.js';
import { clamp } from './utils.js';

export default class GameEngine {
  constructor(canvas) {
    this.canvas = canvas;
    this.renderer = new CanvasRenderer(canvas);
    this.physics = new PhysicsEngine();
    this.ai = new AI({ difficulty: 'medium' });
    this.inputHandler = new InputHandler(canvas, this);
    this.scoreManager = new ScoreManager();
    this.settingsManager = new SettingsManager();
    this.lastTime = 0;
    this.running = false;

    // Bind events
    eventBus.on('pointScored', (payload) => this.handlePoint(payload));
    eventBus.on('pauseToggle', () => this.togglePause());
    eventBus.on('resetGame', () => this.reset());
    eventBus.on('settingsChanged', (s) => this.applySettings(s));

    this.init();
  }

  init() {
    this.inputHandler.init();
    this.applySettings(this.settingsManager.getSettings());
    this.reset();
  }

  applySettings(settings) {
    this.ai.setDifficulty(settings.difficulty);
    this.running = false;
  }

  start() {
    if (!this.running) {
      this.running = true;
      this.lastTime = performance.now();
      requestAnimationFrame(this.loop.bind(this));
    }
  }

  pause() {
    this.running = false;
  }

  togglePause() {
    this.running ? this.pause() : this.start();
  }

  reset() {
    const canvas = this.canvas;
    this.state = {
      canvasWidth: canvas.width,
      canvasHeight: canvas.height,
      players: [
        {
          id: 'player1',
          paddle: new Paddle({
            x: 20,
            y: canvas.height / 2,
            width: 10,
            height: 80,
            canvasHeight: canvas.height,
            color: '#FF5722',
          }),
          score: 0,
        },
        {
          id: 'player