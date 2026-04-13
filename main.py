"""Skeleton pygame app: moving squares with size-based speed.

This file intentionally contains stubs and TODO prompts.
Fill in each TODO step-by-step.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import List

import pygame


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


@dataclass
class MovingSquare:
	"""One square with position and velocity."""

	x: float
	y: float
	vx: float
	vy: float
	size: int
	color: tuple[int, int, int]


def init_pygame() -> tuple[pygame.Surface, pygame.time.Clock]:
	"""Create the window and clock."""
	pygame.init()
	screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
	pygame.display.set_caption("Lab 8 - Moving Squares (Skeleton)")
	clock = pygame.time.Clock()
	return screen, clock


def create_initial_squares(count: int) -> List[MovingSquare]:
	"""Return `count` squares with random start positions and velocities."""
	# TODO (Socratic): Move min/max speed values to global constants so tuning is easier.
	# TODO (Socratic): Try using random.randint instead of random.uniform and compare feel.
	squares: List[MovingSquare] = []
	base_min_speed = -120
	base_max_speed = 120
	base_min_abs_component = 20

	for _ in range(count):
		size = random.randint(MIN_SQUARE_SIZE, MAX_SQUARE_SIZE)
		x = random.uniform(0, WINDOW_WIDTH - size)
		y = random.uniform(0, WINDOW_HEIGHT - size)

		# Smaller squares move faster, larger squares move slower.
		speed_scale = BASE_SQUARE_SIZE / size
		min_speed = base_min_speed * speed_scale
		max_speed = base_max_speed * speed_scale
		min_abs_component = base_min_abs_component * speed_scale

		vx = random.uniform(min_speed, max_speed)
		vy = random.uniform(min_speed, max_speed)
		while abs(vx) < min_abs_component and abs(vy) < min_abs_component:
			vx = random.uniform(min_speed, max_speed)
			vy = random.uniform(min_speed, max_speed)

		color = (
			random.randint(60, 255),
			random.randint(60, 255),
			random.randint(60, 255),
		)

		squares.append(MovingSquare(x=x, y=y, vx=vx, vy=vy, size=size, color=color))
	return squares


def handle_events() -> bool:
	"""Process events. Return False when app should quit."""
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			return False
	return True


def update_squares(squares: List[MovingSquare], dt_seconds: float) -> None:
	"""Update all squares for one frame."""
	# Add small random acceleration each frame to create a "shaky" movement.
	for square in squares:
		speed_scale = BASE_SQUARE_SIZE / square.size
		max_speed = BASE_MAX_JITTER_SPEED * speed_scale

		square.vx += random.uniform(-JITTER_ACCELERATION, JITTER_ACCELERATION) * dt_seconds
		square.vy += random.uniform(-JITTER_ACCELERATION, JITTER_ACCELERATION) * dt_seconds

		square.vx = max(-max_speed, min(max_speed, square.vx))
		square.vy = max(-max_speed, min(max_speed, square.vy))

		square.x += square.vx * dt_seconds
		square.y += square.vy * dt_seconds

		if square.x < 0:
			square.x = 0
			square.vx = abs(square.vx) * BOUNCE_DAMPING
		elif square.x + square.size > WINDOW_WIDTH:
			square.x = WINDOW_WIDTH - square.size
			square.vx = -abs(square.vx) * BOUNCE_DAMPING

		if square.y < 0:
			square.y = 0
			square.vy = abs(square.vy) * BOUNCE_DAMPING
		elif square.y + square.size > WINDOW_HEIGHT:
			square.y = WINDOW_HEIGHT - square.size
			square.vy = -abs(square.vy) * BOUNCE_DAMPING


def draw_scene(screen: pygame.Surface, squares: List[MovingSquare]) -> None:
	"""Render one frame."""
	# TODO (Socratic): Give each square its own color field in MovingSquare.
	# TODO (Socratic): Draw a small HUD text with FPS in the top-left corner.
	screen.fill(BACKGROUND_COLOR)

	for square in squares:
		rect = pygame.Rect(int(square.x), int(square.y), square.size, square.size)
		pygame.draw.rect(screen, square.color, rect)

	pygame.display.flip()


def run() -> None:
	"""Application entry point."""
	screen, clock = init_pygame()
	squares = create_initial_squares(SQUARE_COUNT)

	running = True
	while running:
		# TODO (Socratic): Why is dividing by 1000 useful here?
		dt_seconds = clock.tick(FPS) / 1000.0

		# Small idle wait when no input/event is pending to reduce busy polling.
		if not pygame.event.peek():
			pygame.time.wait(IDLE_WAIT_MS)

		running = handle_events()
		update_squares(squares, dt_seconds)
		draw_scene(screen, squares)

	pygame.quit()


if __name__ == "__main__":
	run()
