import pygame
import math
import numpy as np
from track import WAYPOINTS


class Car:
    def __init__(self, x, y, brain=None, color=(220, 50, 50)):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.max_speed = 6
        self.accel = 0.2
        self.friction = 0.05
        self.turn_speed = 3

        self.start = (x, y)
        self.alive = True

        # AI
        self.brain = brain
        self.fitness = 0
        self.next_wp = 1
        self.passed = 0
        self.age = 0
        self.max_age = 1500    # 25 sec (60 FPS par), isse zyada jeeyi to band

        # sensors
        self.sensor_angles = [-60, -30, 0, 30, 60]
        self.sensor_len = 200
        self.sensors = [1.0] * len(self.sensor_angles)
        self.sensor_points = []

        # car ki image
        self.base = pygame.Surface((40, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.base, color, (0, 0, 40, 20), border_radius=4)
        pygame.draw.rect(self.base, (150, 200, 255), (24, 3, 10, 14))

    def move(self):
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y -= math.sin(rad) * self.speed

    def update(self, keys):
        """Manual driving (arrow keys)"""
        if not self.alive:
            return

        if keys[pygame.K_UP]:
            self.speed += self.accel
        elif keys[pygame.K_DOWN]:
            self.speed -= self.accel
        else:
            if self.speed > 0:
                self.speed = max(0, self.speed - self.friction)
            elif self.speed < 0:
                self.speed = min(0, self.speed + self.friction)

        self.speed = max(-self.max_speed / 2, min(self.max_speed, self.speed))

        if abs(self.speed) > 0.1:
            direction = 1 if self.speed > 0 else -1
            if keys[pygame.K_LEFT]:
                self.angle += self.turn_speed * direction
            if keys[pygame.K_RIGHT]:
                self.angle -= self.turn_speed * direction

        self.move()

    def update_ai(self):
        """Neural network se driving"""
        if not self.alive:
            return

        steer, throttle = self.brain.forward(np.array(self.sensors))

        self.speed += throttle * self.accel
        self.speed = max(1, min(self.max_speed, self.speed))

        self.angle += steer * self.turn_speed
        self.move()

        self.age += 1
        if self.age > self.max_age:
            self.alive = False
        self.update_progress()

    def update_progress(self):
        wx, wy = WAYPOINTS[self.next_wp]
        d = math.hypot(wx - self.x, wy - self.y)
        if d < 90:
            self.passed += 1
            self.next_wp = (self.next_wp + 1) % len(WAYPOINTS)
            wx, wy = WAYPOINTS[self.next_wp]
            d = math.hypot(wx - self.x, wy - self.y)
        self.fitness = self.passed * 1000 - d

    def cast_sensors(self, track):
        self.sensors = []
        self.sensor_points = []
        for offset in self.sensor_angles:
            rad = math.radians(self.angle + offset)
            dx, dy = math.cos(rad), -math.sin(rad)
            dist = 0
            while dist < self.sensor_len:
                px = self.x + dx * dist
                py = self.y + dy * dist
                if track.is_off_road(px, py):
                    break
                dist += 2
            self.sensors.append(dist / self.sensor_len)
            self.sensor_points.append((self.x + dx * dist, self.y + dy * dist))

    def get_corners(self):
        rad = math.radians(self.angle)
        fx, fy = math.cos(rad), -math.sin(rad)
        sx, sy = math.sin(rad), math.cos(rad)
        corners = []
        for dx, dy in [(20, 10), (20, -10), (-20, 10), (-20, -10)]:
            corners.append((self.x + dx * fx + dy * sx,
                            self.y + dx * fy + dy * sy))
        return corners

    def check_collision(self, track):
        for cx, cy in self.get_corners():
            if track.is_off_road(cx, cy):
                self.alive = False
                self.speed = 0
                return

    def reset(self):
        self.x, self.y = self.start
        self.angle = 0
        self.speed = 0
        self.alive = True
        self.fitness = 0
        self.next_wp = 1
        self.passed = 0
        self.age = 0

    def draw_sensors(self, screen):
        for point in self.sensor_points:
            pygame.draw.line(screen, (255, 255, 0), (self.x, self.y), point, 1)
            pygame.draw.circle(screen, (255, 0, 0), (int(point[0]), int(point[1])), 4)

    def draw(self, screen):
        rotated = pygame.transform.rotate(self.base, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        screen.blit(rotated, rect)