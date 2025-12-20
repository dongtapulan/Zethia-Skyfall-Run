# ui/hud.py
import pygame

class HUD:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font('assets/fonts/8-bitanco.ttf', 32)
        self.score = 0
        self.health = 100

    def update(self, dt):
        # For example, update animations or counters here
        # dt is delta time (time between frames)
        pass

    def draw(self):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        health_text = self.font.render(f"HP: {self.health}", True, (255, 100, 100))
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(health_text, (20, 60))
