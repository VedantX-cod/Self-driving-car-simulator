import pygame

GRASS = (30, 90, 30)
ROAD = (70, 70, 70)

# EASY track (purana, chahiye to wapas use kar sakte ho)
# WAYPOINTS = [(200, 150), (800, 150), (900, 350), (800, 550),
#              (500, 600), (200, 550), (100, 350)]

WAYPOINTS = [(200, 150), (800, 150), (900, 250), (750, 350),
             (900, 480), (800, 620), (550, 550), (400, 640),
             (200, 580), (120, 400), (250, 300), (100, 220)]
ROAD_WIDTH = 100

class Track:
    def __init__(self, size):
        self.surface = pygame.Surface(size)
        self.surface.fill(GRASS)
        n = len(WAYPOINTS)
        for i in range(n):
            a = WAYPOINTS[i]
            b = WAYPOINTS[(i + 1) % n]
            pygame.draw.line(self.surface, ROAD, a, b, ROAD_WIDTH)
            pygame.draw.circle(self.surface, ROAD, a, ROAD_WIDTH // 2)

    def is_off_road(self, x, y):
        x, y = int(x), int(y)
        w, h = self.surface.get_size()
        if x < 0 or y < 0 or x >= w or y >= h:
            return True
        return self.surface.get_at((x, y))[:3] == GRASS

    def draw(self, screen):
        screen.blit(self.surface, (0, 0))