import pygame
from core.settings import *

class MagicBolt:
    def __init__(self, x, y, direction=1, speed=400):
        self.image = pygame.image.load("assets/sprites/Witch/magic_bolt.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.direction = direction  # 1 = right, -1 = left
        self.active = True

    def update(self, dt):
        # Move projectile
        self.rect.x += self.speed * self.direction * dt / 1000

        # Deactivate if off-screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.active = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)
