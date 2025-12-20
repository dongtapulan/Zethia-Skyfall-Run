import pygame
import traceback
from ui.start_menu import StartMenu
from ui.hud import HUD
from core.settings import *
from core.game_state import GameState
from entities.player import Player
from world.background import Background
from world.environment import Environment
from ui.cutscene import Cutscene

# -----------------------------
# Initialize Pygame & Mixer
# -----------------------------
pygame.init()
pygame.mixer.init()

try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Zethia: Skyfall Run")
except Exception as e:
    print(f"Failed to create display: {e}")
    pygame.quit()
    exit()

clock = pygame.time.Clock()

# -----------------------------
# Try to load and play menu music (with fallback)
# -----------------------------
try:
    pygame.mixer.music.load("assets/music/menu_theme.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Could not load menu music: {e}")
    print("Continuing without music...")

# -----------------------------
# Setup UI, Player, World, Cutscene
# -----------------------------
try:
    menu = StartMenu(screen)
    hud = HUD(screen)
    state = GameState()
    player = Player()
    background = Background()
    environment = Environment()
    cutscene = Cutscene(screen)
except Exception as e:
    print(f"Failed to initialize game components: {e}")
    traceback.print_exc()
    pygame.quit()
    exit()

# --- Transition variables ---
transition_alpha = 0
transition_speed = 3
transition_text = ""
try:
    transition_font = pygame.font.Font("assets/fonts/8-bitanco.ttf", 60)
except:
    transition_font = pygame.font.SysFont("courier", 60, bold=True)  # Fallback font
transition_stage = 0  # 0: fade to black, 1: show text, 2: fade to cutscene

running = True
error_occurred = False
error_message = ""

# -----------------------------
# Main Loop
# -----------------------------
while running:
    try:
        dt = clock.tick(FPS)
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                running = False

        # Clear screen
        screen.fill((0, 0, 0))

        # MENU STATE ---------------------
        if state.current == "menu":
            action = menu.update(events, dt)

            if action == "Start Game":
                try:
                    pygame.mixer.music.fadeout(1000)
                except:
                    pass
                state.set_state("transition")
                transition_alpha = 0
                transition_stage = 0

            elif action == "Quit":
                running = False

            menu.draw(dt)

        # TRANSITION STATE ---------------------
        elif state.current == "transition":
            # Update transition
            if transition_stage == 0:  # Fade to black
                transition_alpha += transition_speed
                if transition_alpha >= 255:
                    transition_alpha = 255
                    transition_stage = 1
                    transition_text = "Zethia: Skyfall Run"
                    
            elif transition_stage == 1:  # Show text
                # Wait a bit then move to cutscene
                if pygame.time.get_ticks() % 3000 < dt:  # Show text for 3 seconds
                    transition_stage = 2
                    
            elif transition_stage == 2:  # Fade to cutscene
                # Start cutscene music and transition
                if transition_alpha == 255:  # Only load music once
                    try:
                        pygame.mixer.music.load("assets/music/cutscene_theme.mp3")
                        pygame.mixer.music.set_volume(0.5)
                        pygame.mixer.music.play(-1)
                    except:
                        print("Could not load cutscene music")

                transition_alpha -= transition_speed
                if transition_alpha <= 0:
                    transition_alpha = 0
                    state.set_state("cutscene")

            # Draw transition
            screen.fill((0, 0, 0))  # Black background
            
            if transition_stage == 1:  # Show text in the middle of black screen
                text_surface = transition_font.render(transition_text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(text_surface, text_rect)
            
            # Apply fade overlay
            if transition_alpha > 0:
                fade_surface = pygame.Surface((WIDTH, HEIGHT))
                fade_surface.fill((0, 0, 0))
                fade_surface.set_alpha(transition_alpha)
                screen.blit(fade_surface, (0, 0))

        # CUTSCENE STATE ---------------------
        elif state.current == "cutscene":
            # Pass events to cutscene for proper spacebar handling
            cutscene.update(dt, events)
            cutscene.draw()

            # Check if cutscene is finished (spacebar will advance through text)
            if cutscene.finished:
                try:
                    pygame.mixer.music.fadeout(800)
                    pygame.mixer.music.load("assets/music/game_theme.mp3")
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)
                except:
                    print("Could not load game music")
                state.set_state("game")

        # GAME STATE ---------------------
        elif state.current == "game":
            background.update(dt)
            environment.update(dt)
            player.update(dt)
            hud.update(dt)

            background.draw(screen)
            environment.draw(screen)
            player.draw(screen)
            hud.draw()

        # Display error message if something went wrong
        if error_occurred:
            error_font = pygame.font.SysFont("arial", 24)
            error_surface = error_font.render(f"Error: {error_message}", True, (255, 0, 0))
            screen.blit(error_surface, (10, 10))

        pygame.display.flip()

    except Exception as e:
        print(f"Error in main loop: {e}")
        traceback.print_exc()
        error_occurred = True
        error_message = str(e)
        # Try to keep running to see error on screen

pygame.quit()