from settings import AssetLoader

class HealthBar:
    def __init__(self, x, y, max_health, spacing=5, heart_size=(32,32)):
        loader = AssetLoader(scale=heart_size)
        self.full_heart = loader.load_image("Sprites", "full_heart.png")
        self.half_heart = loader.load_image("Sprites", "half_heart.png")
        self.empty_heart = loader.load_image("Sprites", "empty_heart.png")

        self.x = x
        self.y = y
        self.max_health = max_health
        self.spacing = spacing
        self.current_health = max_health

    def update(self, health):
        self.current_health = health

    def draw(self, surface):
        full = self.current_health // 2
        half = self.current_health % 2
        max_slots = self.max_health // 2
        for i in range(max_slots):
            heart_x = self.x + i * (self.full_heart.get_width() + self.spacing)
            if i < full:
                surface.blit(self.full_heart, (heart_x, self.y)) # voll
            elif i == full and half:
                surface.blit(self.half_heart, (heart_x, self.y)) # halb
            else:
                surface.blit(self.empty_heart, (heart_x, self.y)) # leer
