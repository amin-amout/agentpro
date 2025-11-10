/**
 * Utility functions used across the application.
 * @module utils
 */

/**
 * Clamp a value between min and max.
 * @param {number} value
 * @param {number} min
 * @param {number} max
 * @returns {number}
 */
export const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

/**
 * Generate a random angle between -45 and 45 degrees in radians.
 * @returns {number}
 */
export const randomAngle = () => {
  const deg = Math.random() * 90 - 45;
  return (deg * Math.PI) / 180;
};

/**
 * Debounce a function.
 * @param {Function} fn
 * @param {number} delay
 * @returns {Function}
 */
export const debounce = (fn, delay) => {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(null, args), delay);
  };
};
