from __future__ import annotations

from dataclasses import dataclass, field
import math
import random
from typing import List

import pygame
import itertools



WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MIN_SQUARE_SIZE = 15
MAX_SQUARE_SIZE = 60
BASE_SQUARE_SIZE = 30
SQUARE_COUNT = 24
BACKGROUND_COLOR = (20, 20, 20)
FPS = 60
IDLE_WAIT_MS = 1
JITTER_ACCELERATION = 220.0
BASE_MAX_JITTER_SPEED = 180.0
BOUNCE_DAMPING = 0.82
MIN_LIFESPAN = 3.0   # seconds
MAX_LIFESPAN = 10.0  # seconds

# --- Predator / prey tuning ---
CHASE_WEIGHT = 0.55
MIN_SIZE_DELTA = 6
DETECTION_RADIUS = 220.0


@dataclass
class MovingSquare:
    """One square with position, velocity, and life span."""

    x: float
    y: float
    vx: float
    vy: float
    size: int
    color: tuple[int, int, int]
    lifespan: float        # total time to live, in seconds
    age: float = field(default=0.0)   # time lived so far, in seconds


def _random_velocity(size: int) -> tuple[float, float]:
    """Return a random (vx, vy) scaled by square size."""
    base_min_speed = -120
    base_max_speed = 120
    base_min_abs = 20
    speed_scale = BASE_SQUARE_SIZE / size
    lo = base_min_speed * speed_scale
    hi = base_max_speed * speed_scale
    min_abs = base_min_abs * speed_scale
    vx = random.uniform(lo, hi)
    vy = random.uniform(lo, hi)
    while abs(vx) < min_abs and abs(vy) < min_abs:
        vx = random.uniform(lo, hi)
        vy = random.uniform(lo, hi)
    return vx, vy


def _random_color() -> tuple[int, int, int]:
    return (
        random.randint(60, 255),
        random.randint(60, 255),
        random.randint(60, 255),
    )


def init_pygame() -> tuple[pygame.Surface, pygame.time.Clock]:
    """Create the window and clock."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Lab 8 - Moving Squares (Small Chases Big)")
    clock = pygame.time.Clock()
    return screen, clock


def _make_square() -> MovingSquare:
    """Create one square with random attributes."""
    size = random.randint(MIN_SQUARE_SIZE, MAX_SQUARE_SIZE)
    x = random.uniform(0, WINDOW_WIDTH - size)
    y = random.uniform(0, WINDOW_HEIGHT - size)
    vx, vy = _random_velocity(size)
    return MovingSquare(
        x=x,
        y=y,
        vx=vx,
        vy=vy,
        size=size,
        color=_random_color(),
        lifespan=random.uniform(MIN_LIFESPAN, MAX_LIFESPAN),
        age=0.0,
    )


def create_initial_squares(count: int) -> List[MovingSquare]:
    squares = []
    for _ in range(5):
        squares.append(_make_square(size=25))
    for _ in range(10):
        squares.append(_make_square(size=10))
    for _ in range(30):
        squares.append(_make_square(size=4))
    return squares



def rebirth_square(square: MovingSquare) -> None:
    size = square.size  
    square.x = random.uniform(0, WINDOW_WIDTH - size)
    square.y = random.uniform(0, WINDOW_HEIGHT - size)
    square.vx, square.vy = _random_velocity(size)
    square.color = _random_color()
    square.lifespan = random.uniform(MIN_LIFESPAN, MAX_LIFESPAN)
    square.age = 0.0


def handle_events() -> bool:
    """Process events. Return False when app should quit."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
    return True


def _center(square: MovingSquare) -> tuple[float, float]:
    return square.x + square.size / 2, square.y + square.size / 2


def check_collision(a: MovingSquare, b: MovingSquare) -> bool:
    rect_a = pygame.Rect(a.x, a.y, a.size, a.size)
    rect_b = pygame.Rect(b.x, b.y, b.size, b.size)
    return rect_a.colliderect(rect_b)


def handle_eating(squares: List[MovingSquare]) -> None:
    for a, b in itertools.combinations(squares, 2):
        if check_collision(a, b):
            if a.size > b.size:
                rebirth_square(b)
            elif b.size > a.size:
                rebirth_square(a)


