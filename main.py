from __future__ import annotations

from dataclasses import dataclass, field
import math
import random
from typing import List
from collections import deque

import pygame
import itertools



TEST_MODE_ON: bool = True
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MIN_SQUARE_SIZE = 15
MAX_SQUARE_SIZE = 60
BASE_SQUARE_SIZE = 30
SQUARE_COUNT = 24
BACKGROUND_COLOR = (20, 20, 20)
FPS = 60
TRAILS_LENGTH = 30
IDLE_WAIT_MS = 1
JITTER_ACCELERATION = 220.0
BASE_MAX_JITTER_SPEED = 180.0
BOUNCE_DAMPING = 0.82
GROWTH_SPEED = 1        # pixels per growth tick
GROWTH_INTERVAL_MS = 500  # ms between growth ticks
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
    trail: deque = field(default_factory=lambda: deque(maxlen=TRAILS_LENGTH))
    pending_growth: int = field(default=0)
    growth_timer: float = field(default=0.0)



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


def _make_square(size: int | None = None) -> MovingSquare:
    """Create one square with random attributes."""
    if size is None:
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


def create_initial_squares() -> List[MovingSquare]:
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
    square.trail.clear()



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
                a.pending_growth += b.size // 5
            elif b.size > a.size:
                rebirth_square(a)
                b.pending_growth += a.size // 5



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
        square.trail.append((int(square.x + square.size / 2), int(square.y + square.size / 2)))

        # --- Animated growth ---
        if square.pending_growth > 0:
            square.growth_timer += dt_seconds
            if square.growth_timer >= GROWTH_INTERVAL_MS / 1000.0:
                square.growth_timer = 0.0
                square.size = min(square.size + GROWTH_SPEED, MAX_SQUARE_SIZE)
                square.pending_growth -= GROWTH_SPEED
                speed_scale = BASE_SQUARE_SIZE / square.size
                new_max = BASE_MAX_JITTER_SPEED * speed_scale
                square.vx = max(-new_max, min(new_max, square.vx))
                square.vy = max(-new_max, min(new_max, square.vy))
    



def draw_scene(screen: pygame.Surface, squares: List[MovingSquare]) -> None:
    """Render one frame.

    Each square fades slightly as it ages — alpha goes from 255 → 80
    over its lifespan, giving a visual cue that rebirth is approaching.
    """
    screen.fill(BACKGROUND_COLOR)

    for square in squares:
        if len(square.trail) >= 2:
            pygame.draw.lines(screen, square.color, False, list(square.trail), 1)

        # Compute fade: fully opaque when young, dimmer when old.
        ratio = min(square.age / square.lifespan, 1.0)
        alpha = int(255 - ratio * 175)   

        surf = pygame.Surface((square.size, square.size), pygame.SRCALPHA)
        r, g, b = square.color
        surf.fill((r, g, b, alpha))
        screen.blit(surf, (int(square.x), int(square.y)))

    pygame.display.flip()


def run_speed_test() -> None:
    square = MovingSquare(
        x=100.0, y=100.0,
        vx=50.0, vy=0.0,
        size=25,
        color=(255, 255, 255),
        lifespan=10.0,
        age=0.0,
    )
    dt = 1.0
    expected_x = square.x + square.vx * dt  # = 150.0

    square.x += square.vx * dt
    square.y += square.vy * dt

    assert abs(square.x - expected_x) < 0.001, f"Speed test failed: expected {expected_x}, got {square.x}"
    print("Speed test passed.")


def run() -> None:
    """Application entry point."""
    screen, clock = init_pygame()
    squares = create_initial_squares()
    if TEST_MODE_ON:
        run_speed_test()

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


