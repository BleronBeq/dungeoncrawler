
import pygame
from os.path import join, dirname
from pytmx.util_pygame import load_pygame

class AssetLoader:
    def __init__(self, scale=None):
        self.scale = scale
        self.base_path = (join(dirname(__file__), ".."))

    def load_image(self, *path_parts):
        path = join(self.base_path, "assets", *path_parts)
        img = pygame.image.load(path).convert_alpha()
        if self.scale:
            img = pygame.transform.smoothscale(img, self.scale)
        return img

    def load_tmx(self, *path_parts):
        path = join(self.base_path, "assets", *path_parts)
        return load_pygame(path)
    
    def get_path(self, *path_parts):
        return join(self.base_path, "assets", *path_parts)
