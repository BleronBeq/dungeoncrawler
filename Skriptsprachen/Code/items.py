from unittest import loader
import pygame
from settings import AssetLoader
from math import atan2, degrees
class ItemsManager:

    def __init__(self, tilemap, player, enemies):
        self.set_map(tilemap)
        self.key_count = 0
        self._prev_e_pressed = False

        self.enemies = enemies
        self.sword = Sword(player, enemies, scale=0.75)

        self.door_sound = pygame.mixer.Sound("Audio/doorOpen.ogg")
        self.door_sound.set_volume(0.5)

    def set_map(self, tilemap):
        self.tilemap = tilemap
        self.key_count = 0
        self._prev_e_pressed = False

        self._key_icon = None
        self._key_icon_placeholder = None

        try:
            loader = AssetLoader(scale=(32,32))
            self._key_icon_placeholder = loader.load_image("Sprites", "key_placeholder.png")
        except Exception:
            self._key_icon_placeholder = None

        try:
            loader = AssetLoader(scale=(48, 48))
            self._key_icon = loader.load_image("Sprites", "key.png")
        except Exception:
            self._key_icon = None

        self._ui_font = pygame.font.SysFont(None, 22)

    def update(self, keys, player_rect, mouse_pos):
        for pos, rect in list(self.tilemap.key_rects.items()):
            if pos in self.tilemap.collected_keys:
                continue
            if player_rect.colliderect(rect):
                self.tilemap.collect_key(pos)
                self.key_count += 1

        e_pressed = keys[pygame.K_e]
        e_edge = e_pressed and not self._prev_e_pressed
        self._prev_e_pressed = e_pressed

        # Türen öffnen
        if e_edge and self.key_count > 0:
            for pos, rect in self.tilemap.door_rects.items():
                if pos in self.tilemap.open_doors:
                    continue
                if player_rect.colliderect(rect):
                    # Tür öffnen
                    self.tilemap.open_door(pos)
                    self.key_count -= 1
                    self.door_sound.play()
                    break

        # Schwert 
        if keys[pygame.K_SPACE]:
            self.sword.attack()
        self.sword.rotate_sword(mouse_pos)
        self.sword.update()

    def draw_sword(self, surface, kamera=None, zoom=1.0):
        self.sword.draw(surface, kamera, zoom)

    def draw_key_ui(self, surface, margin=(10, 10), color=(240, 240, 240)):

        icon = self._key_icon if self.key_count > 0 else self._key_icon_placeholder
        if icon is None:
            icon = self._key_icon or self._key_icon_placeholder
        if icon is None:
            return

        x = surface.get_width() - icon.get_width() - margin[0]
        y = margin[1]
        surface.blit(icon, (x, y))

class Sword(pygame.sprite.Sprite):
    def __init__(self, player, enemies, offset_radius=0, scale=0.75):
        super().__init__()
        self.player = player
        self.enemies = enemies
        self.render_scale = scale
        loader = AssetLoader()
        self.sprite_sheet = loader.load_image("Sprites", "sword.png")

        self.attack_sound = pygame.mixer.Sound("Audio/swish_2.wav")
        self.attack_sound.set_volume(0.5)

        sheet_width, sheet_height = self.sprite_sheet.get_size()
        self.frame_width = sheet_width
        self.frame_height = sheet_height // 5
        self.num_frames = 5

        self.frames = []
        for i in range(self.num_frames):
            rect = pygame.Rect(0, i * self.frame_height, self.frame_width, self.frame_height)
            frame = self.sprite_sheet.subsurface(rect)
            # Schwert-Bild
            frame_centered = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
            frame_centered.blit(frame, (-0, 0)) 
            self.frames.append(frame_centered)

        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=self.player.rect.center)

        self.attacking = False
        self.counter = 0
        self.animation_speed = 5
        self.angle = 0

        self.damage = 2
        self._already_hit_ids = set()

        # Abstand, wie weit das Schwert neben dem Spieler sitzen soll
        self.offset_radius = offset_radius or (max(self.player.rect.width, self.player.rect.height) // 1 + 10)
        # Blickrichtung-Einheitsvektor
        self.look_dir = pygame.Vector2(1, 0)

    def attack(self):
        if not self.attacking:
            self.attacking = True
            self.index = 0
            self.counter = 0
            self._already_hit_ids.clear()
            if hasattr(self, "attack_sound"):
                self.attack_sound.play()

    def damage_enemies(self):
        if not self.attacking or self.enemies is None:
            return
        for enemy in list(self.enemies):
            if hasattr(enemy, "rect") and self.rect.colliderect(enemy.rect):
                eid = id(enemy)
                if eid in getattr(self, "_already_hit_ids", set()):
                    continue
                if hasattr(enemy, "take_damage"):
                    enemy.take_damage(self.damage)
                else:
                    enemy.health = max(0, getattr(enemy, "health", 0) - self.damage)
                    if enemy.health <= 0 and hasattr(enemy, "kill"):
                        enemy.kill()
                if not hasattr(self, "_already_hit_ids"):
                    self._already_hit_ids = set()
                self._already_hit_ids.add(eid)


    def rotate_sword(self, mouse_pos):
        # Winkel von Spieler zur Maus
        direction = pygame.Vector2(mouse_pos) - pygame.Vector2(self.player.rect.center)
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
        else:
            direction = direction.normalize()
        self.look_dir = direction
        self.angle = degrees(atan2(-direction.y, direction.x))

    def update(self):
        # Animation
        if self.attacking:
            self.damage_enemies()
            self.counter += 1
            if self.counter >= self.animation_speed:
                self.counter = 0
                self.index += 1
                if self.index >= self.num_frames:
                    self.index = 0
                    self.attacking = False

        # Rotation
        self.image = pygame.transform.rotozoom(self.frames[self.index], self.angle, self.render_scale)
        target_center = pygame.Vector2(self.player.rect.center) + self.look_dir * self.offset_radius
        self.rect = self.image.get_rect(center=(int(target_center.x), int(target_center.y)))

    def draw(self, surface, kamera=None, zoom=1.0):
        if zoom != 1.0:
            scaled = pygame.transform.scale(
                self.image,
                (int(self.rect.width * zoom), int(self.rect.height * zoom))
            )
        else:
            scaled = self.image

        if kamera is not None:
            screen_x, screen_y = kamera.apply((self.rect.x, self.rect.y))
            surface.blit(scaled, (screen_x * zoom, screen_y * zoom))
        else:
            surface.blit(scaled, self.rect.topleft)
