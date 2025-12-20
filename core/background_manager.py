import pygame, random, os, math

# -------------------------------------------------------------
# 🏔️ Safe Image Loader
# -------------------------------------------------------------
def safe_load_image(path, fallback_color=(150, 150, 150), size=(100, 100)):
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        # Apply slight pixelation for 8-bit style
        small = pygame.transform.scale(img, (img.get_width() // 2, img.get_height() // 2))
        return pygame.transform.scale(small, (img.get_width(), img.get_height()))
    else:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(fallback_color)
        print(f"[WARN] Missing image: {path}")
        return surf


# -------------------------------------------------------------
# 🏔️ 8-bit Style Hill/Mountain Range
# -------------------------------------------------------------
class MountainRange:
    def __init__(self, screen_height, num_hills=6):
        self.screen_height = screen_height
        self.num_hills = num_hills
        self.speed = 18
        self.hill_surfaces = []  # Cache for performance
        self.reset_positions()
        self.generate_hills()
        
    def reset_positions(self):
        self.width = 1400
        self.x1 = 0
        self.x2 = self.width
        
    def generate_hill_shape(self, width, height, hill_type):
        """Generate 8-bit style hill shapes with stepped curves"""
        points = []
        steps = 8  # Number of steps for 8-bit effect
        
        # Start at bottom left
        points.append((0, height))
        
        if hill_type == "gentle":
            # Gentle rolling hill with steps
            for step in range(1, steps + 1):
                x = (width * step) // steps
                if step < steps // 2:
                    y = height - (height * step * 3) // (steps * 4)
                else:
                    y = height - (height * (steps - step) * 3) // (steps * 4)
                points.append((x, y))
        elif hill_type == "steep":
            # Steep hill with sharp peak
            for step in range(1, steps + 1):
                x = (width * step) // steps
                if step < steps // 2:
                    y = height - (height * step * 2) // steps
                else:
                    y = height - (height * 2 * (steps - step)) // steps
                points.append((x, y))
        else:  # "rolling"
            # Rolling hills with multiple peaks
            for step in range(1, steps + 1):
                x = (width * step) // steps
                if step % 3 == 0:
                    y = height - (height * 2) // 3
                elif step % 3 == 1:
                    y = height - height // 2
                else:
                    y = height - (height * 3) // 4
                points.append((x, y))
        
        # End at bottom right
        points.append((width, height))
        
        return points
    
    def generate_hills(self):
        """Generate 8-bit style hills"""
        self.hills = []
        hill_width = self.width // self.num_hills
        self.hill_surfaces = []
        
        for i in range(self.num_hills):
            # Hill parameters with 8-bit color palette
            height = random.randint(160, 220)
            width = random.randint(hill_width - 60, hill_width + 60)
            x_offset = i * hill_width + random.randint(-30, 30)
            hill_type = random.choice(["gentle", "steep", "rolling"])
            
            # 8-bit color palette (limited colors)
            base_colors = [
                (60, 100, 80),    # Dark green
                (80, 120, 100),   # Medium green
                (100, 140, 120),  # Light green
                (70, 90, 110),    # Blue-gray
            ]
            
            # Detail colors (rocks, trees)
            detail_colors = [
                (90, 70, 50),     # Brown
                (110, 90, 70),    # Light brown
                (80, 100, 80),    # Moss
                (120, 100, 80),   # Tan
            ]
            
            base_color = random.choice(base_colors)
            detail_color = random.choice(detail_colors)
            
            # Generate hill shape
            shape_points = self.generate_hill_shape(width, height, hill_type)
            
            # Create cached surface
            hill_surface = self.create_hill_surface(width, height, shape_points, 
                                                   base_color, detail_color)
            
            self.hills.append({
                'x_offset': x_offset,
                'height': height,
                'width': width,
                'surface': hill_surface,
                'shape_points': shape_points
            })
    
    def create_hill_surface(self, width, height, shape_points, base_color, detail_color):
        """Create 8-bit style hill surface"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw hill with stepped edges (8-bit style)
        for i in range(len(shape_points) - 1):
            x1, y1 = shape_points[i]
            x2, y2 = shape_points[i + 1]
            
            # Create stepped line for 8-bit effect
            steps = max(2, abs(x2 - x1) // 10)
            for step in range(steps):
                sx1 = x1 + (x2 - x1) * step // steps
                sx2 = x1 + (x2 - x1) * (step + 1) // steps
                sy1 = y1 + (y2 - y1) * step // steps
                sy2 = y1 + (y2 - y1) * step // steps  # Keep y constant for step
                
                # Draw step with slight color variation
                step_color = (
                    max(0, base_color[0] - step * 2),
                    max(0, base_color[1] - step * 2),
                    max(0, base_color[2] - step * 2)
                )
                pygame.draw.line(surface, step_color, (sx1, sy1), (sx2, sy2), 3)
        
        # Add 8-bit style details (pixelated trees/rocks)
        num_details = random.randint(2, 5)
        for _ in range(num_details):
            detail_x = random.randint(10, width - 10)
            detail_y = random.randint(height // 3, height - 20)
            
            # Simple pixel tree/rock shapes
            if random.random() > 0.5:
                # Tree (simple pixel shape)
                pygame.draw.rect(surface, detail_color, 
                               (detail_x - 3, detail_y - 8, 6, 8))
                pygame.draw.rect(surface, (40, 80, 40),
                               (detail_x - 4, detail_y - 12, 8, 4))
            else:
                # Rock (simple pixel shape)
                pygame.draw.rect(surface, detail_color,
                               (detail_x - 4, detail_y - 4, 8, 8))
        
        return surface
    
    def update_and_draw(self, screen, dt):
        dt_sec = dt / 1000.0
        screen_w, screen_h = screen.get_size()
        
        # Update positions
        self.x1 -= self.speed * dt_sec
        self.x2 -= self.speed * dt_sec
        
        # Wrap around
        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
            self.generate_hills()
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width
            self.generate_hills()
        
        # Draw hills
        self.draw_hill_range(screen, self.x1, screen_h)
        self.draw_hill_range(screen, self.x2, screen_h)
    
    def draw_hill_range(self, screen, x_offset, screen_h):
        """Draw hills with 8-bit style shadows"""
        for hill in self.hills:
            x = x_offset + hill['x_offset']
            y = screen_h - hill['height']
            
            # Draw hill
            screen.blit(hill['surface'], (x, y))
            
            # Simple 8-bit shadow
            shadow = pygame.Surface((hill['width'], 15), pygame.SRCALPHA)
            for i in range(15):
                alpha = int(40 * (1 - i/15))
                pygame.draw.line(shadow, (0, 0, 0, alpha),
                               (0, i), (hill['width'], i))
            screen.blit(shadow, (x, screen_h - 15))


# -------------------------------------------------------------
# 🏔️ Parallax Layer (8-bit Optimized)
# -------------------------------------------------------------
class ParallaxLayer:
    def __init__(self, image_path, speed, stretch=False, scale_factor=1.0, align_bottom=False):
        self.image = safe_load_image(image_path)
        self.speed = speed
        self.stretch = stretch
        self.scale_factor = scale_factor
        self.align_bottom = align_bottom
        self.cached_surface = None
        self.reset_positions()

    def reset_positions(self):
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x1 = 0
        self.x2 = self.width

    def update_and_draw(self, screen, dt):
        dt_sec = dt / 1000.0
        self.x1 -= self.speed * dt_sec
        self.x2 -= self.speed * dt_sec

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

        if self.stretch:
            screen_w, screen_h = screen.get_size()
            if (self.cached_surface is None or 
                self.cached_surface.get_size() != (screen_w, int(self.height * self.scale_factor))):
                # Apply 8-bit pixelation to stretched image
                temp = pygame.transform.scale(
                    self.image, (screen_w // 2, int(self.height * self.scale_factor) // 2)
                )
                self.cached_surface = pygame.transform.scale(
                    temp, (screen_w, int(self.height * self.scale_factor))
                )
            
            y_pos = screen_h - self.cached_surface.get_height() if self.align_bottom else 0
            screen.blit(self.cached_surface, (self.x1, y_pos))
            screen.blit(self.cached_surface, (self.x2, y_pos))
        else:
            y_pos = screen.get_height() - self.height if self.align_bottom else 0
            screen.blit(self.image, (self.x1, y_pos))
            screen.blit(self.image, (self.x2, y_pos))


# -------------------------------------------------------------
# 🏝️ 8-bit Floating Island
# -------------------------------------------------------------
class FloatingIsland:
    def __init__(self, image_path, speed_range=(0.5, 1.2)):
        self.image_path = image_path
        self.speed_range = speed_range
        self.shadow_surface = None
        self.reset()

    def reset(self):
        self.image = safe_load_image(self.image_path)
        scale_factor = random.uniform(0.8, 1.0)  # Smaller for 8-bit
        w = int(self.image.get_width() * scale_factor)
        h = int(self.image.get_height() * scale_factor)
        
        # Apply 8-bit pixelation
        small = pygame.transform.scale(self.image, (w // 2, h // 2))
        self.image = pygame.transform.scale(small, (w, h))
        
        self.x = random.randint(900, 1500)
        self.y = random.randint(100, 220)  # Higher up
        self.speed = random.uniform(*self.speed_range)
        self.vertical_float_time = random.uniform(0, 6.28)
        
        # Create 8-bit style shadow
        if self.shadow_surface is None or self.shadow_surface.get_size() != (w + 10, h // 3):
            self.shadow_surface = pygame.Surface((w + 10, h // 3), pygame.SRCALPHA)
            # Simple oval shadow
            shadow_color = (0, 0, 0, 40)
            pygame.draw.ellipse(self.shadow_surface, shadow_color, (0, 0, w + 10, h // 3))

    def update_and_draw(self, screen, dt):
        dt_sec = dt / 1000.0
        self.x -= self.speed * dt_sec * 100
        self.vertical_float_time += dt_sec * 0.5
        y_offset = 4 * math.sin(self.vertical_float_time)  # Less movement

        if self.x + self.image.get_width() < 0:
            self.reset()

        # Draw shadow
        shadow_y = self.y + self.image.get_height() - 8
        screen.blit(self.shadow_surface, (self.x - 5, shadow_y))
        
        # Draw island
        screen.blit(self.image, (self.x, self.y + y_offset))


# -------------------------------------------------------------
# 🌬️ 8-bit Wind Particles
# -------------------------------------------------------------
class WindParticle:
    def __init__(self, width, height):
        self.streak_cache = {}
        self.reset(width, height)

    def reset(self, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.speed = random.uniform(15, 30)  # Slower for 8-bit
        self.alpha = random.randint(80, 120)
        self.length = random.randint(4, 8)  # Shorter
        
        if self.length not in self.streak_cache:
            surf = pygame.Surface((self.length, 1), pygame.SRCALPHA)  # Thinner
            for i in range(self.length):
                alpha = int(self.alpha * (1 - i/self.length))
                pygame.draw.line(surf, (255, 255, 255, alpha), 
                               (i, 0), (i, 1))
            self.streak_cache[self.length] = surf

    def update_and_draw(self, screen, dt):
        dt_sec = dt / 1000.0
        self.x -= self.speed * dt_sec

        if self.x < -self.length:
            self.x = screen.get_width() + 10
            self.y = random.randint(0, screen.get_height())

        screen.blit(self.streak_cache[self.length], (self.x, self.y))


# -------------------------------------------------------------
# ✨ 8-bit Glow Particles
# -------------------------------------------------------------
class GlowParticle:
    def __init__(self, width, height):
        self.glow_cache = {}
        self.reset(width, height)

    def reset(self, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.size = random.randint(2, 4)  # Smaller
        self.speed = random.uniform(8, 15)
        # Limited 8-bit color palette
        self.color = random.choice([
            (200, 220, 255),  # Light blue
            (255, 240, 200),  # Warm white
            (220, 200, 255),  # Lavender
        ])
        self.alpha = random.randint(80, 140)
        self.float_time = random.uniform(0, 6.28)
        self.glow_size = self.size + 2  # Smaller glow
        
        cache_key = (self.size, self.glow_size, self.alpha)
        if cache_key not in self.glow_cache:
            glow_surface = pygame.Surface((self.glow_size, self.glow_size), pygame.SRCALPHA)
            # Simple square for 8-bit style
            pygame.draw.rect(glow_surface, (*self.color, self.alpha),
                           (0, 0, self.glow_size, self.glow_size))
            self.glow_cache[cache_key] = glow_surface

    def update_and_draw(self, screen, dt):
        dt_sec = dt / 1000.0
        self.x -= self.speed * dt_sec
        self.float_time += dt_sec * 0.3  # Slower
        y_offset = 2 * math.sin(self.float_time)

        if self.x < -self.glow_size:
            self.reset(*screen.get_size())
            self.x = screen.get_width() + self.glow_size

        cache_key = (self.size, self.glow_size, self.alpha)
        screen.blit(self.glow_cache[cache_key], 
                   (self.x - self.size//2, self.y + y_offset - self.size//2))


# -------------------------------------------------------------
# 🌞 8-bit Style Sun
# -------------------------------------------------------------
class Sun:
    def __init__(self, x, y, radius=70):  # Smaller for 8-bit
        self.x = x
        self.y = y
        self.radius = radius
        self.pulse_timer = 0.0
        self.glow_surface = None
        self.core_surface = None
        
    def update(self, dt):
        self.pulse_timer += dt * 0.0008  # Slower pulse
        
        pulse = 0.5 + 0.5 * math.sin(self.pulse_timer)
        
        if self.glow_surface is None:
            self.create_sun_surfaces(pulse)
        
    def create_sun_surfaces(self, pulse):
        """Create 8-bit style sun surfaces"""
        # Simple glow (concentric squares for 8-bit)
        self.glow_surface = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        
        # Create pixelated glow effect
        glow_colors = [
            (255, 220, 120, 60),
            (255, 200, 100, 90),
            (255, 180, 80, 120)
        ]
        
        for i, (color, size_factor) in enumerate([(glow_colors[0], 1.5), 
                                                 (glow_colors[1], 1.2), 
                                                 (glow_colors[2], 1.0)]):
            size = int(self.radius * size_factor * (0.9 + 0.1 * pulse))
            # Draw square for 8-bit style
            rect = pygame.Rect(
                self.glow_surface.get_width()//2 - size//2,
                self.glow_surface.get_height()//2 - size//2,
                size, size
            )
            pygame.draw.rect(self.glow_surface, color, rect)
        
        # Sun core (simple square)
        self.core_surface = pygame.Surface((self.radius, self.radius), pygame.SRCALPHA)
        core_color = (255, 240, 180, 255)
        pygame.draw.rect(self.core_surface, core_color, (0, 0, self.radius, self.radius))
        
        # Add pixel grid effect
        for x in range(0, self.radius, 4):
            for y in range(0, self.radius, 4):
                if (x + y) % 8 == 0:
                    bright = (min(255, core_color[0] + 20),
                            min(255, core_color[1] + 20),
                            min(255, core_color[2] + 20),
                            255)
                    pygame.draw.rect(self.core_surface, bright, (x, y, 2, 2))

    def draw(self, screen):
        if self.glow_surface is None:
            self.update(16)
            
        # Draw glow
        screen.blit(self.glow_surface, 
                   (self.x - self.glow_surface.get_width() // 2, 
                    self.y - self.glow_surface.get_height() // 2),
                   special_flags=pygame.BLEND_RGBA_ADD)
        
        # Draw core
        if self.core_surface:
            screen.blit(self.core_surface,
                       (self.x - self.core_surface.get_width() // 2,
                        self.y - self.core_surface.get_height() // 2),
                       special_flags=pygame.BLEND_RGBA_ADD)


# -------------------------------------------------------------
# 🌅 8-bit Background Manager
# -------------------------------------------------------------
class BackgroundManager:
    def __init__(self, screen):
        self.screen = screen
        self.time = 0.0
        self.gradient_cache = None
        self.gradient_timer = 0

        # 🌞 Add 8-bit sun
        self.sun = Sun(x=180, y=150, radius=60)

        # Layers with 8-bit style
        self.layers = [
            ParallaxLayer("assets/backgrounds/clouds_far.png", speed=6, stretch=False),
            ParallaxLayer("assets/backgrounds/fl_island1.png", speed=10, stretch=False),
        ]
        
        # Add 8-bit hill range
        self.mountain_range = MountainRange(screen.get_height(), num_hills=4)

        # Reduced particle counts for 8-bit
        self.islands = [FloatingIsland("assets/backgrounds/fl_island1.png") for _ in range(2)]
        self.wind_particles = [WindParticle(*screen.get_size()) for _ in range(8)]
        self.glow_particles = [GlowParticle(*screen.get_size()) for _ in range(6)]
        
        # 8-bit color palette for sky
        self.top_sky_color = (70, 110, 180)    # Deep blue
        self.mid_sky_color = (120, 160, 220)   # Medium blue
        self.bottom_sky_color = (180, 200, 240) # Light blue

    def create_gradient_surface(self, width, height):
        """Create 8-bit style gradient with limited colors"""
        gradient = pygame.Surface((width, height))
        
        # Create stepped gradient for 8-bit effect
        steps = 8
        step_height = height // steps
        
        for step in range(steps):
            # Calculate color for this step
            blend = step / steps
            r = int(self.top_sky_color[0] * (1 - blend) + self.bottom_sky_color[0] * blend)
            g = int(self.top_sky_color[1] * (1 - blend) + self.bottom_sky_color[1] * blend)
            b = int(self.top_sky_color[2] * (1 - blend) + self.bottom_sky_color[2] * blend)
            
            # Quantize colors for 8-bit effect
            r = (r // 32) * 32
            g = (g // 32) * 32
            b = (b // 32) * 32
            
            step_color = (r, g, b)
            
            # Draw step
            y_start = step * step_height
            y_end = min((step + 1) * step_height, height)
            pygame.draw.rect(gradient, step_color, (0, y_start, width, y_end - y_start))
        
        return gradient

    def update_and_draw(self, dt):
        dt_sec = dt / 1000.0
        self.time += dt_sec
        self.gradient_timer += dt_sec
        
        # Update sun
        self.sun.update(dt)
        
        # Update gradient cache periodically
        if (self.gradient_cache is None or 
            self.gradient_timer > 2.0 or  # Update less frequently
            self.gradient_cache.get_size() != self.screen.get_size()):
            
            self.gradient_cache = self.create_gradient_surface(
                self.screen.get_width(), 
                self.screen.get_height()
            )
            self.gradient_timer = 0
        
        # Draw background
        self.screen.blit(self.gradient_cache, (0, 0))
        
        # ☀️ Draw 8-bit sun
        self.sun.draw(self.screen)

        # Draw layers
        for layer in self.layers:
            layer.update_and_draw(self.screen, dt)
            
        # Draw hills
        self.mountain_range.update_and_draw(self.screen, dt)
            
        # Draw particles
        for island in self.islands:
            island.update_and_draw(self.screen, dt)
        for p in self.wind_particles:
            p.update_and_draw(self.screen, dt)
        for g in self.glow_particles:
            g.update_and_draw(self.screen, dt)