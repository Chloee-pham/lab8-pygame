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
