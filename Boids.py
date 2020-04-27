import pygame as pg
import numpy as np
from random import random
from pygame import Vector2 as Vector

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1200
FPS = 30


GLOBAL_SCALE = .91
MAX_SPEED = 4.1 * GLOBAL_SCALE
NEARBY_RADIUS = 60 * GLOBAL_SCALE
ALIGNMENT_RADIUS = NEARBY_RADIUS / 5
SEPARATION_RADIUS = 1 * GLOBAL_SCALE
COHESION_RADIUS = NEARBY_RADIUS


BOID_SHAPE = 0.1875  # Modifies triangle shape. Ideal around 0.2
BOID_SIZE = 7.5

BOID_COLOR = (191, 55, 55)
BACKGROUND_COLOR = (26, 34, 43)


# Adjusts vector to a different magnitude while maintaining direction
def vector_set_magnitude(vector, mag):
	angle = np.arctan2(vector.y, vector.x)
	vector.y = mag * np.sin(angle)
	vector.x = mag * np.cos(angle)


class Boid:
	def __init__(self, x, y):
		self.position = Vector(x, y)
		self.velocity = Vector(random() * 2 - 1, random() * 2 - 1)

		self.friends = []

	# Moves a boid to its new position, wraps it if neccessary
	def move(self, boids):
		self.wrap()

		self.get_nearby(boids)
		self.flock()

		self.position += self.velocity

	# Uses all of the rules to update the boid velocity
	def flock(self):
		allign = self.get_alignment()
		avoidDir = self.get_separation()
		noise = Vector(random() * 2 - 1, random() * 2 - 1)
		cohese = self.get_cohesion()

		# Change vector multipliers here:

		allign *= 1.3

		avoidDir *= 0.4

		noise *= 0.1

		cohese *= 8

		# Increaseing a multiplier will give that rule more control over the
		# general direction of the boid. Change at your own risk!d

		self.velocity += allign
		self.velocity += avoidDir
		self.velocity += noise
		self.velocity += cohese

		# Restricts velocity to the max speed so boids don't reach infinite speed

		magnitude = np.hypot(self.velocity.y, self.velocity.x)

		if magnitude > MAX_SPEED:
			vector_set_magnitude(self.velocity, MAX_SPEED)

	# Gets boids nearby to the the current boid
	def get_nearby(self, boids):
		nearby = []
		for b in boids:
			if (b == self):
				continue

			if (np.linalg.norm(self.position - b.position) < NEARBY_RADIUS):
				nearby.append(b)

		self.friends = nearby

	# Gets the alignment vector
	def get_alignment(self):
		sumVector = Vector(0, 0)
		count = 0

		for b in self.friends:
			d = np.linalg.norm(self.position - b.position)

			if d > 0 and d < NEARBY_RADIUS:
				copy = Vector(b.velocity.x, b.velocity.y)
				copy.normalize()
				copy /= d
				sumVector += copy
				count += 1

		return sumVector

	# Gets the seperation vector
	def get_separation(self):
		steer = Vector(0, 0)
		count = 0

		for b in self.friends:
			d = np.linalg.norm(self.position - b.position)
			if d > 0 and d < ALIGNMENT_RADIUS:
				diff = self.position - b.position
				diff.normalize()
				diff /= d
				steer += diff
				count += 1

		if count > 0:
			return steer / count

		return steer

	# Gets the cohesion vector
	def get_cohesion(self):
		neighbordist = 50
		sumVector = Vector(0, 0)
		count = 0

		for b in self.friends:
			d = np.linalg.norm(self.position - b.position)
			if d > 0 and d < COHESION_RADIUS:
				sumVector += b.position
				count += 1
		count = 0
		if (count > 0):
			sumVector /= count

			desired = sumVector - self.position
			vector_set_magnitude(desired, 0.05)

			return desired
		else:
			return Vector(0, 0)

	# Gets the rotated position vectors of a boid based on direction
	def position_vectors(self):
		degree = np.arctan2(self.velocity.y, self.velocity.x)

		triangle = [0, ((1 - BOID_SHAPE) * np.pi), ((1 + BOID_SHAPE) * np.pi)]
		result = list()
		for t in triangle:
			# apply the circle formula
			x = boid.position.x + BOID_SIZE * np.cos(t + degree)
			y = boid.position.y + BOID_SIZE * np.sin(t + degree)
			result.append((x, y))

		return result

	# Makes sure the boids don't fly off the screen
	def wrap(self):
		self.position.x = (self.position.x + SCREEN_WIDTH) % SCREEN_WIDTH
		self.position.y = (self.position.y + SCREEN_HEIGHT) % SCREEN_HEIGHT


class Game:
	def __init__(self, width, height):
		self.paused = False
		self.boids = []
		for x in range(50):
			self.boids.append(Boid(random() * width, random() * height))

	# Adds a boid to a given "x" and "y"
	def add_boid(self, x, y):
		self.boids.append(Boid(x, y))

	# Updates the position of all boids
	def run(self):
		for b in self.boids:
			b.move(self.boids)


if __name__ == "__main__":
	game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
	pg.init()
	screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	clock = pg.time.Clock()
	screen.fill(BACKGROUND_COLOR)

	while True:
		for event in pg.event.get():
			# Exits window on quit
			if event.type == pg.QUIT:
				pg.quit()
				exit(0)
			# Triggers add boid
			elif event.type == pg.MOUSEBUTTONUP:
				pos = pg.mouse.get_pos()
				game.add_boid(pos[0], pos[1])
			# Toggles pause
			elif event.type == pg.KEYUP and event.key == pg.K_SPACE:
				game.paused = not game.paused

		clock.tick(FPS)

		screen.fill(BACKGROUND_COLOR)

		if not game.paused:
			game.run()

		for boid in game.boids:
			pg.draw.polygon(screen, BOID_COLOR, boid.position_vectors())

		pg.display.update()
