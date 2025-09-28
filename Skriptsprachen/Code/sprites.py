import pygame
import random
import math
from ui import HealthBar
from settings import AssetLoader
#Spielerfigur
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, collision_tiles, tilewidth, tileheight):
        super().__init__()
        loader = AssetLoader()
        self.sprite_sheet = loader.load_image("Sprites", "Player.png")
        self.frames = self.load_frames()
        self.direction = "down"
        self.anim_index = 0
        self.image = self.frames[self.direction][self.anim_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 2.5
        self.anim_timer = 0
        self.collision_tiles = collision_tiles
        self.tilewidth = tilewidth
        self.tileheight = tileheight
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.health = 20  # Aktuelle Gesundheit
        self.max_health = 20  # Maximale Gesundheit

        self.is_dead = False

        # Sound Boden
        self.step_sound = [
            pygame.mixer.Sound("Audio/footstep_concrete1.ogg"), #Quelle von der Soundeffekte: https://kenney.itch.io/kenney-game-assets
            pygame.mixer.Sound("Audio/footstep_concrete2.ogg"),
            pygame.mixer.Sound("Audio/footstep_concrete3.ogg"),
            pygame.mixer.Sound("Audio/footstep_concrete4.ogg"),
            pygame.mixer.Sound("Audio/footstep_concrete5.ogg")
            ]

        for sound in self.step_sound:
            sound.set_volume(0.5)

        self.hit_sound = pygame.mixer.Sound("Audio/hit1.ogg") #Quelle des Sounds: https://kenney.itch.io/kenney-game-assets
        self.hit_sound.set_volume(0.5)

        self.death_sound = pygame.mixer.Sound("Audio/elden-ring-death.mp3") #Quelle des Sounds: https://www.youtube.com/@bond_factory/videos
        self.death_sound.set_volume(0.5)

        self.step_timer = 0

    def can_move(self, dx, dy): # TODO: Kollision mit Wänden verändern.
        new_rect = self.rect.move(dx, dy)
        tile_x = new_rect.centerx // self.tilewidth
        tile_y = new_rect.centery // self.tileheight
        return (tile_x, tile_y) not in self.collision_tiles
    
    def take_damage(self,amount: int):
        if self.health > 0:
            self.hit_sound.play()

        self.health = max(0, self.health - int(amount))

        if self.health == 0 and not self.is_dead:
            self.is_dead = True
            self.death_sound.play()

    def load_frames(self):
        directions = ["down", "left", "right", "up"] # Reihenfolge vom Spieler Sprite-Sheet
        frames = {direction: [] for direction in directions}
        title_width = 32
        title_height = 32
        for row, dir in enumerate(directions):
            for col in range(3):
                rect = pygame.Rect(col * title_width, row * title_height, title_width, title_height)
                image = self.sprite_sheet.subsurface(rect)
                frames[dir].append(image)
        return frames
    
    # Schatten zeichnen unter dem Spieler
    def draw_shadow(self, surface, offset, zoom):
        shadow_w = int(self.rect.width * 0.7 * zoom)
        shadow_h = int(self.rect.height * 0.25 * zoom)
        shadow_surface = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 90), shadow_surface.get_rect())

        # Position unter den Füßen
        screen_x = (self.rect.centerx - offset[0]) * zoom - shadow_w // 2
        screen_y = (self.rect.bottom - offset[1]) * zoom - shadow_h // 2 + 5

        surface.blit(shadow_surface, (screen_x, screen_y))

    def draw(self,surface):
        self.draw_shadow(surface)
        surface.blit(self.image, self.rect)
    

    def update(self, keys, dt):
        dx, dy = 0, 0
        if keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_s]:
            dy += self.speed
        if keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_d]:
            dx += self.speed

        moved = False
        # Richtung für Animation setzen
        if dy < 0:
            self.direction = 'up'
        elif dy > 0:
            self.direction = 'down'
        elif dx < 0:
            self.direction = 'left'
        elif dx > 0:
            self.direction = 'right'

        # Normieren bei diagonaler Bewegung
        if dx != 0 and dy != 0:
            dx /= math.sqrt(2)
            dy /= math.sqrt(2)

        if dx != 0 or dy != 0:
            if self.can_move(dx, dy):
                self.pos_x += dx
                self.pos_y += dy
                self.rect.x = round(self.pos_x)
                self.rect.y = round(self.pos_y)
                moved = True

        if moved:
            self.anim_timer += dt
            if self.anim_timer > 150:
                self.anim_index = (self.anim_index + 1) % 3
                self.anim_timer = 0

                self.step_timer += dt
                if self.step_timer > 30:
                    sound = random.choice(self.step_sound).play()
                    self.step_timer = 0
        else:
            self.anim_index = 1 

        self.image = self.frames[self.direction][self.anim_index]


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, player, collision_tiles, tilewidth, tileheight, speed=1.5):
        super().__init__()
        loader = AssetLoader()
        enemy_sheet = loader.load_image("Sprites", "Enemy.png")
        self.frames = self.load_frames(enemy_sheet, cols=5, rows=4, margin=0, spacing=0, trim=1)
        self.direction_str = "down"
        self.frames_index = 0.0
        self.animation_speed = 8.0
        self.image = self.frames[self.direction_str][0]

        self.rect = self.image.get_rect(center=pos)
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

        self.player = player
        self.look_vec = pygame.Vector2()
        self.speed = speed

        self.collision_tiles = collision_tiles
        self.tilewidth = tilewidth
        self.tileheight = tileheight

        self.health = 5
        self.attack_damage = 1
        self.attack_cooldown = 800
        self._attack_timer_ms = 0

    def spawn_enemy(enemy_group, player, collision_tiles, tilewidth, tileheight, max_enemies=5,spawn_area=(200,200,800,600)):
        while len(enemy_group) < max_enemies:
            x = random.randint(spawn_area[0], spawn_area[0] + spawn_area[2])
            y = random.randint(spawn_area[1], spawn_area[1] + spawn_area[3])
            enemy = Enemy((x, y), player, collision_tiles, tilewidth, tileheight)
            enemy_group.add(enemy)

    def animate(self, dt):
        frame_list = self.frames[self.direction_str]
        self.frames_index += self.animation_speed * (dt / 1000.0)
        self.image = frame_list[int(self.frames_index) % len(frame_list)]

    def can_move(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
        tile_x = new_rect.centerx // self.tilewidth
        tile_y = new_rect.centery // self.tileheight
        return (tile_x, tile_y) not in self.collision_tiles
    
    def take_damage(self, amount: int):
        self.health = max(0, self.health - int(amount))
        if self.health == 0:
            self.kill()

    def attack_player(self, dt):
        self._attack_timer_ms = max(0, self._attack_timer_ms - dt)
        if self._attack_timer_ms == 0 and self.rect.colliderect(self.player.rect):
            self.player.take_damage(self.attack_damage)
            self._attack_timer_ms = self.attack_cooldown


    def load_frames(self, sheet, cols=5, rows=4, margin=0, spacing=0, trim=0):
        directions = ["down", "left", "right", "up"] # Reihenfolge vom Enemy Sprite-Sheet
        frames = {direction: [] for direction in directions}

        # Größe der Einzelbilder
        total_w, total_h = sheet.get_width(), sheet.get_height()
        frame_w = (total_w - 2 * margin - (cols - 1) * spacing) // cols
        frame_h = (total_h - 2 * margin - (rows - 1) * spacing) // rows

        for row, dir_name in enumerate(directions):
            for col in range(cols):
                x = margin + col * (frame_w + spacing) + trim
                y = margin + row * (frame_h + spacing) + trim
                w = max(1, frame_w - 2 * trim)
                h = max(1, frame_h - 2 * trim)
                rect = pygame.Rect(x, y, w, h)

                rect = rect.clip(pygame.Rect(0, 0, total_w, total_h))
                img = sheet.subsurface(rect).convert_alpha()
                img.set_colorkey((255, 0, 255))  # Magenta transparent
                frames[dir_name].append(img)
        return frames

    def move(self, dt):
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)

        direction = player_pos - enemy_pos
        if direction.length_squared() > 0:
            direction = direction.normalize()
        else:
            direction = pygame.Vector2()

        dx = direction.x * self.speed
        dy = direction.y * self.speed

        # Richtung für Animation bestimmen
        prev_dir = self.direction_str
        if abs(dx) > abs(dy):
            self.direction_str = 'right' if dx > 0 else 'left'
        else:
            if dy != 0:
                self.direction_str = 'down' if dy > 0 else 'up'
        if self.direction_str != prev_dir:
            self.frames_index = 0.0

        moved = False
        if dx != 0 and self.can_move(dx, 0):
            self.pos_x += dx
            moved = True
        if dy != 0 and self.can_move(0, dy):
            self.pos_y += dy
            moved = True

        if moved:
            self.rect.x = round(self.pos_x)
            self.rect.y = round(self.pos_y)

    def update(self, dt):
        self.move(dt)
        self.animate(dt)
        self.attack_player(dt)
