import pygame, sys
from Spieler import Player
from pytmx.util_pygame import load_pygame
from Kamera import *
from ui import HealthBar
from menu import Menu

class Spiel:
    def __init__(self, map_path="C:/Users/Admin/OneDrive/Desktop/VS-Code Uni/Python/Skriptsprachen/Maps/Tiled-Map.tmx"):
        pygame.init()
        pygame.display.set_caption("Dungeon Crawler")
        self.zoom = 1.5
        self.screen = pygame.display.set_mode((1280, 800))
        self.clock = pygame.time.Clock()
        self.map_path = map_path
        self.load_map(self.map_path)
        self.health_bar = HealthBar(10, 10, 200, 20, max_health=100)
        self.health_bar.update(self.player.health)
        self.health_bar.draw(self.screen)

    def load_map(self, path):
        self.tmx_data = load_pygame(path)
        # Kollisionstiles sammeln
        self.collision_tiles = set()
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, '__iter__') and getattr(layer, 'name', '') == 'Wände':
                for x, y, gid in layer:
                    if gid != 0:
                        self.collision_tiles.add((x, y))

        # Spawn suchen
        spawn_x, spawn_y = 100, 100
        for layer in self.tmx_data.layers:
            if getattr(layer, 'name', '') == "playerSpawn":
                for obj in layer:
                    spawn_x, spawn_y = obj.x, obj.y
                    break

        self.player = Player(spawn_x, spawn_y, self.collision_tiles, self.tmx_data.tilewidth, self.tmx_data.tileheight)
        self.player_group = pygame.sprite.Group(self.player)
        self.kamera = Kamera(self.player)

        # Exits sammeln (Objektgruppe "exit")
        self.exits = []
        for layer in self.tmx_data.layers:
            if getattr(layer, 'name', '') == "exit":
                for obj in layer:
                    next_map = None
                    for prop in getattr(obj, 'properties', {}):
                        if prop == "nextMap":
                            next_map = obj.properties[prop]
                            if next_map:
                                import os
                                next_map = os.path.join(os.path.dirname(path), next_map)
                    self.exits.append({
                        "rect": pygame.Rect(obj.x, obj.y, obj.width, obj.height),
                        "nextMap": next_map
                    })

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill((0, 0, 0))
            self.kamera.update()
            offset = self.kamera.camera.topleft
            # Tile-Layer zeichnen
            for layer in self.tmx_data.visible_layers:
                if layer.__class__.__name__ == "TiledTileLayer":
                    try:
                        for x, y, gid in layer:
                            image = self.tmx_data.get_tile_image_by_gid(gid)
                            if image:
                                scaled_image = pygame.transform.scale(
                                    image,
                                    (int(self.tmx_data.tilewidth * self.zoom), int(self.tmx_data.tileheight * self.zoom))
                                )
                                screen_x = (x * self.tmx_data.tilewidth - offset[0]) * self.zoom
                                screen_y = (y * self.tmx_data.tileheight - offset[1]) * self.zoom
                                self.screen.blit(scaled_image, (screen_x, screen_y))
                    except Exception as e:
                        print(f"Fehler beim Zeichnen des Layers {getattr(layer, 'name', 'unbekannt')}: {e}")

            # Schatten für den Spieler zeichnen
            for sprite in self.player_group:
                sprite.draw_shadow(self.screen, offset, self.zoom)

            # Spieler updaten und zeichnen
            keys = pygame.key.get_pressed()
            dt = self.clock.get_time()
            self.player_group.update(keys, dt)
            for sprite in self.player_group:
                scaled_sprite = pygame.transform.scale(
                    sprite.image,
                    (int(sprite.rect.width * self.zoom), int(sprite.rect.height * self.zoom))
                )
                self.screen.blit(
                    scaled_sprite,
                    ((sprite.rect.x - offset[0]) * self.zoom, (sprite.rect.y - offset[1]) * self.zoom)
                )
            
            # HealthBar
            self.health_bar.update(self.player.health)
            self.health_bar.draw(self.screen)
            
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

    #Menü 
    menu = Menu(screen)
    menu.run()

    spiel = Spiel()
    spiel.run()
