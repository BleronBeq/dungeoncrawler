import os
import pygame
from pytmx.util_pygame import load_pygame

class TileMap:
    def __init__(self):
        self.tmx_data = None
        self.collision_tiles = set()
        self.exits = []
        self.spawn = (100, 100)
        self.tilewidth = 0
        self.tileheight = 0

        # Gegner-Spawn
        self.enemy_spawns = []

        # Türen/Schlüssel-States
        self.door_tiles = set()    
        self.key_tiles = set()     
        self.open_doors = set()    
        self.collected_keys = set()
        self.door_rects = {}       
        self.key_rects = {}        

    def load(self, path: str):
        self.tmx_data = load_pygame(path)
        self.tilewidth = self.tmx_data.tilewidth
        self.tileheight = self.tmx_data.tileheight

        # Reset States
        self.collision_tiles.clear()
        self.door_tiles.clear()
        self.key_tiles.clear()
        self.open_doors.clear()
        self.collected_keys.clear()
        self.door_rects.clear()
        self.key_rects.clear()

        # Kollisionstiles (Wände + Türen)
        for layer in self.tmx_data.visible_layers:
            if layer.__class__.__name__ == "TiledTileLayer":
                lname = getattr(layer, 'name', '')
                if lname in ('Wände', 'Türen'):
                    for x, y, gid in layer:
                        if gid != 0:
                            self.collision_tiles.add((x, y))

        # Türen und Schlüssel Tile-Positionen/Rects erfassen
        for layer in self.tmx_data.layers:
            if layer.__class__.__name__ == "TiledTileLayer":
                lname = getattr(layer, 'name', '')
                if lname == 'Türen':
                    for x, y, gid in layer:
                        if gid != 0:
                            self.door_tiles.add((x, y))
                            self.door_rects[(x, y)] = pygame.Rect(
                                x * self.tilewidth, y * self.tileheight, self.tilewidth, self.tileheight
                            )
                elif lname == 'Schlüssel':
                    for x, y, gid in layer:
                        if gid != 0:
                            self.key_tiles.add((x, y))
                            self.key_rects[(x, y)] = pygame.Rect(
                                x * self.tilewidth, y * self.tileheight, self.tilewidth, self.tileheight
                            )

        # Spawn
        spawn_x, spawn_y = 100, 100
        for layer in self.tmx_data.layers:
            if getattr(layer, 'name', '') == "playerSpawn":
                for obj in layer:
                    spawn_x, spawn_y = int(obj.x), int(obj.y)
                    break
        self.spawn = (spawn_x, spawn_y)

        # Gegner-Spawn
        self.enemy_spawns = []
        for layer in self.tmx_data.layers:
            if getattr(layer, 'name', '') == "enemySpawn":
                for obj in layer:
                    self.enemy_spawns.append((int(obj.x), int(obj.y)))

        # Exits
        self.exits = []
        for layer in self.tmx_data.layers:
            if getattr(layer, 'name', '') == "exit":
                for obj in layer:
                    next_map = None
                    props = getattr(obj, 'properties', {})
                    if 'nextMap' in props and props['nextMap']:
                        next_map = os.path.join(os.path.dirname(path), props['nextMap'])
                    self.exits.append({
                        "rect": pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height)),
                        "nextMap": next_map
                    })

    def open_door(self, pos):
        # Tür öffnen: nicht mehr zeichnen, nicht mehr kollidieren
        if pos in self.door_tiles and pos not in self.open_doors:
            self.open_doors.add(pos)
            if pos in self.collision_tiles:
                self.collision_tiles.discard(pos)

    def collect_key(self, pos):
        # Schlüssel einsammeln: nicht mehr zeichnen
        if pos in self.key_tiles and pos not in self.collected_keys:
            self.collected_keys.add(pos)

    def draw(self, screen: pygame.Surface, kamera, zoom: float):
        if not self.tmx_data:
            return
        offset_x, offset_y = kamera.offset
        for layer in self.tmx_data.visible_layers:
            if layer.__class__.__name__ == "TiledTileLayer":
                lname = getattr(layer, 'name', '')
                try:
                    for x, y, gid in layer:
                        if gid == 0:
                            continue
                        # Sichtbarkeit
                        if lname == 'Türen' and (x, y) in self.open_doors:
                            continue
                        if lname == 'Schlüssel' and (x, y) in self.collected_keys:
                            continue

                        image = self.tmx_data.get_tile_image_by_gid(gid)
                        if not image:
                            continue
                        w = int(self.tilewidth * zoom)
                        h = int(self.tileheight * zoom)
                        scaled = pygame.transform.scale(image, (w, h))
                        screen_x = (x * self.tilewidth - offset_x) * zoom
                        screen_y = (y * self.tileheight - offset_y) * zoom
                        screen.blit(scaled, (screen_x, screen_y))
                except Exception as e:
                    print(f"Fehler beim Zeichnen des Layers {lname or 'unbekannt'}: {e}")