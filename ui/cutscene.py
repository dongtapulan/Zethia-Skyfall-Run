import pygame
import random
from core.settings import *

class Cutscene:
    def __init__(self, screen):
        self.screen = screen
        
        # ----- Cutscene state -----
        self.current_scene = "opening"  # "opening", "witch_dialogue", "complete"
        
        # ----- Load backgrounds and SCALE THEM -----
        self.bg_normal = pygame.image.load("assets/cutscenes/zethia_city.png").convert_alpha()
        self.bg_corrupted = pygame.image.load("assets/cutscenes/zethia_city_corrupted.png").convert_alpha()
        self.bg_witch = pygame.image.load("assets/cutscenes/witch_cutscene.png").convert_alpha()

        # --- SCALE to cover entire screen (maintains aspect ratio) ---
        # Calculate scale ratio to cover entire screen (no black bars)
        screen_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
        
        # Scale opening backgrounds
        bg_ratio = self.bg_normal.get_width() / self.bg_normal.get_height()
        if bg_ratio > screen_ratio:
            scale_ratio = SCREEN_WIDTH / self.bg_normal.get_width()
            new_width = SCREEN_WIDTH
            new_height = int(self.bg_normal.get_height() * scale_ratio)
        else:
            scale_ratio = SCREEN_HEIGHT / self.bg_normal.get_height()
            new_width = int(self.bg_normal.get_width() * scale_ratio)
            new_height = SCREEN_HEIGHT

        self.bg_normal = pygame.transform.scale(self.bg_normal, (new_width, new_height))
        self.bg_corrupted = pygame.transform.scale(self.bg_corrupted, (new_width, new_height))

        # Scale witch background
        witch_ratio = self.bg_witch.get_width() / self.bg_witch.get_height()
        if witch_ratio > screen_ratio:
            witch_scale = SCREEN_WIDTH / self.bg_witch.get_width()
            witch_width = SCREEN_WIDTH
            witch_height = int(self.bg_witch.get_height() * witch_scale)
        else:
            witch_scale = SCREEN_HEIGHT / self.bg_witch.get_height()
            witch_width = int(self.bg_witch.get_width() * witch_scale)
            witch_height = SCREEN_HEIGHT

        self.bg_witch = pygame.transform.scale(self.bg_witch, (witch_width, witch_height))

        # Position to center the backgrounds (may crop edges)
        self.bg_x = (SCREEN_WIDTH - new_width) // 2
        self.bg_y = (SCREEN_HEIGHT - new_height) // 2
        self.witch_bg_x = (SCREEN_WIDTH - witch_width) // 2
        self.witch_bg_y = (SCREEN_HEIGHT - witch_height) // 2

        # Camera slow pan (moves slightly to the right)
        self.cam_x = 0
        self.cam_speed = 15  # slow cinematic pan

        # Corruption fade (opacity)
        self.use_corrupted = False
        self.fade_alpha = 0
        self.fade_speed = 80

        # Witch scene transition
        self.witch_scene_alpha = 0
        self.witch_scene_fade_speed = 3

        # ----- Story text -----
        try:
            self.font = pygame.font.Font("assets/fonts/8-bitanco.ttf", 36)
        except:
            try:
                self.font = pygame.font.Font("assets/fonts/Retro Gaming.ttf", 36)
            except:
                self.font = pygame.font.SysFont("arial", 36)
        
        # Dialogue font (slightly smaller for speech)
        try:
            self.dialogue_font = pygame.font.Font("assets/fonts/8-bitanco.ttf", 32)
        except:
            try:
                self.dialogue_font = pygame.font.Font("assets/fonts/Retro Gaming.ttf", 32)
            except:
                self.dialogue_font = pygame.font.SysFont("arial", 32)
        
        # Opening scene text
        self.opening_text = [
            "In the heart of the Zethia Republic lies ZyriL,",
            "the ancient World Tree whose glow once sustained all life.",
            "",
            "But now its light is fading...",
            "and a mysterious gloom spreads across the land.",
            "",
            "Our story begins with Mae —",
            "the Witch of the Whispering Woods.",
        ]

        # Witch dialogue text
        self.witch_dialogue = [
            "Mae: The air... it grows heavy with darkness.",
            "ZyriL's glow weakens with each passing night.",
            "",
            "I can feel it in the wind's whisper,",
            "in the trembling leaves of the ancient trees.",
            "",
            "Something ancient stirs...",
            "and it hungers for the World Tree's light.",
            "",
            "But I am no ordinary witch.",
            "The woods have shared their secrets with me,",
            "and I will not let this darkness consume us.",
            "",
            "The time has come to act.",
        ]

        # Current text set based on scene
        self.current_text_set = self.opening_text
        
        # Text display variables
        self.display_text = ""
        self.text_index = 0
        self.char_index = 0
        self.typing_speed = 28
        self.typing_timer = 0
        self.finished = False

        # When corruption should appear (line index)
        self.corrupt_trigger_line = 3

        # ----- Particles -----
        self.particles = []
        self.magic_particles = []  # Special particles for witch scene

        # Cutscene intro fade
        self.cutscene_fade_alpha = 255  # Start black
        self.cutscene_fade_speed = 2

        # Spacebar control
        self.space_pressed = False
        self.space_handled = False  # Prevent multiple triggers
        self.current_line_complete = False
        self.continue_prompt_font = pygame.font.Font(None, 30)

        # Text display surfaces
        self.text_surface = pygame.Surface((SCREEN_WIDTH - 160, 100), pygame.SRCALPHA)
        self.dialogue_surface = pygame.Surface((SCREEN_WIDTH - 200, 120), pygame.SRCALPHA)

        # Text box positions
        self.opening_text_rect = pygame.Rect(80, SCREEN_HEIGHT - 150, SCREEN_WIDTH - 160, 100)
        self.dialogue_rect = pygame.Rect(100, SCREEN_HEIGHT - 180, SCREEN_WIDTH - 200, 120)

        # Witch scene specific
        self.witch_scene_started = False
        self.name_tag_font = pygame.font.Font(None, 34)
        self.name_tag_surface = pygame.Surface((200, 40), pygame.SRCALPHA)

    # ----------------------------------------------------
    # PARTICLES
    # ----------------------------------------------------
    def update_particles(self, dt):
        # Random chance to create new floating particles
        if random.random() < 0.08:
            self.particles.append({
                "x": random.randint(0, SCREEN_WIDTH),
                "y": SCREEN_HEIGHT + 20,
                "speed": random.uniform(20, 50),
                "alpha": random.randint(150, 230),
                "size": random.randint(2, 5),
                "color": (255, 200, 130)  # Warm light
            })

        # Update & fade particles
        for p in self.particles[:]:
            p["y"] -= p["speed"] * dt / 1000
            p["alpha"] -= 45 * dt / 1000

            if p["alpha"] <= 0:
                self.particles.remove(p)

    # ----------------------------------------------------
    # MAGIC PARTICLES (for witch scene)
    # ----------------------------------------------------
    def update_magic_particles(self, dt):
        # Create magical energy particles around Mae
        if random.random() < 0.12 and self.current_scene == "witch_dialogue":
            # Particles emanate from center/bottom of screen
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.uniform(100, 300)
            speed = random.uniform(40, 100)
            
            self.magic_particles.append({
                "x": SCREEN_WIDTH // 2 + distance * random.uniform(-0.5, 0.5),
                "y": SCREEN_HEIGHT - 100,
                "speed_x": random.uniform(-30, 30),
                "speed_y": random.uniform(-speed, -speed * 0.3),
                "alpha": random.randint(180, 255),
                "size": random.randint(3, 8),
                "color": (
                    random.randint(150, 255),  # R
                    random.randint(100, 200),  # G
                    random.randint(200, 255)   # B (magical blue-purple)
                ),
                "life": random.uniform(1.0, 2.0)
            })

        # Update magic particles
        for p in self.magic_particles[:]:
            p["x"] += p["speed_x"] * dt / 1000
            p["y"] += p["speed_y"] * dt / 1000
            p["life"] -= dt / 1000
            p["alpha"] = int(p["life"] * 255)
            
            if p["life"] <= 0:
                self.magic_particles.remove(p)

    # ----------------------------------------------------
    # TYPING ANIMATION
    # ----------------------------------------------------
    def update_typing(self, dt):
        if self.text_index >= len(self.current_text_set):
            if self.current_scene == "opening":
                # Transition to witch scene
                self.current_scene = "witch_dialogue"
                self.current_text_set = self.witch_dialogue
                self.text_index = 0
                self.display_text = ""
                self.char_index = 0
                self.current_line_complete = False
                self.witch_scene_started = True
                return
            else:
                self.finished = True
                return

        # Trigger corruption effect in opening scene
        if self.current_scene == "opening" and self.text_index == self.corrupt_trigger_line:
            self.use_corrupted = True

        line = self.current_text_set[self.text_index]
        
        # If spacebar is pressed and not handled yet, complete the current line instantly
        if self.space_pressed and not self.space_handled and not self.current_line_complete:
            self.display_text = line
            self.char_index = len(line)
            self.current_line_complete = True
            self.space_handled = True
            return
        
        # Normal typing animation
        self.typing_timer += dt

        if self.typing_timer > self.typing_speed:
            self.typing_timer = 0

            if self.char_index < len(line):
                self.display_text += line[self.char_index]
                self.char_index += 1
                
                # Check if we've reached the end of the line
                if self.char_index >= len(line):
                    self.current_line_complete = True
            else:
                self.current_line_complete = True

    # ----------------------------------------------------
    # UPDATE CUTSCENE LOGIC
    # ----------------------------------------------------
    def update(self, dt, events=None):
        # Reset space handled flag at start of update
        self.space_handled = False
        
        # Check for spacebar input using events (more reliable)
        if events is None:
            events = pygame.event.get()
            
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.space_pressed = True
                    self.space_handled = False  # Reset for new press

        # Fade in cutscene at start
        if self.cutscene_fade_alpha > 0:
            self.cutscene_fade_alpha -= self.cutscene_fade_speed
            if self.cutscene_fade_alpha < 0:
                self.cutscene_fade_alpha = 0

        # Handle scene transitions
        if self.current_scene == "opening":
            # Slow horizontal camera pan
            self.cam_x += self.cam_speed * dt / 1000
            if self.cam_x > 40:
                self.cam_x = 40

            # Background corruption fade
            if self.use_corrupted and self.fade_alpha < 255:
                self.fade_alpha += self.fade_speed * dt / 1000
                if self.fade_alpha > 255:
                    self.fade_alpha = 255

        elif self.current_scene == "witch_dialogue":
            # Fade in witch scene
            if self.witch_scene_alpha < 255:
                self.witch_scene_alpha += self.witch_scene_fade_speed
                if self.witch_scene_alpha > 255:
                    self.witch_scene_alpha = 255

        # Update particles
        self.update_particles(dt)
        self.update_magic_particles(dt)
        self.update_typing(dt)
        
        # If spacebar is pressed and current line is complete, move to next line
        if self.space_pressed and self.current_line_complete and not self.space_handled:
            self.text_index += 1
            if self.text_index < len(self.current_text_set):
                self.display_text = ""
                self.char_index = 0
                self.current_line_complete = False
            self.space_handled = True
        
        # Reset space_pressed after handling
        self.space_pressed = False

    # ----------------------------------------------------
    # DRAW OPENING SCENE
    # ----------------------------------------------------
    def draw_opening_scene(self):
        # FILL WITH BLACK BACKGROUND FIRST
        self.screen.fill((0, 0, 0))
        
        # DRAW NORMAL BACKGROUND (scaled to cover screen)
        self.screen.blit(self.bg_normal, (self.bg_x - self.cam_x, self.bg_y))

        # DRAW CORRUPTED VERSION OVER IT
        if self.use_corrupted:
            corrupted = self.bg_corrupted.copy()
            corrupted.set_alpha(self.fade_alpha)
            self.screen.blit(corrupted, (self.bg_x - self.cam_x, self.bg_y))

        # DRAW PARTICLES
        for p in self.particles:
            s = pygame.Surface((p["size"], p["size"]), pygame.SRCALPHA)
            # Get color values and ensure they are valid integers in 0-255 range
            try:
                r = int(p["color"][0])
                g = int(p["color"][1])
                b = int(p["color"][2])
                a = int(p["alpha"])
                
                # Clamp values to valid range
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
                a = max(0, min(255, a))
                
                rgba_color = (r, g, b, a)
                s.fill(rgba_color)
                self.screen.blit(s, (p["x"], p["y"]))
            except (ValueError, TypeError, KeyError):
                # Skip this particle if there's an error
                continue

        # DRAW TEXT BOX BACKGROUND
        text_bg_surface = pygame.Surface((self.opening_text_rect.width, self.opening_text_rect.height), pygame.SRCALPHA)
        text_bg_surface.fill((0, 0, 0, 200))
        self.screen.blit(text_bg_surface, self.opening_text_rect)

        # DRAW TEXT
        self.text_surface.fill((0, 0, 0, 0))
        
        if self.display_text:
            # Render text with word wrapping
            words = self.display_text.split(' ')
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_surface = self.font.render(test_line, True, (255, 255, 255))
                if test_surface.get_width() <= self.text_surface.get_width() - 20:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw each line
            y_offset = 0
            for line in lines:
                rendered = self.font.render(line, True, (255, 220, 200))
                self.text_surface.blit(rendered, (10, y_offset))
                y_offset += rendered.get_height() + 5
            
            self.screen.blit(self.text_surface, (self.opening_text_rect.x + 10, self.opening_text_rect.y + 10))

    # ----------------------------------------------------
    # DRAW WITCH DIALOGUE SCENE
    # ----------------------------------------------------
    def draw_witch_scene(self):
        # FILL WITH BLACK BACKGROUND FIRST
        self.screen.fill((0, 0, 0))
        
        # DRAW WITCH BACKGROUND WITH FADE IN
        witch_bg = self.bg_witch.copy()
        witch_bg.set_alpha(self.witch_scene_alpha)
        self.screen.blit(witch_bg, (self.witch_bg_x, self.witch_bg_y))

        # DRAW MAGIC PARTICLES
        for p in self.magic_particles:
            s = pygame.Surface((p["size"], p["size"]), pygame.SRCALPHA)
            # Get color values and ensure they are valid integers in 0-255 range
            try:
                r = int(p["color"][0])
                g = int(p["color"][1])
                b = int(p["color"][2])
                a = int(p["alpha"])
                
                # Clamp values to valid range
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
                a = max(0, min(255, a))
                
                rgba_color = (r, g, b, a)
                s.fill(rgba_color)
                self.screen.blit(s, (p["x"], p["y"]))
            except (ValueError, TypeError, KeyError):
                # Skip this particle if there's an error
                continue

        # DRAW NAME TAG (Mae:)
        self.name_tag_surface.fill((0, 0, 0, 0))
        name_text = "Mae"
        name_surface = self.name_tag_font.render(name_text, True, (220, 180, 255))
        
        # Create a decorative name tag background
        name_bg = pygame.Surface((name_surface.get_width() + 30, name_surface.get_height() + 15), pygame.SRCALPHA)
        name_bg.fill((30, 20, 50, 220))  # Dark purple background
        # Add a border
        pygame.draw.rect(name_bg, (180, 140, 255, 150), (0, 0, name_bg.get_width(), name_bg.get_height()), 2)
        
        self.name_tag_surface.blit(name_bg, (0, 0))
        self.name_tag_surface.blit(name_surface, (15, 8))
        
        # Position name tag above dialogue box
        self.screen.blit(self.name_tag_surface, 
                        (self.dialogue_rect.x + 20, self.dialogue_rect.y - 50))

        # DRAW DIALOGUE BOX BACKGROUND
        dialogue_bg = pygame.Surface((self.dialogue_rect.width, self.dialogue_rect.height), pygame.SRCALPHA)
        dialogue_bg.fill((20, 15, 40, 220))  # Darker purple for witch dialogue
        # Add a magical border
        pygame.draw.rect(dialogue_bg, (180, 140, 255, 180), 
                        (0, 0, self.dialogue_rect.width, self.dialogue_rect.height), 3)
        self.screen.blit(dialogue_bg, self.dialogue_rect)

        # DRAW DIALOGUE TEXT
        self.dialogue_surface.fill((0, 0, 0, 0))
        
        if self.display_text:
            # Render text with word wrapping
            words = self.display_text.split(' ')
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_surface = self.dialogue_font.render(test_line, True, (255, 255, 255))
                if test_surface.get_width() <= self.dialogue_surface.get_width() - 20:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw each line
            y_offset = 0
            for line in lines:
                # Special color for Mae's name
                if line.startswith("Mae:"):
                    rendered = self.dialogue_font.render(line, True, (220, 180, 255))
                else:
                    rendered = self.dialogue_font.render(line, True, (230, 230, 255))
                self.dialogue_surface.blit(rendered, (10, y_offset))
                y_offset += rendered.get_height() + 5
            
            self.screen.blit(self.dialogue_surface, 
                           (self.dialogue_rect.x + 10, self.dialogue_rect.y + 10))

    # ----------------------------------------------------
    # DRAW EVERYTHING
    # ----------------------------------------------------
    def draw(self):
        if self.current_scene == "opening":
            self.draw_opening_scene()
        elif self.current_scene == "witch_dialogue":
            self.draw_witch_scene()

        # DRAW CONTINUE PROMPT (blinking)
        if self.current_line_complete and not self.finished:
            blink = (pygame.time.get_ticks() // 500) % 2 == 0
            if blink:
                prompt_text = "Press SPACE to continue"
                prompt_surface = self.continue_prompt_font.render(prompt_text, True, 
                    (200, 200, 200) if self.current_scene == "opening" else (220, 200, 255))
                prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, 
                    self.opening_text_rect.bottom + 30 if self.current_scene == "opening" 
                    else self.dialogue_rect.bottom + 30))
                self.screen.blit(prompt_surface, prompt_rect)

        # DRAW CUTSCENE FADE (fades in at start)
        if self.cutscene_fade_alpha > 0:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.cutscene_fade_alpha)
            self.screen.blit(fade_surface, (0, 0))

    # ----------------------------------------------------
    # CHECK IF CUTSCENE IS COMPLETE
    # ----------------------------------------------------
    def is_complete(self):
        return self.finished

    # ----------------------------------------------------
    # RESET CUTSCENE (for replayability)
    # ----------------------------------------------------
    def reset(self):
        self.current_scene = "opening"
        self.current_text_set = self.opening_text
        self.display_text = ""
        self.text_index = 0
        self.char_index = 0
        self.finished = False
        self.use_corrupted = False
        self.fade_alpha = 0
        self.witch_scene_alpha = 0
        self.cam_x = 0
        self.cutscene_fade_alpha = 255
        self.particles.clear()
        self.magic_particles.clear()
        self.current_line_complete = False
        self.witch_scene_started = False
        self.space_pressed = False
        self.space_handled = False