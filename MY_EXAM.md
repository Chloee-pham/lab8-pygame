Exercise 3:
Removed bounce logic. Added wrap-around: when a square exits one edge, it reappears on the opposite side. Velocity is unchanged.
Exercise 4: 
Used pygame.Rect and colliderect() to check if two squares overlap.
Since squares are rectangles, no custom math needed.
Exercise 5: 
Used check_collision() to detect overlapping squares each frame.
When two squares collide, the larger one eats the smaller one.
The eaten square calls rebirth_square(), which respawns it with original size.
Used itertools.combinations() to check all pairs without duplicates.
Exercise 6:
Predator grows by 20% of prey size after eating (capped at MAX_SQUARE_SIZE).
Since larger squares should move slower, velocity is clamped after each growth using the same speed_scale formula already used in update_squares().
This keeps the physics consistent — bigger squares naturally become slower.
Exercise 7:
Each square stores its last 30 center positions in a deque (maxlen=30).
Trail is drawn using pygame.draw.lines() each frame.
Visual artifact: when a square respawns, the old trail positions remain,
causing a line to be drawn from the old location to the new one.
Fix: call square.trail.clear() inside rebirth_square() to reset the trail on respawn.
Exercise 8:
To validate speed, I create a square with known position and velocity,
simulate one frame with a fixed dt=1.0s, and check the resulting position.
Expected: x = x0 + vx * dt. Used assert to verify within floating point tolerance.
TEST_MODE_ON flag controls whether the test runs at startup.
Limitation: this only tests basic linear movement, not acceleration or wall wrapping.
Exercies 9:
Instead of growing instantly after eating, the predator accumulates pending_growth.
Every 500ms (GROWTH_INTERVAL_MS), the square grows by GROWTH_SPEED (1 pixel) until
pending_growth reaches 0. Velocity is clamped after each growth tick to keep
speed consistent with the new size.

I DONT HAVE ENOUGH TIME T-T