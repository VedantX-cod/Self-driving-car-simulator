import pygame
import random
import os
from car import Car
from track import Track, WAYPOINTS
from network import NeuralNetwork

pygame.init()
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("Self-Driving Car Simulator")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

POP_SIZE = 50
ELITE = 3
PARENT_POOL = 10
START = (300, 150)
SAVE_FILE = "best_brain.npz"
track = Track((1000, 700))


def random_color():
    return (random.randint(80, 255), random.randint(80, 255), random.randint(80, 255))


def first_population():
    return [Car(*START, brain=NeuralNetwork(), color=random_color())
            for _ in range(POP_SIZE)]


def seeded_population(brain):
    cars = [Car(*START, brain=brain.copy(), color=(255, 255, 255))]
    while len(cars) < POP_SIZE:
        b = brain.copy()
        b.mutate()
        cars.append(Car(*START, brain=b, color=random_color()))
    return cars


def next_generation(cars):
    cars.sort(key=lambda c: c.fitness, reverse=True)
    parents = [c.brain for c in cars[:PARENT_POOL]]
    new_cars = []
    for c in cars[:ELITE]:
        new_cars.append(Car(*START, brain=c.brain.copy(), color=(255, 255, 255)))
    while len(new_cars) < POP_SIZE:
        a, b = random.sample(parents, 2)
        child = NeuralNetwork.crossover(a, b)
        child.mutate()
        new_cars.append(Car(*START, brain=child, color=random_color()))
    return new_cars


def draw_graph(history):
    x0, y0, w, h = 770, 570, 210, 110
    pygame.draw.rect(screen, (20, 20, 20), (x0, y0, w, h))
    pygame.draw.rect(screen, (200, 200, 200), (x0, y0, w, h), 1)
    data = history[-50:]
    if len(data) < 2:
        return
    lo, hi = min(data), max(data)
    span = (hi - lo) or 1
    pts = []
    for i, v in enumerate(data):
        px = x0 + 5 + i * (w - 10) / (len(data) - 1)
        py = y0 + h - 5 - (v - lo) / span * (h - 10)
        pts.append((px, py))
    pygame.draw.lines(screen, (0, 255, 120), False, pts, 2)
    label = font.render("Best fitness", True, (255, 255, 255))
    screen.blit(label, (x0 + 5, y0 - 22))


cars = first_population()
generation = 1
best_ever = float("-inf")
best_brain = None
history = []
fast = False
mode = "train"
demo_car = None
status, status_timer = "", 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                fast = not fast
            elif event.key == pygame.K_r:
                cars = first_population()
                generation, best_ever, best_brain = 1, float("-inf"), None
                history = []
                mode = "train"
            elif event.key == pygame.K_s:
                if best_brain is not None:
                    best_brain.save(SAVE_FILE)
                    status, status_timer = "Best brain saved!", 120
                else:
                    status, status_timer = "Abhi koi generation complete nahi hui", 120
            elif event.key == pygame.K_l:
                if os.path.exists(SAVE_FILE):
                    best_brain = NeuralNetwork.load(SAVE_FILE)
                    cars = seeded_population(best_brain)
                    mode = "train"
                    status, status_timer = "Saved brain se training continue", 120
                else:
                    status, status_timer = "Save file nahi mili", 120
            elif event.key == pygame.K_d:
                if mode == "demo":
                    mode = "train"
                else:
                    brain = best_brain
                    if brain is None and os.path.exists(SAVE_FILE):
                        brain = NeuralNetwork.load(SAVE_FILE)
                    if brain is not None:
                        demo_car = Car(*START, brain=brain.copy(), color=(255, 80, 80))
                        demo_car.max_age = 10 ** 9   # demo mein time limit nahi
                        mode = "demo"
                    else:
                        status, status_timer = "Pehle train karo ya save file chahiye", 120

    track.draw(screen)

    if mode == "train":
        steps = 5 if fast else 1
        for _ in range(steps):
            for car in cars:
                if car.alive:
                    car.cast_sensors(track)
                    car.update_ai()
                    car.check_collision(track)

            if not any(c.alive for c in cars):
                best_car = max(cars, key=lambda c: c.fitness)
                history.append(best_car.fitness)
                if best_car.fitness > best_ever:
                    best_ever = best_car.fitness
                    best_brain = best_car.brain.copy()
                cars = next_generation(cars)
                generation += 1

        for car in cars:
            if car.alive:
                car.draw(screen)
        alive_cars = [c for c in cars if c.alive]
        if alive_cars:
            max(alive_cars, key=lambda c: c.fitness).draw_sensors(screen)

        laps = max(c.passed for c in cars) // len(WAYPOINTS)
        l1 = f"TRAIN  Gen: {generation}   Alive: {len(alive_cars)}/{POP_SIZE}   Laps: {laps}"
        l2 = f"F fast({'ON' if fast else 'OFF'})  S save  L load  D demo  R restart"
        draw_graph(history)
    else:
        demo_car.cast_sensors(track)
        demo_car.update_ai()
        demo_car.check_collision(track)
        if not demo_car.alive:
            demo_car.reset()
        demo_car.draw_sensors(screen)
        demo_car.draw(screen)
        l1 = f"DEMO  Laps: {demo_car.passed // len(WAYPOINTS)}"
        l2 = "D = training mode par wapas"

    screen.blit(font.render(l1, True, (255, 255, 255)), (10, 10))
    screen.blit(font.render(l2, True, (255, 255, 255)), (10, 36))
    if status_timer > 0:
        screen.blit(font.render(status, True, (255, 255, 0)), (10, 62))
        status_timer -= 1

    pygame.display.flip()
    clock.tick(60)

pygame.quit()