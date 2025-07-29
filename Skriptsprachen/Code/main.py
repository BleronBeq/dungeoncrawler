import pygame, sys
from Spieler import Player
from pytmx.util_pygame import load_pygame
from Kamera import *

class Spiel:
    def __init__(self):
        # Grundeinstellungen
        pygame.init()
        pygame.display.set_caption("Dungeon Crawler")
        self.zoom = 1.5 
        self.screen = pygame.display.set_mode((1280, 800))
        self.clock = pygame.time.Clock()

        # Map laden
        self.tmx_data = load_pygame("C:/Users/Admin/OneDrive/Desktop/VS-Code Uni/Python/Skriptsprachen/Maps/Tiled-Map.tmx")

        # Kollisionstiles sammeln
        self.collision_tiles = set()
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, '__iter__') and layer.name == 'Wände':
                for x, y, gid in layer:
                    if gid != 0:
                        self.collision_tiles.add((x, y))

        # Spieler erstellen
        self.player = Player(100, 100, self.collision_tiles, self.tmx_data.tilewidth, self.tmx_data.tileheight)
        self.player_group = pygame.sprite.Group(self.player)

        # Kamera erstellen
        self.kamera = Kamera(self.player)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill((0, 0, 0))  # Hintergrund

            # Kamera-Position updaten
            self.kamera.update()
            offset = self.kamera.camera.topleft

            # Tile-Layer
            for layer in self.tmx_data.visible_layers:
                if hasattr(layer, '__iter__'):
                    try:
                        for x, y, gid in layer:
                            image = self.tmx_data.get_tile_image_by_gid(gid)
                            if image:
                                # Skalieren
                                scaled_image = pygame.transform.scale(image, (self.tmx_data.tilewidth * self.zoom, self.tmx_data.tileheight * self.zoom))
                                screen_x = (x * self.tmx_data.tilewidth - offset[0]) * self.zoom
                                screen_y = (y * self.tmx_data.tileheight - offset[1]) * self.zoom
                                self.screen.blit(scaled_image, (screen_x, screen_y))
                    except Exception as e:
                        print(f"Fehler beim Zeichnen des Layers {getattr(layer, 'name', 'unbekannt')}: {e}")

            # Spieler updaten und zeichnen
            keys = pygame.key.get_pressed()
            dt = self.clock.get_time()
            self.player_group.update(keys, dt)
            for sprite in self.player_group:
                scaled_sprite = pygame.transform.scale(sprite.image, (sprite.rect.width * self.zoom, sprite.rect.height * self.zoom))
                self.screen.blit(scaled_sprite, ((sprite.rect.x - offset[0]) * self.zoom, (sprite.rect.y - offset[1]) * self.zoom))

            pygame.display.flip()
            self.clock.tick(60)


# Spiel starten
if __name__ == "__main__":
    spiel = Spiel()
    spiel.run()

