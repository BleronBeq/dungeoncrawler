import pygame, sys
from settings import AssetLoader
from sprites import *
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

        self.max_enemies = 5 #max(1,len(self.tilemap.enemy_spawns))
        self.respawn_cooldown_ms = 1500
        self._respawn_timer_ms = 0

        # Healthbar
        self.health_bar = HealthBar(x=10, y=10, max_health=20, spacing=5, heart_size=(32, 32))

    def load_map(self, path):
        # Mapdaten laden
        self.tilemap.load(path)

        # Player erstellen (Spawn aus TileMap)
        spawn_x, spawn_y = self.tilemap.spawn
        self.player = Player(spawn_x, spawn_y, self.tilemap.collision_tiles, self.tilemap.tilewidth, self.tilemap.tileheight)
        self.player_group = pygame.sprite.Group(self.player)

        # Gegner erstellen
        self.enemy_group = pygame.sprite.Group()
        for (enemy_x, enemy_y) in self.tilemap.enemy_spawns:
            enemy = Enemy((enemy_x, enemy_y),self.player,self.tilemap.collision_tiles,self.tilemap.tilewidth,self.tilemap.tileheight)
            self.enemy_group.add(enemy)

        # Kamera
        self.kamera = Kamera(self.player, 1280, 800, self.zoom)

        # Exits referenzieren
        self.exits = self.tilemap.exits

        # Items/Türen-Manager
        self.items = ItemsManager(self.tilemap, self.player, self.enemy_group)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            dt = self.clock.get_time()

            # Gegner spawnen (Dauerloop)
            #Enemy.spawn_enemy(self.enemy_group, self.player, self.tilemap.collision_tiles, self.tilemap.tilewidth, self.tilemap.tileheight, max_enemies=8)

            # Respawn nur von Tiled-Spawnpunkten
            self._respawn_timer_ms = max(0, self._respawn_timer_ms - dt)
            if self._respawn_timer_ms == 0 and len(self.enemy_group) < self.max_enemies:
                if self.tilemap.enemy_spawns:
                    sx, sy = random.choice(self.tilemap.enemy_spawns)  # wähle einen Tiled-Spawnpunkt
                    enemy = Enemy(
                        (sx, sy),
                        self.player,
                        self.tilemap.collision_tiles,
                        self.tilemap.tilewidth,
                        self.tilemap.tileheight
                    )
                    self.enemy_group.add(enemy)
                self._respawn_timer_ms = self.respawn_cooldown_ms


            # Spieler-Update
            self.player_group.update(keys, dt)

            # Gegner-Update
            self.enemy_group.update(dt)

            # Items/Türen-Logik
            self.items.update(keys, self.player.rect, pygame.mouse.get_pos(), self.kamera, self.zoom)

            # Tod-Erkennung
            if getattr(self.player, "is_dead", False) or self.player.health <= 0:
                menu = Menu(self.screen)
                menu.game_over()
                menu.return_to_menu()
                self.load_map(self.map_path)
                continue

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

            # Gegner zeichnen
            for sprite in self.enemy_group:
                scaled_sprite = pygame.transform.scale(
                    sprite.image,
                    (int(sprite.rect.width * self.zoom), int(sprite.rect.height * self.zoom))
                )
                screen_x, screen_y = self.kamera.apply((sprite.rect.x, sprite.rect.y))
                self.screen.blit(
                    scaled_sprite,
                    (screen_x * self.zoom, screen_y * self.zoom)
                )

            # Schwert 
            self.items.draw_sword(self.screen, self.kamera, self.zoom)

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