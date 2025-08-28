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

    def load(self, path: str):
        self.tmx_data = load_pygame(path)
        self.tilewidth = self.tmx_data.tilewidth
        self.tileheight = self.tmx_data.tileheight

        # Kollisionstiles
        self.collision_tiles.clear()
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, '__iter__') and getattr(layer, 'name', '') == 'Wände':
                for x, y, gid in layer:
                    if gid != 0:
                        self.collision_tiles.add((x, y))

        # Spawn
        spawn_x, spawn_y = 100, 100
        for layer in self.tmx_data.layers:
            if getattr(layer, 'name', '') == "playerSpawn":
                for obj in layer:
                    spawn_x, spawn_y = int(obj.x), int(obj.y)
                    break
        self.spawn = (spawn_x, spawn_y)

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

    def draw(self, screen: pygame.Surface, kamera, zoom: float):
        if not self.tmx_data:
            return
        offset_x, offset_y = kamera.offset
        for layer in self.tmx_data.visible_layers:
            if layer.__class__.__name__ == "TiledTileLayer":
                try:
                    for x, y, gid in layer:
                        if gid == 0:
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
                    print(f"Fehler beim Zeichnen des Layers {getattr(layer, 'name', 'unbekannt')}: {e}")