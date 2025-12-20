# At the top of player.py
import pygame
import math
import random
from core.settings import *
from .projectile import MagicBolt  # <-- fixed


class Player:
    def __init__(self):
        # --- Load idle and attack sprites ---
        self.frames = [
            pygame.image.load("assets/sprites/Witch/player_idle.png").convert_alpha(),     # idle
            pygame.image.load("assets/sprites/Witch/player_idle2.png").convert_alpha(),    # blink
            pygame.image.load("assets/sprites/Witch/player_attack.png").convert_alpha()    # attack frame
        ]
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()

        # --- Position ---
        self.rect.centerx = SCREEN_WIDTH * 0.25
        self.rect.centery = SCREEN_HEIGHT * 0.5
        self.base_y = self.rect.centery  # reference for bobbing

        # --- Movement ---
        self.speed = 180
        self.vertical_speed = 160
        self.float_timer = 0.0
        self.idle_amplitude = 10
        self.idle_speed = 2.0

        # --- Blinking animation ---
        self.blink_timer = 0.0
        self.blink_interval = random.uniform(3, 5)
        self.is_blinking = False
        self.blink_duration = 0.15

        # --- Attack / Projectiles ---
        self.projectiles = []
        self.shoot_cooldown = 0.25  # seconds
        self.shoot_timer = 0.0
        self.attack_frame_timer = 0.1  # how long attack frame shows
        self.attack_frame_active = False
        self.attack_frame_counter = 0.0

    def update(self, dt):
        keys = pygame.key.get_pressed()
        moved = False

        # --- Horizontal movement ---
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed * dt / 1000
            moved = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed * dt / 1000
            moved = True

        # --- Vertical movement ---
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.vertical_speed * dt / 1000
            moved = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.vertical_speed * dt / 1000
            moved = True

        # --- Idle hover motion ---
        if not moved:
            self.float_timer += self.idle_speed * dt / 1000
            offset = math.sin(self.float_timer) * self.idle_amplitude
            self.rect.centery = self.base_y + offset
        else:
            self.base_y = self.rect.centery

        # --- Blinking animation ---
        self.blink_timer += dt / 1000
        if not self.is_blinking and self.blink_timer > self.blink_interval:
            self.is_blinking = True
            self.current_frame = 1
            self.blink_timer = 0
            self.blink_interval = random.uniform(3, 5)
        elif self.is_blinking and self.blink_timer > self.blink_duration:
            self.is_blinking = False
            self.current_frame = 0
            self.blink_timer = 0

        # --- Shooting / Attack frame ---
        self.shoot_timer += dt / 1000
        if keys[pygame.K_SPACE] and self.shoot_timer >= self.shoot_cooldown:
            self.shoot()
            self.shoot_timer = 0
            self.attack_frame_active = True
            self.attack_frame_counter = 0.0

        # --- Handle attack frame duration ---
        if self.attack_frame_active:
            self.attack_frame_counter += dt / 1000
            self.current_frame = 2  # attack sprite
            if self.attack_frame_counter > self.attack_frame_timer:
                self.attack_frame_active = False
                self.current_frame = 0  # back to idle

        # --- Update projectiles ---
        for bolt in self.projectiles:
            bolt.update(dt)
        self.projectiles = [b for b in self.projectiles if b.active]

        # --- Update current image ---
        self.image = self.frames[self.current_frame]

        # --- Keep within screen bounds ---
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def shoot(self):
        # Magic bolt appears in front of player
        bolt = MagicBolt(self.rect.centerx + self.rect.width // 2, self.rect.centery)
        self.projectiles.append(bolt)

    def draw(self, surface):
        # --- Soft glow ---
        glow_surface = pygame.Surface((self.rect.width + 40, self.rect.height + 40), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface,
            (255, 210, 160, 40),
            (glow_surface.get_width() // 2, glow_surface.get_height() // 2),
            glow_surface.get_width() // 2,
        )
        surface.blit(glow_surface, (self.rect.x - 20, self.rect.y - 20))

        # --- Draw player ---
        surface.blit(self.image, self.rect)

        # --- Draw projectiles ---
        for bolt in self.projectiles:
            bolt.draw(surface)
