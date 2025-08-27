import pygame
import sys

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

class Button:
    def __init__(self, text, x, y, w, h,action = None):
        self.text = text
        self.rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        self.action = action
        self.font = pygame.font.Font(None, 74)
        self.color_inactive = (100, 100, 100)
        self.color_active = (200, 200, 200)
        self.color = self.color_inactive
    
    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if self.rect.collidepoint(mouse_pos):
            self.color = self.color_active
            if click[0] == 1 and self.action is not None:
                self.action()
        
        else:
            pygame.draw.rect(screen, WHITE, self.rect)


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.buttons = [
            Button("Start Game", (640, 300), self.start_game),
            Button("Quit", (640, 400), self.quit_game)
        ]
        pygame.display.set_caption("DUNGEON CRAWLER")
        pygame.display.set_mode((1280, 800))
        self.font = pygame.font.Font(None, 74)
    
    def start_game(self):
        print("Starting game...")

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def run(self):
        while self.running:
            self.screen.fill(BLACK)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            for button in self.buttons:
                button.draw(self.screen)
            
            pygame.display.update()
            


