/**
 * @file src/utils.js
 * @module Utils
 * @description
 * A collection of pure helper functions used throughout the Ping Pong game.
 * All functions are pure, side‑effect free and fully typed via JSDoc.
 *
 * Public API:
 *  - randomAngle([min = -Math.PI/4], [max = Math.PI/4]) → number
 *  - clamp(value, min, max) → number
 *  - debounce(fn, delay) → Function
 *
 * These helpers are intentionally minimal to keep the bundle size small and
 * to avoid external dependencies.
 */

'use strict';

/**
 * Returns a random angle in radians between `min` and `max`.
 * Useful for setting the ball's initial velocity direction.
 *
 * @param {number} [min=-Math.PI / 4] - Minimum angle in radians.
 * @param {number} [max=Math.PI / 4] - Maximum angle in radians.
 * @returns {number} A random angle in radians.
 * @throws {TypeError} If `min` or `max` is not a number.
 */
export function randomAngle(min = -Math.PI / 4, max = Math.PI / 4) {
  if (typeof min !== 'number' || typeof max !== 'number') {
    throw new TypeError('randomAngle: min and max must be numbers');
  }
  if (min > max) {
    [min, max] = [max, min]; // swap to maintain order
  }
  return Math.random() * (max - min) + min;
}

/**
 * Clamps a numeric value between a minimum and maximum boundary.
 *
 * @param {number} value - The value to clamp.
 * @param {number} min   - Minimum allowed value.
 * @param {number} max   - Maximum allowed value.
 * @returns {number} The clamped value.
 * @throws {TypeError} If any argument is not a number.
 */
export function clamp(value, min, max) {
  if (typeof value !== 'number' || typeof min !== 'number' || typeof max !== 'number') {
    throw new TypeError('clamp: all arguments must be numbers');
  }
  if (min > max) {
    [min, max] = [max, min]; // swap to maintain order
  }
  return Math.min(Math.max(value, min), max);
}

/**
 * Creates a debounced version of the provided function.
 * The debounced function delays invoking `fn` until after `delay` milliseconds
 * have elapsed since the last call. Useful for throttling high-frequency
 * events like resize or mousemove.
 *
 * @param {Function} fn    - The function to debounce.
 * @param {number}   delay - Delay in milliseconds.
 * @returns {Function} A debounced function.
 * @throws {TypeError} If `fn` is not a function or `delay` is not a number.
 */
export function debounce(fn, delay) {
  if (typeof fn !== 'function') {
    throw new TypeError('debounce: first argument must be a function');
  }
  if (typeof delay !== 'number' || delay < 0) {
    throw new TypeError('debounce: second argument must be a non-negative number');
  }

  let timeoutId = null;

  return function debounced(...args) {
    const context = this;
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      fn.apply(context, args);
    }, delay);
  };
}

/**
 * Export all functions as a single object for convenience.
 */
export default { randomAngle, clamp, debounce };