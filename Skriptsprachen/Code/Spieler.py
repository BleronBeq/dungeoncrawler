import pygame
import math

#Spielerfigur
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, collision_tiles, tilewidth, tileheight):
        super().__init__()
        self.sprite_sheet = pygame.image.load("C:/Users/Admin/OneDrive/Desktop/VS-Code Uni/Python/Skriptsprachen/Sprites/Player.png").convert_alpha()
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

    def can_move(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
        tile_x = new_rect.centerx // self.tilewidth
        tile_y = new_rect.centery // self.tileheight
        return (tile_x, tile_y) not in self.collision_tiles

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
        else:
            self.anim_index = 1 

        self.image = self.frames[self.direction][self.anim_index]