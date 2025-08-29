import pygame
from settings import AssetLoader

class ItemsManager:

    def __init__(self, tilemap):
        self.set_map(tilemap)
        self.key_count = 0
        self._prev_e_pressed = False

    def set_map(self, tilemap):
        self.tilemap = tilemap
        self.key_count = 0
        self._prev_e_pressed = False

        self._key_icon = None
        self._key_icon_placeholder = None

        try:
            loader = AssetLoader(scale=(48,48))
            self._key_icon_placeholder = loader.load_image("Maps", "key_placeholder.png")
        except Exception:
            self._key_icon_placeholder = None

        try:
            loader = AssetLoader(scale=(48, 48))
            self._key_icon = loader.load_image("Maps", "key.png")
        except Exception:
            self._key_icon = None

        self._ui_font = pygame.font.SysFont(None, 22)

    def update(self, keys, player_rect):
        for pos, rect in list(self.tilemap.key_rects.items()):
            if pos in self.tilemap.collected_keys:
                continue
            if player_rect.colliderect(rect):
                self.tilemap.collect_key(pos)
                self.key_count += 1

        e_pressed = keys[pygame.K_e]
        e_edge = e_pressed and not self._prev_e_pressed
        self._prev_e_pressed = e_pressed

        # Türen öffnen
        if e_edge and self.key_count > 0:
            for pos, rect in self.tilemap.door_rects.items():
                if pos in self.tilemap.open_doors:
                    continue
                if player_rect.colliderect(rect):
                    # Tür öffnen
                    self.tilemap.open_door(pos)
                    self.key_count -= 1
                    break

    def draw_key_ui(self, surface, margin=(10, 10), color=(240, 240, 240)):

        icon = self._key_icon if self.key_count > 0 else self._key_icon_placeholder
        if icon is None:
            icon = self._key_icon or self._key_icon_placeholder
        if icon is None:
            return

        x = surface.get_width() - icon.get_width() - margin[0]
        y = margin[1]
        surface.blit(icon, (x, y))
        # Anzahl nur anzeigen, wenn >1
        #if self.key_count > 1:
        #    txt = self._ui_font.render(f"x{self.key_count}", True, color)
        #    surface.blit(txt, (x - txt.get_width() - 6, y + (icon.get_height() - txt.get_height()) // 2))

    #def draw_ui(self, surface, font=None, pos=(10, 50), color=(240, 240, 240)):
    #    if font is None:
    #        font = pygame.font.SysFont(None, 22)
    #    txt = font.render(f"Schlüssel: {self.key_count}", True, color)
    #    surface.blit(txt, pos)