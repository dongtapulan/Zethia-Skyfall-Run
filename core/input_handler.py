# core/input_handler.py
import pygame

def handle_input(events, player=None):
    for event in events:
        if event.type == pygame.QUIT:
            return "quit"

    keys = pygame.key.get_pressed()
    if player:
        if keys[pygame.K_w]:
            player.move(0, -1)
        if keys[pygame.K_s]:
            player.move(0, 1)
        if keys[pygame.K_a]:
            player.move(-1, 0)
        if keys[pygame.K_d]:
            player.move(1, 0)
    return None
