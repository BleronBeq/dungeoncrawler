
import pygame

class HealthBar:
    def __init__(self,x,y,width,height, max_health):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_health = max_health
        self.current_health = max_health

    def update(self, current_health):
        self.current_health = max(0, min(current_health, self.max_health))

    def draw(self, surface):
        pygame.draw.rect(surface, (255,0,0), (self.x, self.y, self.width, self.height))
        health_width = (self.current_health / self.max_health) * self.width
        pygame.draw.rect(surface, (0,255,0), (self.x, self.y, health_width, self.height))

