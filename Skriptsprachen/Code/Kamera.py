from main import pygame

class Kamera(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.camera = pygame.Rect(0, 0, 1280, 800)  # Passe an Fenstergröße an
        self.deadzone = 30  # Abstand vom Rand, bevor die Kamera folgt

    def update(self):
        # Bildschirmmitte
        cam_cx = self.camera.width // 2
        cam_cy = self.camera.height // 2

        # Deadzone-Rechteck um die Bildschirmmitte
        dz_left = self.camera.x + cam_cx - self.deadzone
        dz_right = self.camera.x + cam_cx + self.deadzone
        dz_top = self.camera.y + cam_cy - self.deadzone
        dz_bottom = self.camera.y + cam_cy + self.deadzone

        px, py = self.player.rect.center

        # Kamera nur bewegen, wenn Spieler Deadzone verlässt
        if px < dz_left:
            self.camera.x -= dz_left - px
        elif px > dz_right:
            self.camera.x += px - dz_right
        if py < dz_top:
            self.camera.y -= dz_top - py
        elif py > dz_bottom:
            self.camera.y += py - dz_bottom

        # Kamera immer auf Spieler zentrieren
        self.camera.center = self.player.rect.center
        # Begrenzung der Kamera innerhalb der Spielwelt (hier Beispielgröße, ggf. anpassen)
        self.camera.clamp_ip(pygame.Rect(0, 0, 1920, 1920))

    def apply(self, entity):
        return entity.rect.move(-self.camera.x, -self.camera.y)

    def draw(self, surface):
        for sprite in self.player.groups():
            if hasattr(sprite, 'rect'):
                surface.blit(sprite.image, self.apply(sprite))