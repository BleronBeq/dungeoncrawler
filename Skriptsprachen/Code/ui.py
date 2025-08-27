
import pygame

class HealthBar:
    def __init__(self, x, y, max_health, full_heart_path, half_heart_path, empty_heart_path, spacing=5, heart_size=(32,32)):
        self.x = x
        self.y = y
        self.max_health = max_health
        self.current_health = max_health
        self.spacing = spacing

        # Volles Herz
        full_heart = pygame.image.load(full_heart_path).convert_alpha()
        self.full_heart = pygame.transform.smoothscale(full_heart, heart_size)

        # Halbes Herz
        half_heart = pygame.image.load(half_heart_path).convert_alpha()
        self.half_heart = pygame.transform.smoothscale(half_heart, heart_size)

        # Leeres Herz
        empty_heart = pygame.image.load(empty_heart_path).convert_alpha()
        self.empty_heart = pygame.transform.smoothscale(empty_heart, heart_size)

        self.heart_width = heart_size[0]
        self.heart_height = heart_size[1]

    def update(self, current_health):
        self.current_health = max(0, min(current_health, self.max_health))

    def draw(self, surface):
        for i in range(self.max_health):
            heart_x = self.x + i * (self.heart_width + self.spacing)

            hp_per_heart = 1
            if i < self.current_health:

                surface.blit(self.full_heart, (heart_x, self.y))
            elif self.current_health > i:
                surface.blit(self.half_heart, (heart_x, self.y))
            else:
                surface.blit(self.empty_heart, (heart_x, self.y))
