import pygame
import math
import random
from core.settings import *

class Background:
    def __init__(self):
        # --- Load parallax layers ---
        self.cloud_far = pygame.image.load("assets/backgrounds/parallax_layers/clouds_far.png").convert_alpha()
        self.cloud_mid = pygame.image.load("assets/backgrounds/parallax_layers/clouds_mid.png").convert_alpha()
        self.trees_close_original = pygame.image.load("assets/backgrounds/parallax_layers/trees_close.png").convert_alpha()

        # --- Load mountains ---
        self.mountain1_original = pygame.image.load("assets/backgrounds/parallax_layers/mountain1.png").convert_alpha()
        self.mountain2_original = pygame.image.load("assets/backgrounds/parallax_layers/mountain2.png").convert_alpha()

        # --- Scale adjustments (cache these) ---
        self.trees_close = pygame.transform.smoothscale(
            self.trees_close_original,
            (int(self.trees_close_original.get_width() * 2.3),
             int(self.trees_close_original.get_height() * 2.3))
        )

        self.mountain1 = pygame.transform.smoothscale(
            self.mountain1_original,
            (int(self.mountain1_original.get_width() * 2.6),
             int(self.mountain1_original.get_height() * 2.6))
        )
        self.mountain2 = pygame.transform.smoothscale(
            self.mountain2_original,
            (int(self.mountain2_original.get_width() * 2.6),
             int(self.mountain2_original.get_height() * 2.6))
        )

        # --- Scroll offsets ---
        self.far_x = 0
        self.mid_x = 0
        self.mountain_x = 0
        self.close_x = 0

        # --- Parallax speeds ---
        self.far_speed = 10
        self.mid_speed = 20
        self.mountain_speed = 15
        self.close_speed = 40

        # --- Sun settings ---
        self.sun_pos = (WIDTH * 0.8, HEIGHT * 0.3)
        self.sun_radius = 80
        self.sun_glow_radius = 180
        self.glow_timer = 0.0

        # --- Random offset pattern for mountains ---
        self.mountain_pattern = []
        self._generate_mountain_pattern()

        # --- Enhanced graphics elements ---
        self.stars = []
        self._generate_stars()
        self.birds = []
        self._generate_birds()
        self.butterflies = []
        self._generate_butterflies()
        self.light_rays = []
        self._generate_light_rays()

        # --- Progress system ---
        self.progress = 0.0
        self.progress_speed = 0.1  # Progress per second
        self.level_complete = False
        self.completion_show_time = 0
        self.show_completion = False
        
        # --- Quest Complete UI ---
        self.completion_font_large = pygame.font.Font("assets/fonts/8-bitanco.ttf", 72)
        self.completion_font_medium = pygame.font.Font("assets/fonts/8-bitanco.ttf", 36)
        self.completion_font_small = pygame.font.Font("assets/fonts/8-bitanco.ttf", 28)
        
        # Fallback fonts
        if self.completion_font_large is None:
            self.completion_font_large = pygame.font.SysFont("arial", 72, bold=True)
        if self.completion_font_medium is None:
            self.completion_font_medium = pygame.font.SysFont("arial", 36, bold=True)
        if self.completion_font_small is None:
            self.completion_font_small = pygame.font.SysFont("arial", 28, bold=True)

        # --- PERFORMANCE OPTIMIZATIONS ---
        # Pre-render sun surface
        self.sun_surface = None
        self.last_sun_update = 0
        self.sun_update_interval = 50  # Update sun every 50ms
        
        # Pre-render fade surface
        self.fade_surface = None
        self.last_fade_update = 0
        self.fade_update_interval = 1000  # Update fade every second
        
        # Pre-calculate gradient colors
        self._precalculate_gradient()
        
        # Cache progress bar surfaces
        self.progress_bar_bg = None
        self.last_progress = -1
        
        # Reduce particle counts for better performance
        self._optimize_particles()

    def _optimize_particles(self):
        """Reduce particle counts for better performance"""
        # Reduce stars from 80 to 40
        if len(self.stars) > 40:
            self.stars = self.stars[:40]
        
        # Reduce birds from 6 to 4
        if len(self.birds) > 4:
            self.birds = self.birds[:4]
        
        # Reduce butterflies from 8 to 5
        if len(self.butterflies) > 5:
            self.butterflies = self.butterflies[:5]
        
        # Reduce light rays from 12 to 8
        if len(self.light_rays) > 8:
            self.light_rays = self.light_rays[:8]

    def _precalculate_gradient(self):
        """Pre-calculate sky gradient colors to avoid per-pixel calculations"""
        self.gradient_colors_top = []
        self.gradient_colors_bottom = []
        
        # Top gradient (sky)
        for y in range(HEIGHT // 2):
            blend = y / (HEIGHT // 2)
            top_color = (90, 160, 240)
            middle_color = (180, 200, 255)
            r = top_color[0] * (1 - blend) + middle_color[0] * blend
            g = top_color[1] * (1 - blend) + middle_color[1] * blend
            b = top_color[2] * (1 - blend) + middle_color[2] * blend
            self.gradient_colors_top.append((int(r), int(g), int(b)))
        
        # Bottom gradient (horizon)
        for y in range(HEIGHT // 2):
            blend = y / (HEIGHT // 2)
            middle_color = (180, 200, 255)
            horizon_color = (255, 180, 100)
            r = middle_color[0] * (1 - blend) + horizon_color[0] * blend
            g = middle_color[1] * (1 - blend) + horizon_color[1] * blend
            b = middle_color[2] * (1 - blend) + horizon_color[2] * blend
            self.gradient_colors_bottom.append((int(r), int(g), int(b)))

    def _generate_stars(self):
        """Generate twinkling stars in the sky - OPTIMIZED"""
        for _ in range(40):  # Reduced from 80
            self.stars.append({
                "x": random.randint(0, WIDTH),
                "y": random.randint(0, HEIGHT // 3),
                "size": random.uniform(1.0, 2.5),  # Smaller size range
                "brightness": random.uniform(0.3, 1.0),
                "twinkle_speed": random.uniform(0.5, 1.5),  # Slower twinkle
                "twinkle_offset": random.uniform(0.0, 6.28)
            })

    def _generate_birds(self):
        """Generate flying birds - OPTIMIZED"""
        for _ in range(4):  # Reduced from 6
            self.birds.append({
                "x": random.randint(-100, WIDTH),
                "y": random.randint(50, HEIGHT // 4),
                "speed": random.uniform(40, 80),  # Faster to reduce screen time
                "size": random.uniform(0.8, 1.2),
                "flap_timer": random.uniform(0.0, 6.28),
                "flap_speed": random.uniform(2.0, 3.0)  # Slower flapping
            })

    def _generate_butterflies(self):
        """Generate fluttering butterflies - OPTIMIZED"""
        for _ in range(5):  # Reduced from 8
            self.butterflies.append({
                "x": random.randint(0, WIDTH),
                "y": random.randint(HEIGHT // 2, HEIGHT - 200),
                "speed_x": random.uniform(-15, 15),  # Slower movement
                "speed_y": random.uniform(-10, 10),
                "size": random.uniform(0.6, 0.9),  # Smaller
                "color": (
                    random.randint(200, 255),
                    random.randint(150, 220),
                    random.randint(100, 180)
                ),
                "flap_phase": random.uniform(0.0, 6.28),
                "flap_speed": random.uniform(2.0, 4.0)  # Slower flapping
            })

    def _generate_light_rays(self):
        """Generate magical light rays from the sun - OPTIMIZED"""
        for _ in range(8):  # Reduced from 12
            angle = random.uniform(0, 360)
            length = random.uniform(80, 200)  # Shorter rays
            self.light_rays.append({
                "angle": math.radians(angle),
                "length": length,
                "alpha": random.randint(30, 80),  # Less opaque
                "pulse_speed": random.uniform(0.3, 1.0),  # Slower pulse
                "pulse_offset": random.uniform(0.0, 6.28),
                "width": random.uniform(2, 6)  # Thinner
            })

    def _generate_mountain_pattern(self):
        """Generate smooth but slightly irregular mountain placement to avoid perfect repetition."""
        x = 0
        self.mountain_pattern.clear()
        while x < WIDTH * 2.2:  # extend slightly beyond screen width
            img = random.choice([self.mountain1, self.mountain2])
            gap = random.randint(60, 100)  # Larger gaps for fewer mountains
            self.mountain_pattern.append((x, img))
            # Overlap slightly to blend smoothly
            x += img.get_width() - 300 + gap  # More overlap, fewer mountains

    def _create_sun_surface(self):
        """Create and cache the sun surface"""
        current_time = pygame.time.get_ticks()
        if self.sun_surface is not None and (current_time - self.last_sun_update) < self.sun_update_interval:
            return self.sun_surface
            
        self.last_sun_update = current_time
        sun_surface = pygame.Surface((self.sun_glow_radius * 2, self.sun_glow_radius * 2), pygame.SRCALPHA)
        
        # Outer magical glow - simplified
        for i in range(5):  # Reduced from 8
            alpha = 80 - i * 12
            radius = self.sun_radius * 2 + i * 20 + math.sin(self.glow_timer * 0.7) * 8
            glow_color = (255, 220, 160, alpha)
            pygame.draw.circle(
                sun_surface,
                glow_color,
                (self.sun_glow_radius, self.sun_glow_radius),
                int(radius)
            )
        
        # Inner sun glow - simplified
        for i in range(4):  # Reduced from 6
            alpha = 180 - i * 30
            radius = self.sun_radius + i * 12 + math.sin(self.glow_timer) * 6
            pygame.draw.circle(
                sun_surface,
                (255, 230, 180, alpha),
                (self.sun_glow_radius, self.sun_glow_radius),
                int(radius)
            )
        
        # Sun core
        pygame.draw.circle(
            sun_surface,
            (255, 240, 200, 255),
            (self.sun_glow_radius, self.sun_glow_radius),
            int(self.sun_radius * 0.8)
        )
        
        self.sun_surface = sun_surface
        return sun_surface

    def _create_fade_surface(self):
        """Create and cache the fade surface"""
        current_time = pygame.time.get_ticks()
        if self.fade_surface is not None and (current_time - self.last_fade_update) < self.fade_update_interval:
            return self.fade_surface
            
        self.last_fade_update = current_time
        fade = pygame.Surface((WIDTH, 200), pygame.SRCALPHA)
        
        # Draw gradient
        for i in range(200):
            alpha = int(100 * (i / 200))
            r = 245 * (1 - i/200) + 180 * (i/200)
            g = 200 * (1 - i/200) + 140 * (i/200)
            b = 150 * (1 - i/200) + 220 * (i/200)
            pygame.draw.line(fade, (int(r), int(g), int(b), alpha), 
                           (0, i), (WIDTH, i))
        
        # Add fewer magical sparkles
        for _ in range(10):  # Reduced from 20
            x = random.randint(0, WIDTH)
            y = random.randint(0, 200)
            size = random.uniform(1.0, 2.0)  # Smaller
            brightness = random.uniform(0.5, 0.8)  # Dimmer
            sparkle_color = (255, 255, 200, int(100 * brightness))  # Less opaque
            pygame.draw.circle(fade, sparkle_color, (x, y), int(size))
        
        self.fade_surface = fade
        return fade

    def update_progress(self, dt):
        """Update progress bar and check for level completion"""
        if not self.level_complete:
            self.progress += self.progress_speed * dt / 1000
            if self.progress >= 100.0:
                self.progress = 100.0
                self.level_complete = True
                self.show_completion = True
                self.completion_show_time = pygame.time.get_ticks()

    def update(self, dt):
        # Update progress
        self.update_progress(dt)
        
        # Animate parallax scrolling
        dt_scaled = dt / 1000
        self.far_x -= self.far_speed * dt_scaled
        self.mid_x -= self.mid_speed * dt_scaled
        self.mountain_x -= self.mountain_speed * dt_scaled
        self.close_x -= self.close_speed * dt_scaled

        # Wrap-around scrolling
        if self.far_x <= -WIDTH: self.far_x = 0
        if self.mid_x <= -WIDTH: self.mid_x = 0
        if self.mountain_x <= -WIDTH:
            self.mountain_x = 0
            self._generate_mountain_pattern()
        if self.close_x <= -WIDTH: self.close_x = 0

        # Animate sun glow - slower
        self.glow_timer += dt * 0.001

        # Update stars (twinkling) - only update half each frame
        for i, star in enumerate(self.stars):
            if i % 2 == 0:  # Update every other star
                star["brightness"] = 0.5 + 0.5 * math.sin(self.glow_timer * star["twinkle_speed"] + star["twinkle_offset"])

        # Update birds
        for bird in self.birds:
            bird["x"] += bird["speed"] * dt_scaled
            bird["flap_timer"] += bird["flap_speed"] * dt_scaled
            if bird["x"] > WIDTH + 100:
                bird["x"] = -100
                bird["y"] = random.randint(50, HEIGHT // 4)

        # Update butterflies - only update position every other frame
        current_time = pygame.time.get_ticks()
        for i, butterfly in enumerate(self.butterflies):
            if i % 2 == 0 or current_time % 2 == 0:
                butterfly["x"] += butterfly["speed_x"] * dt_scaled
                butterfly["y"] += butterfly["speed_y"] * dt_scaled
                butterfly["flap_phase"] += butterfly["flap_speed"] * dt_scaled
                
                # Bounce off edges
                if butterfly["x"] < 0 or butterfly["x"] > WIDTH:
                    butterfly["speed_x"] *= -1
                if butterfly["y"] < HEIGHT // 2 or butterfly["y"] > HEIGHT - 100:
                    butterfly["speed_y"] *= -1

    def draw(self, surface):
        # --- Enhanced sky gradient with sunset effect (OPTIMIZED) ---
        # Draw pre-calculated gradients
        for y, color in enumerate(self.gradient_colors_top):
            pygame.draw.line(surface, color, (0, y), (WIDTH, y))
        
        for y, color in enumerate(self.gradient_colors_bottom):
            pygame.draw.line(surface, color, (0, HEIGHT // 2 + y), (WIDTH, HEIGHT // 2 + y))

        # --- Draw stars - only draw visible ones ---
        for star in self.stars:
            if star["brightness"] > 0.1:  # Only draw if visible
                brightness = star["brightness"]
                star_color = (255, 255, 255, int(brightness * 255))
                star_size = star["size"] * brightness
                pygame.draw.circle(surface, star_color[:3], 
                                 (int(star["x"]), int(star["y"])), 
                                 int(star_size))

        # --- Enhanced Sun with magical glow (CACHED) ---
        sun_surface = self._create_sun_surface()
        surface.blit(sun_surface, (self.sun_pos[0] - self.sun_glow_radius, self.sun_pos[1] - self.sun_glow_radius))

        # --- Draw light rays - simplified ---
        current_time = pygame.time.get_ticks()
        for ray in self.light_rays:
            # Only draw every other ray each frame
            if hash(str(ray)) % 2 == current_time % 1000 // 500:
                pulse = 0.5 + 0.5 * math.sin(self.glow_timer * ray["pulse_speed"] + ray["pulse_offset"])
                ray_length = ray["length"] * pulse
                end_x = self.sun_pos[0] + math.cos(ray["angle"]) * ray_length
                end_y = self.sun_pos[1] + math.sin(ray["angle"]) * ray_length
                
                # Draw simple line instead of polygon
                pygame.draw.line(surface, (255, 230, 180, int(ray["alpha"] * pulse)),
                               (self.sun_pos[0], self.sun_pos[1]),
                               (end_x, end_y),
                               int(ray["width"]))

        # --- Parallax clouds ---
        surface.blit(self.cloud_far, (self.far_x, 0))
        surface.blit(self.cloud_far, (self.far_x + WIDTH, 0))
        surface.blit(self.cloud_mid, (self.mid_x, 80))
        surface.blit(self.cloud_mid, (self.mid_x + WIDTH, 80))

        # --- Draw birds - simplified shapes ---
        for bird in self.birds:
            # Simple triangle instead of V shape
            flap_offset = math.sin(bird["flap_timer"]) * 3
            points = [
                (bird["x"], bird["y"]),
                (bird["x"] - 8 * bird["size"], bird["y"] + 8 * bird["size"] + flap_offset),
                (bird["x"] + 8 * bird["size"], bird["y"] + 8 * bird["size"] + flap_offset)
            ]
            pygame.draw.polygon(surface, (50, 50, 70), points, 0)

        # --- Mountains (smoothly connected background) ---
        mountain_y = HEIGHT - self.mountain1.get_height() + 160
        # Only draw mountains that are visible
        for (x, img) in self.mountain_pattern:
            draw_x = x + self.mountain_x
            if draw_x + img.get_width() > 0 and draw_x < WIDTH:
                surface.blit(img, (draw_x, mountain_y))

        # --- Draw butterflies - simplified ---
        for butterfly in self.butterflies:
            flap = math.sin(butterfly["flap_phase"]) * 3
            # Draw simple circles for wings
            left_wing_pos = (butterfly["x"] - 8 * butterfly["size"], 
                           butterfly["y"] + flap)
            right_wing_pos = (butterfly["x"] + 8 * butterfly["size"], 
                            butterfly["y"] + flap)
            
            pygame.draw.circle(surface, butterfly["color"], 
                             (int(left_wing_pos[0]), int(left_wing_pos[1])), 
                             int(8 * butterfly["size"]))
            pygame.draw.circle(surface, butterfly["color"], 
                             (int(right_wing_pos[0]), int(right_wing_pos[1])), 
                             int(8 * butterfly["size"]))
            
            # Butterfly body
            pygame.draw.circle(surface, (80, 60, 40), 
                             (int(butterfly["x"]), int(butterfly["y"])), 
                             int(3 * butterfly["size"]))

        # --- Trees (foreground layer) ---
        tree_y = HEIGHT - self.trees_close.get_height() + 50
        surface.blit(self.trees_close, (self.close_x, tree_y))
        surface.blit(self.trees_close, (self.close_x + WIDTH, tree_y))

        # --- Enhanced ground fade with magical particles (CACHED) ---
        fade = self._create_fade_surface()
        surface.blit(fade, (0, HEIGHT - 200))

        # --- Draw progress bar ---
        self.draw_progress_bar(surface)

        # --- Draw Quest Complete overlay if level is complete ---
        if self.show_completion:
            self.draw_quest_complete_overlay(surface)

    def draw_progress_bar(self, surface):
        """Draw the progress bar at the top of the screen - OPTIMIZED"""
        bar_width = WIDTH - 100
        bar_height = 25
        bar_x = 50
        bar_y = 20
        
        # Only redraw background if progress changed significantly
        if self.progress_bar_bg is None or abs(self.progress - self.last_progress) > 2:
            self.last_progress = self.progress
            
            # Create progress bar surface
            self.progress_bar_bg = pygame.Surface((bar_width + 4, bar_height + 4), pygame.SRCALPHA)
            
            # Background
            pygame.draw.rect(self.progress_bar_bg, (40, 40, 60, 255), 
                           (0, 0, bar_width + 4, bar_height + 4), border_radius=5)
            pygame.draw.rect(self.progress_bar_bg, (20, 20, 40, 255), 
                           (2, 2, bar_width, bar_height), border_radius=3)
            
            # Decorative elements
            pygame.draw.circle(self.progress_bar_bg, (100, 150, 255, 255), (0, bar_height // 2 + 2), 8)
            pygame.draw.circle(self.progress_bar_bg, (100, 150, 255, 255), (bar_width + 4, bar_height // 2 + 2), 8)
        
        # Draw cached background
        surface.blit(self.progress_bar_bg, (bar_x - 2, bar_y - 2))
        
        # Progress fill (only this changes frequently)
        fill_width = int((self.progress / 100.0) * bar_width)
        if fill_width > 0:
            # Simple fill instead of gradient
            fill_color = (100 + int(155 * (self.progress/100)), 
                         int(180 * (self.progress/100)), 
                         220 + int(35 * (self.progress/100)))
            pygame.draw.rect(surface, fill_color, 
                           (bar_x, bar_y, fill_width, bar_height), border_radius=3)
            
            # Simple glowing edge
            if fill_width > 3:
                pygame.draw.line(surface, (180, 220, 255),
                               (bar_x + fill_width - 3, bar_y),
                               (bar_x + fill_width - 3, bar_y + bar_height), 2)
        
        # Progress text - only update if progress changed
        if int(self.progress) != int(self.last_progress):
            progress_text = f"Quest Progress: {int(self.progress)}%"
            font = pygame.font.Font(None, 24)
            self.progress_text_surface = font.render(progress_text, True, (220, 220, 240))
            self.progress_text_rect = self.progress_text_surface.get_rect(center=(WIDTH // 2, bar_y + bar_height // 2))
        
        if hasattr(self, 'progress_text_surface'):
            surface.blit(self.progress_text_surface, self.progress_text_rect)

    def draw_quest_complete_overlay(self, surface):
        """Draw the Quest Complete overlay with buttons - OPTIMIZED"""
        # Semi-transparent background
        if not hasattr(self, 'overlay_surface'):
            self.overlay_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            self.overlay_surface.fill((0, 0, 0, 180))
        
        surface.blit(self.overlay_surface, (0, 0))
        
        # Update pulse only every few frames
        current_time = pygame.time.get_ticks()
        pulse = 0.5 + 0.5 * math.sin(current_time * 0.003)
        
        # Cache text surfaces
        if not hasattr(self, 'quest_text_surface'):
            self.quest_text_surface = self.completion_font_large.render("QUEST COMPLETE", True, (255, 220, 100))
            self.quest_shadow_surface = self.completion_font_large.render("QUEST COMPLETE", True, (180, 140, 50))
            self.quest_rect = self.quest_text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        
        # Draw shadow and main text
        surface.blit(self.quest_shadow_surface, (self.quest_rect.x + 4, self.quest_rect.y + 4))
        surface.blit(self.quest_text_surface, self.quest_rect)
        
        # Simple glow effect - only draw if pulsing enough
        if pulse > 0.7:
            glow_surface = pygame.Surface((self.quest_rect.width + 20, self.quest_rect.height + 20), pygame.SRCALPHA)
            glow_alpha = int(50 * pulse)
            glow_text = self.completion_font_large.render("QUEST COMPLETE", True, (255, 240, 180, glow_alpha))
            glow_surface.blit(glow_text, (10, 10))
            surface.blit(glow_surface, (self.quest_rect.x - 10, self.quest_rect.y - 10))
        
        # Cache congratulations text
        if not hasattr(self, 'congrats_text_surface'):
            self.congrats_text_surface = self.completion_font_medium.render("You have restored light to Zethia!", True, (220, 240, 255))
            self.congrats_rect = self.congrats_text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        
        surface.blit(self.congrats_text_surface, self.congrats_rect)
        
        # Draw buttons (simplified)
        self._draw_buttons(surface, pulse)

    def _draw_buttons(self, surface, pulse):
        """Draw buttons for quest complete overlay - OPTIMIZED"""
        button_y = HEIGHT // 2 + 50
        button_width = 300
        button_height = 60
        button_spacing = 80
        
        # Cache button surfaces
        if not hasattr(self, 'story_button_surface'):
            # Create story button surface
            self.story_button_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
            pygame.draw.rect(self.story_button_surface, (80, 160, 220), 
                           (0, 0, button_width, button_height), border_radius=10)
            pygame.draw.rect(self.story_button_surface, (180, 220, 255), 
                           (0, 0, button_width, button_height), 3, border_radius=10)
            
            story_text = self.completion_font_small.render("Proceed to Story", True, (240, 250, 255))
            text_rect = story_text.get_rect(center=(button_width//2, button_height//2))
            self.story_button_surface.blit(story_text, text_rect)
            
            # Create exit button surface
            self.exit_button_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
            pygame.draw.rect(self.exit_button_surface, (220, 100, 100), 
                           (0, 0, button_width, button_height), border_radius=10)
            pygame.draw.rect(self.exit_button_surface, (255, 200, 200), 
                           (0, 0, button_width, button_height), 3, border_radius=10)
            
            exit_text = self.completion_font_small.render("Exit Game", True, (255, 240, 240))
            exit_text_rect = exit_text.get_rect(center=(button_width//2, button_height//2))
            self.exit_button_surface.blit(exit_text, exit_text_rect)
        
        # Draw buttons
        story_button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, button_y, button_width, button_height)
        surface.blit(self.story_button_surface, story_button_rect)
        
        exit_button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, button_y + button_spacing, button_width, button_height)
        surface.blit(self.exit_button_surface, exit_button_rect)
        
        # Store button rects for click detection
        self.story_button_rect = story_button_rect
        self.exit_button_rect = exit_button_rect

    def is_mouse_over_button(self, button_rect):
        """Check if mouse is over a button"""
        mouse_pos = pygame.mouse.get_pos()
        return button_rect.collidepoint(mouse_pos)

    def handle_click(self, pos):
        """Handle mouse clicks on the Quest Complete overlay"""
        if not self.show_completion:
            return None
            
        if self.story_button_rect.collidepoint(pos):
            return "proceed_to_story"
        elif self.exit_button_rect.collidepoint(pos):
            return "exit_game"
        return None

    def reset_level(self):
        """Reset the level progress"""
        self.progress = 0.0
        self.level_complete = False
        self.show_completion = False
        # Clear cached surfaces
        self.progress_bar_bg = None
        self.last_progress = -1