def _find_nearest_larger_target(
    chaser: MovingSquare,
    squares: List[MovingSquare],
) -> MovingSquare | None:
    """Return the closest square that is meaningfully larger, within detection radius."""
    px, py = _center(chaser)
    best: MovingSquare | None = None
    best_dist = DETECTION_RADIUS

    for candidate in squares:
        if candidate is chaser:
            continue
        if candidate.size - chaser.size < MIN_SIZE_DELTA:
            continue
        cx, cy = _center(candidate)
        dist = math.hypot(cx - px, cy - py)
        if dist < best_dist:
            best_dist = dist
            best = candidate
    return best


def update_squares(squares: List[MovingSquare], dt_seconds: float) -> None:
    """Update all squares for one frame, including life span / rebirth."""
    for square in squares:
        # --- Life Span / Rebirth ---
        square.age += dt_seconds
        if square.age >= square.lifespan:
            rebirth_square(square)
            continue  # skip movement update for the reborn square this frame

        # --- Base jitter ---
        speed_scale = BASE_SQUARE_SIZE / square.size
        max_speed = BASE_MAX_JITTER_SPEED * speed_scale

        jitter_ax = random.uniform(-JITTER_ACCELERATION, JITTER_ACCELERATION)
        jitter_ay = random.uniform(-JITTER_ACCELERATION, JITTER_ACCELERATION)

        # --- Chase / flee directed acceleration ---
        directed_ax = 0.0
        directed_ay = 0.0

        target = _find_nearest_larger_target(square, squares)
        if target is not None:
            # Smaller square: steer toward a larger target.
            sx, sy = _center(square)
            tx, ty = _center(target)
            dx, dy = tx - sx, ty - sy
            dist = math.hypot(dx, dy) or 1.0
            # Scale force so it's stronger up close (inverse falloff, clamped).
            strength = JITTER_ACCELERATION * min(DETECTION_RADIUS / dist, 3.0)
            directed_ax = (dx / dist) * strength
            directed_ay = (dy / dist) * strength

        # Blend jitter and directed acceleration.
        ax = jitter_ax * (1.0 - CHASE_WEIGHT) + directed_ax * CHASE_WEIGHT
        ay = jitter_ay * (1.0 - CHASE_WEIGHT) + directed_ay * CHASE_WEIGHT

        square.vx += ax * dt_seconds
        square.vy += ay * dt_seconds

        square.vx = max(-max_speed, min(max_speed, square.vx))
        square.vy = max(-max_speed, min(max_speed, square.vy))

        square.x += square.vx * dt_seconds
        square.y += square.vy * dt_seconds

        # --- Wrap around walls ---
        if square.x + square.size < 0:
             square.x = WINDOW_WIDTH
        elif square.x > WINDOW_WIDTH:
             square.x = -square.size

        if square.y + square.size < 0:
             square.y = WINDOW_HEIGHT
        elif square.y > WINDOW_HEIGHT:
             square.y = -square.size



def draw_scene(screen: pygame.Surface, squares: List[MovingSquare]) -> None:
    """Render one frame.

    Each square fades slightly as it ages — alpha goes from 255 → 80
    over its lifespan, giving a visual cue that rebirth is approaching.
    """
    screen.fill(BACKGROUND_COLOR)

    for square in squares:
        # Compute fade: fully opaque when young, dimmer when old.
        ratio = min(square.age / square.lifespan, 1.0)
        alpha = int(255 - ratio * 175)   

        surf = pygame.Surface((square.size, square.size), pygame.SRCALPHA)
        r, g, b = square.color
        surf.fill((r, g, b, alpha))
        screen.blit(surf, (int(square.x), int(square.y)))

    pygame.display.flip()


def run() -> None:
    """Application entry point."""
    screen, clock = init_pygame()
    squares = create_initial_squares()

    running = True
    while running:
        dt_seconds = clock.tick(FPS) / 1000.0

        if not pygame.event.peek():
            pygame.time.wait(IDLE_WAIT_MS)

        running = handle_events()
        update_squares(squares, dt_seconds)
        handle_eating(squares)
        draw_scene(screen, squares)

    pygame.quit()


if __name__ == "__main__":
    run()


