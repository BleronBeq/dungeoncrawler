import pygame, sys
from settings import AssetLoader
from Spieler import Player
from Kamera import *
from ui import HealthBar
from menu import Menu
from map import TileMap
from items import ItemsManager

class Spiel:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Dungeon Crawler")
        self.zoom = 1.5
        self.screen = pygame.display.set_mode((1280, 800))
        self.clock = pygame.time.Clock()

        # Assetloader
        self.loader = AssetLoader(scale=(32, 32))

        # Map-Manager
        self.tilemap = TileMap()

        # Map laden
        self.map_path = self.loader.get_path("Maps", "Tiled-Map.tmx")
        self.load_map(self.map_path)

        # Healthbar
        self.health_bar = HealthBar(x=10, y=10, max_health=20, spacing=5, heart_size=(32, 32))

    def load_map(self, path):
        # Mapdaten laden
        self.tilemap.load(path)

        # Player erstellen (Spawn aus TileMap)
        spawn_x, spawn_y = self.tilemap.spawn
        self.player = Player(spawn_x, spawn_y, self.tilemap.collision_tiles, self.tilemap.tilewidth, self.tilemap.tileheight)
        self.player_group = pygame.sprite.Group(self.player)

        # Kamera
        self.kamera = Kamera(self.player, 1280, 800, self.zoom)

        # Exits referenzieren
        self.exits = self.tilemap.exits

        # Items/Türen-Manager
        self.items = ItemsManager(self.tilemap)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            dt = self.clock.get_time()

            # Spieler-Update
            self.player_group.update(keys, dt)

            # Items/Türen-Logik
            self.items.update(keys, self.player.rect)

            # Kamera
            self.kamera.update()

            # Zeichnen
            self.screen.fill((12, 19, 23))
            self.tilemap.draw(self.screen, self.kamera, self.zoom)

            # Schatten für den Spieler zeichnen
            offset = self.kamera.offset
            for sprite in self.player_group:
                sprite.draw_shadow(self.screen, offset, self.zoom)

            # Spieler zeichnen
            for sprite in self.player_group:
                scaled_sprite = pygame.transform.scale(
                    sprite.image,
                    (int(sprite.rect.width * self.zoom), int(sprite.rect.height * self.zoom))
                )
                screen_x, screen_y = self.kamera.apply((sprite.rect.x, sprite.rect.y))
                self.screen.blit(
                    scaled_sprite,
                    (screen_x * self.zoom, screen_y * self.zoom)
                )

            # HealthBar
            self.health_bar.update(self.player.health)
            self.health_bar.draw(self.screen)

            # Schlüsselanzahl anzeigen
            self.items.draw_key_ui(self.screen)

            # Exit-Check
            player_rect = self.player.rect
            for exit_obj in self.exits:
                if player_rect.colliderect(exit_obj["rect"]):
                    if keys[pygame.K_e]:
                        print("Exit getroffen! Nächste Map:", exit_obj["nextMap"])
                        if exit_obj["nextMap"]:
                            self.load_map(exit_obj["nextMap"])
                            break

            pygame.display.flip()
            self.clock.tick(60)

# Spiel starten
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 800))

    # Menü
    menu = Menu(screen)
    menu.run()

    spiel = Spiel()
    spiel.run()
