import pygame
import math, random
from core import settings, utils
from core.background_manager import BackgroundManager

class StartMenu:
    def __init__(self, screen):
        self.screen = screen
        
        # Load 8-bit style fonts
        try:
            self.title_font = pygame.font.Font("assets/fonts/8-bitanco.ttf", 72)  # Smaller for 8-bit
            self.button_font = pygame.font.Font("assets/fonts/8-bitanco.ttf", 36)
            self.subtitle_font = pygame.font.Font("assets/fonts/8-bitanco.ttf", 24)
            self.hud_font = pygame.font.Font(None, 20)
        except:
            # Fallback with pixelated style
            self.title_font = pygame.font.SysFont("courier", 72, bold=True)
            self.button_font = pygame.font.SysFont("courier", 36, bold=True)
            self.subtitle_font = pygame.font.SysFont("courier", 24)
            self.hud_font = pygame.font.SysFont("courier", 20)

        # --- Buttons ---
        self.buttons = ["START GAME", "QUIT"]  # Uppercase for 8-bit
        self.selected_index = 0
        self.button_rects = []

        # --- Background & HUD ---
        self.bg = BackgroundManager(screen)
        self.version_text = self.hud_font.render("ZETHIA v1.0.0", True, (220, 220, 220))

        # --- Intro Animation ---
        self.intro_stage = 0
        self.intro_timer = 0
        self.fade_surface = pygame.Surface(screen.get_size())
        self.fade_surface.fill((0, 0, 0))
        self.fade_alpha = 255

        # --- Title Animation ---
        self.title_glow_timer = 0
        self.title_float_timer = 0
        self.container_alpha = 0
        self.container_scale = 0.8
        self.title_fadein_done = False
        self.subtitle_alpha = 0

        # --- 8-bit Particle System ---
        self.particles = []
        self.particle_cache = {}
        # Limited 8-bit color palette
        self.particle_colors = [
            (255, 200, 80, 160),   # Gold
            (80, 160, 255, 120),   # Blue
            (255, 100, 150, 100),  # Pink
            (100, 220, 100, 100)   # Green
        ]
        
        # --- Menu effects ---
        self.menu_glow_timer = 0
        self.selection_pulse = 0
        
        # --- Performance ---
        self.frame_times = []
        self.avg_fps = 60
        self.last_particle_spawn = 0
        self.cached_title = None
        self.cached_buttons = {}
        
        pygame.mouse.set_visible(True)
        
        # Pre-render elements
        self.pre_render_elements()

    def pre_render_elements(self):
        """Pre-render 8-bit style elements"""
        # Version text with simple shadow
        version_shadow = self.hud_font.render("ZETHIA v1.0.0", True, (0, 0, 0, 150))
        self.version_text_cached = pygame.Surface(
            (version_shadow.get_width() + 2, version_shadow.get_height() + 2), 
            pygame.SRCALPHA
        )
        self.version_text_cached.blit(version_shadow, (1, 1))
        self.version_text_cached.blit(self.version_text, (0, 0))
        
        # Cache simple particle shapes (squares for 8-bit)
        for size in range(2, 5):
            for color in self.particle_colors:
                key = (size, color[:3])
                if key not in self.particle_cache:
                    surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    # Square particles for 8-bit
                    pygame.draw.rect(surface, color, (0, 0, size * 2, size * 2))
                    self.particle_cache[key] = surface

    # -------------------------------------------------------------------------
    def button_hovered(self, index):
        mouse_pos = pygame.mouse.get_pos()
        return len(self.button_rects) > index and self.button_rects[index].collidepoint(mouse_pos)

    # -------------------------------------------------------------------------
    def spawn_particle(self):
        """Spawn 8-bit style particles"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_particle_spawn < 80:  # Slower spawn
            return
            
        self.last_particle_spawn = current_time
        
        # Simple spawn patterns
        side = random.choice(["top", "right"])
        if side == "top":
            x = random.randint(-20, self.screen.get_width() + 20)
            y = -10
            speed_x = random.uniform(-0.1, 0.1)
            speed_y = random.uniform(0.05, 0.15)
        else:  # right
            x = self.screen.get_width() + 10
            y = random.randint(0, self.screen.get_height())
            speed_x = random.uniform(-0.3, -0.05)
            speed_y = random.uniform(-0.05, 0.05)
        
        color = random.choice(self.particle_colors)
        size = random.randint(2, 4)  # Smaller
        lifetime = random.randint(300, 500)
        
        self.particles.append({
            "pos": [x, y], 
            "color": color,
            "size": size,
            "speed_x": speed_x, 
            "speed_y": speed_y,
            "life": lifetime,
            "max_life": lifetime
        })

    # -------------------------------------------------------------------------
    def update_particles(self, dt):
        """Update particles with 8-bit simplicity"""
        # Limited particle count
        if len(self.particles) < 15:
            self.spawn_particle()

        # Simple particle movement
        for particle in self.particles[:]:
            particle["pos"][0] += particle["speed_x"] * dt / 16.0
            particle["pos"][1] += particle["speed_y"] * dt / 16.0
            particle["life"] -= 1
            
            if (particle["life"] <= 0 or 
                particle["pos"][1] > self.screen.get_height() + 20 or
                particle["pos"][0] < -50 or 
                particle["pos"][0] > self.screen.get_width() + 50):
                self.particles.remove(particle)

    # -------------------------------------------------------------------------
    def draw_particles(self):
        """Draw 8-bit style particles"""
        for particle in self.particles:
            life_ratio = particle["life"] / particle["max_life"]
            alpha = int(255 * life_ratio)
            
            # Get cached square particle
            key = (particle["size"], particle["color"][:3])
            if key in self.particle_cache:
                surface = self.particle_cache[key].copy()
                surface.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
                
                self.screen.blit(surface, 
                               (particle["pos"][0] - particle["size"],
                                particle["pos"][1] - particle["size"]))

    # -------------------------------------------------------------------------
    def update(self, events, dt):
        # Update FPS
        self.frame_times.append(dt)
        if len(self.frame_times) > 30:
            self.frame_times.pop(0)
        if sum(self.frame_times) > 0:
            self.avg_fps = 1000 / (sum(self.frame_times) / len(self.frame_times))
        
        # Intro animation
        if self.intro_stage < 2:
            self.intro_timer += dt
            if self.intro_stage == 0 and self.intro_timer > 1500:  # Shorter
                self.intro_stage = 1
                self.intro_timer = 0
            elif self.intro_stage == 1:
                self.fade_alpha -= 100 * dt / 16.6
                if self.fade_alpha <= 0:
                    self.fade_alpha = 0
                    self.intro_stage = 2
            return None

        # Update selection pulse
        self.selection_pulse += dt * 0.002
        self.menu_glow_timer += dt * 0.001

        # Menu controls
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.buttons)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.buttons)
                elif event.key == pygame.K_RETURN:
                    if self.selected_index == 0:
                        return "Start Game"
                    elif self.selected_index == 1:
                        return "Quit"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i, rect in enumerate(self.button_rects):
                    if rect.collidepoint(mx, my):
                        return "Start Game" if i == 0 else "Quit"

        return None

    # -------------------------------------------------------------------------
    def draw(self, dt):
        # --- Background ---
        self.bg.update_and_draw(dt)

        # --- Update Particles ---
        self.update_particles(dt)

        # --- Intro Stage ---
        if self.intro_stage < 2:
            if self.intro_stage == 0:
                alpha = min(255, int(self.intro_timer / 3))
                logo_text = "ZETHIAN PRODUCTION"  # Uppercase
                
                # Simple 8-bit intro
                intro_surface = pygame.Surface((self.screen.get_width(), 100), pygame.SRCALPHA)
                
                # Main text with simple shadow
                main_font = pygame.font.Font("assets/fonts/8-bitanco.ttf", 32)
                shadow = main_font.render(logo_text, True, (0, 0, 0, alpha))
                main = main_font.render(logo_text, True, (255, 255, 255, alpha))
                
                shadow_rect = shadow.get_rect(center=(intro_surface.get_width() // 2 + 2,
                                                     intro_surface.get_height() // 2 + 2))
                main_rect = main.get_rect(center=(intro_surface.get_width() // 2,
                                                 intro_surface.get_height() // 2))
                
                intro_surface.blit(shadow, shadow_rect)
                intro_surface.blit(main, main_rect)
                
                screen_rect = intro_surface.get_rect(center=(self.screen.get_width() // 2,
                                                           self.screen.get_height() // 2))
                self.screen.blit(intro_surface, screen_rect)
            else:
                self.fade_surface.set_alpha(int(self.fade_alpha))
                self.screen.blit(self.fade_surface, (0, 0))
            return

        # --- Title Animation ---
        self.title_glow_timer += dt * 0.002
        self.title_float_timer += dt * 0.001
        
        # 8-bit color cycling effect
        glow_phase = int(math.sin(self.title_glow_timer) * 127 + 128)
        title_color = (255, glow_phase, 150)  # Color cycling
        title_offset = 2 * math.sin(self.title_float_timer)  # Minimal movement

        # Fade in
        if not self.title_fadein_done:
            self.container_alpha = min(220, self.container_alpha + dt * 0.2)
            self.container_scale = min(1.0, self.container_scale + dt * 0.0006)
            self.subtitle_alpha = min(255, self.subtitle_alpha + dt * 0.3)
            if self.container_alpha >= 220:
                self.title_fadein_done = True

        # --- 8-bit Title Container ---
        container_width = 800  # Narrower for 8-bit
        container_height = 120
        
        # Create pixelated container
        container = pygame.Surface((container_width, container_height), pygame.SRCALPHA)
        
        # Pixel border
        border_color = (255, 200, 150, self.container_alpha)
        # Top border
        pygame.draw.rect(container, border_color, (0, 0, container_width, 4))
        # Bottom border
        pygame.draw.rect(container, border_color, (0, container_height-4, container_width, 4))
        # Side borders
        pygame.draw.rect(container, border_color, (0, 0, 4, container_height))
        pygame.draw.rect(container, border_color, (container_width-4, 0, 4, container_height))
        
        # Fill with subtle pattern
        fill_color = (30, 30, 40, self.container_alpha // 3)
        pygame.draw.rect(container, fill_color, (4, 4, container_width-8, container_height-8))
        
        # Add pixel grid pattern
        for x in range(8, container_width-8, 16):
            for y in range(8, container_height-8, 16):
                if (x + y) % 32 == 0:
                    pygame.draw.rect(container, (60, 60, 70, self.container_alpha // 4),
                                   (x, y, 4, 4))
        
        # Scale and position
        scaled_container = pygame.transform.scale(
            container, 
            (int(container_width * self.container_scale), 
             int(container_height * self.container_scale))
        )
        c_rect = scaled_container.get_rect(center=(self.screen.get_width() // 2, 140))
        self.screen.blit(scaled_container, c_rect)

        # --- 8-bit Title ---
        if self.cached_title is None:
            self.cached_title = self.title_font.render("ZETHIA: SKYFALL RUN", True, title_color)
        
        title_rect = self.cached_title.get_rect(center=(self.screen.get_width() // 2, 
                                                       140 + title_offset))
        
        # Simple shadow
        shadow = self.title_font.render("ZETHIA: SKYFALL RUN", True, (0, 0, 0, 100))
        shadow_rect = shadow.get_rect(center=(self.screen.get_width() // 2 + 2, 
                                             140 + title_offset + 2))
        self.screen.blit(shadow, shadow_rect)
        
        # Main title
        self.screen.blit(self.cached_title, title_rect)
        
        # --- 8-bit Subtitle ---
        if self.subtitle_alpha > 0:
            subtitle_text = "A JOURNEY THROUGH THE WHISPERING WOODS"
            subtitle_render = self.subtitle_font.render(subtitle_text, 
                                                       True, 
                                                       (180, 200, 220, int(self.subtitle_alpha)))
            subtitle_rect = subtitle_render.get_rect(center=(self.screen.get_width() // 2, 190))
            self.screen.blit(subtitle_render, subtitle_rect)

        # --- Buttons ---
        self.button_rects = []
        button_y_start = 280
        for i, label in enumerate(self.buttons):
            rect_y = button_y_start + i * 70
            base_surface = self.button_font.render(label, True, (220, 220, 220))
            rect = base_surface.get_rect(center=(self.screen.get_width() // 2, rect_y))
            self.button_rects.append(rect)

        # --- 8-bit Button Drawing ---
        for i, label in enumerate(self.buttons):
            hovered = self.button_hovered(i)
            selected = i == self.selected_index
            
            # Simple pulse effect
            pulse = 0.5 + 0.5 * math.sin(self.selection_pulse)
            
            if selected or hovered:
                # Selected button (bright with border)
                color = (255, 220, 180)
                bg_color = (40, 40, 60, 200)
                border_color = (255, 200, 100)
                
                # Draw button background
                button_bg = pygame.Surface((self.button_rects[i].width + 40,
                                          self.button_rects[i].height + 20),
                                          pygame.SRCALPHA)
                
                # Solid fill
                pygame.draw.rect(button_bg, bg_color, (0, 0, button_bg.get_width(), button_bg.get_height()))
                
                # Pixel border
                border_size = 3
                pygame.draw.rect(button_bg, border_color, 
                                (0, 0, button_bg.get_width(), border_size))
                pygame.draw.rect(button_bg, border_color, 
                                (0, button_bg.get_height()-border_size, button_bg.get_width(), border_size))
                pygame.draw.rect(button_bg, border_color, 
                                (0, 0, border_size, button_bg.get_height()))
                pygame.draw.rect(button_bg, border_color, 
                                (button_bg.get_width()-border_size, 0, border_size, button_bg.get_height()))
                
                self.screen.blit(button_bg, 
                               (self.button_rects[i].centerx - button_bg.get_width() // 2,
                                self.button_rects[i].centery - button_bg.get_height() // 2))
            else:
                # Normal button
                color = (180, 180, 180)
            
            # Render button text
            text_key = (label, tuple(color))
            if text_key not in self.cached_buttons:
                text_surface = self.button_font.render(label, True, color)
                self.cached_buttons[text_key] = text_surface
            
            cached_surface = self.cached_buttons[text_key]
            rect = cached_surface.get_rect(center=self.button_rects[i].center)
            
            # Simple shadow
            shadow_surface = self.button_font.render(label, True, (0, 0, 0, 80))
            shadow_rect = shadow_surface.get_rect(center=(rect.centerx + 1, rect.centery + 1))
            self.screen.blit(shadow_surface, shadow_rect)
            
            self.screen.blit(cached_surface, rect)

        # --- Draw Particles ---
        self.draw_particles()

        # --- 8-bit HUD ---
        # Version
        self.screen.blit(self.version_text_cached, (10, 10))
        
        # FPS display
        fps_color = (100, 220, 100) if self.avg_fps > 50 else (220, 180, 100) if self.avg_fps > 30 else (220, 100, 100)
        fps_text = f"FPS:{int(self.avg_fps)}"
        fps_render = self.hud_font.render(fps_text, True, fps_color)
        fps_shadow = self.hud_font.render(fps_text, True, (0, 0, 0, 100))
        
        self.screen.blit(fps_shadow, (settings.WIDTH - 70, 11))
        self.screen.blit(fps_render, (settings.WIDTH - 71, 10))
        
        # Control hints (simple)
        if self.intro_stage == 2 and pygame.time.get_ticks() % 6000 < 3000:
            hint_text = "ARROWS/CLICK - ENTER TO SELECT"
            hint_render = self.hud_font.render(hint_text, True, (180, 180, 200, 120))
            hint_rect = hint_render.get_rect(center=(self.screen.get_width() // 2, 
                                                   self.screen.get_height() - 20))
            self.screen.blit(hint_render, hint_rect)