import pygame

class Kamera:
    def __init__(self, player, screen_width=1280, screen_height=800, zoom=1.0):
        self.player = player
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.zoom = zoom
        self.offset = pygame.Vector2(0, 0)

    def update(self):
        self.offset.x = self.player.rect.centerx - (self.screen_width  / (2 * self.zoom))
        self.offset.y = self.player.rect.centery - (self.screen_height / (2 * self.zoom))

    def apply(self, pos):
        return (pos[0] - self.offset.x, pos[1] - self.offset.y)
