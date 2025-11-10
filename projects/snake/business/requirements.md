# Project Requirements

## Project Overview

**Name**: Web Snake Game

**Description**: A lightweight, browser‑only Snake game implemented with plain HTML, CSS, and JavaScript. The game runs in a single page, requires no external libraries or frameworks, and supports basic gameplay: moving a snake, eating food, growing, and detecting collisions.



## User Stories

### Start the game

**ID**: US01

**Description**: As a player, I want to start a new game session so that I can play immediately.

**Acceptance Criteria**:

- A Start button is visible on the landing screen.

- Pressing the Start button clears any previous state and shows the game canvas.

- The first snake segment is positioned at the center of the canvas.



### Control the snake

**ID**: US02

**Description**: As a player, I want to move the snake using arrow keys (or swipe on mobile) so that I can navigate the play area.

**Acceptance Criteria**:

- Arrow keys change the snake’s direction instantly.

- Swipe gestures on touch devices produce the same directional changes.

- The snake cannot reverse direction directly (e.g., moving right → left immediately).



### Eat food and grow

**ID**: US03

**Description**: As a player, I want the snake to grow when it eats food and my score to increase so that I can track my progress.

**Acceptance Criteria**:

- Food appears at random positions not occupied by the snake.

- When the snake’s head reaches food, the snake grows by one segment and a new food item spawns.

- The score increments by 1 for each food eaten and is displayed on screen.



### Detect collisions and end the game

**ID**: US04

**Description**: As a player, I want the game to end when the snake collides with walls or itself so that I know the session is over.

**Acceptance Criteria**:

- Collision with the canvas boundary triggers a Game Over state.

- Collision with any part of the snake’s body triggers a Game Over state.

- A Game Over message is displayed with the final score.



### Restart after game over

**ID**: US05

**Description**: As a player, I want to restart the game after a Game Over so that I can try again.

**Acceptance Criteria**:

- A Restart button appears in the Game Over screen.

- Pressing Restart resets the snake, score, and food to initial state.



### Responsive layout

**ID**: US06

**Description**: As a player on mobile devices, I want the game to adapt to screen size so that I can play comfortably.

**Acceptance Criteria**:

- Canvas scales to fit the viewport while maintaining a square aspect ratio.

- Controls (arrow keys or swipe) work on touch devices.



## Functional Requirements

- **FR01**: Render a square game area (canvas) of configurable size (default 400x400px).

- **FR02**: Implement a game loop using `requestAnimationFrame` that updates the snake’s position at a constant speed (e.g., 10 frames per second).

- **FR03**: Generate food at random grid positions ensuring it does not overlap the snake body.

- **FR04**: Handle keyboard input (Arrow keys) and touch input (swipe) to change snake direction.

- **FR05**: Detect collision with canvas boundaries and snake body segments.

- **FR06**: Maintain a score counter that increments on food consumption.

- **FR07**: Display current score in a UI element.

- **FR08**: Show Game Over overlay with final score and Restart button.

- **FR09**: Reset all game state when Restart is pressed.

- **FR10**: Ensure the entire codebase is written in plain HTML, CSS, and vanilla JavaScript (no external libraries).



## Non-Functional Requirements

- **NFR01**: Performance: The game must run smoothly at 60 FPS on modern browsers.

- **NFR02**: Compatibility: Must support latest versions of Chrome, Firefox, Safari, Edge, and mobile browsers (iOS Safari, Android Chrome).

- **NFR03**: Accessibility: Keyboard controls must be operable with standard arrow keys and screen reader focus must be on the canvas during gameplay.

- **NFR04**: Maintainability: All code should be modular, with clear separation between game logic, rendering, and input handling.

- **NFR05**: Security: The code must not expose any external network requests or use unsafe eval patterns.



## Business Rules

- **BR01**: 

- **BR02**: 

- **BR03**: 

- **BR04**: 

- **BR05**: 



## Success Criteria

- **SC01**: 

- **SC02**: 

- **SC03**: 

- **SC04**: 

- **SC05**: 
