import pygame
import random
import math
from core.settings import *

class WindParticle:
    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.speed = random.uniform(40, 80)
        self.alpha = random.randint(80, 150)
        self.size = random.randint(2, 5)

    def update(self, dt):
        self.x += self.speed * dt / 1000
        self.y += math.sin(pygame.time.get_ticks() * 0.002) * 0.2
        if self.x > WIDTH:
            self.x = -10
            self.y = random.uniform(0, HEIGHT)

    def draw(self, surface):
        particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (255, 255, 255, self.alpha), (self.size // 2, self.size // 2), self.size // 2)
        surface.blit(particle_surface, (self.x, self.y))

class Environment:
    def __init__(self, count=30):
        self.particles = [WindParticle() for _ in range(count)]

    def update(self, dt):
        for p in self.particles:
            p.update(dt)

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
