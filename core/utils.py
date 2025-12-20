# core/utils.py
import pygame

def load_image(path, scale=None):
    image = pygame.image.load(path).convert_alpha()
    if scale:
        image = pygame.transform.scale(image, scale)
    return image

def draw_text(surface, text, pos, font, color=(255,255,255)):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)
