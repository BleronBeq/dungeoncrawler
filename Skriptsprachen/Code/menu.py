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

        self.click_sound = pygame.mixer.Sound("Audio/Spawn.mp3")
        self.click_sound.set_volume(0.3)
    
    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if self.rect.collidepoint(mouse_pos):
            self.color = self.color_active
            if click[0] == 1 and self.action is not None:
                self.click_sound.play()
                self.action()
        
        else:
            self.color = self.color_inactive

        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)

        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.buttons = [
            Button("Spiel Starten", 640, 300, 350, 60, self.start_game),
            Button("Beenden", 640, 400, 350, 60, self.quit_game)
        ]
        pygame.display.set_caption("DUNGEON CRAWLER")
        self.font = pygame.font.Font(None, 74)


        pygame.mixer.music.load("Audio/EldenRingMenu.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    
    def start_game(self):
        print("Starte das Spiel...")
        pygame.mixer.music.stop()
        self.running = False

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
            title_surf = self.font.render("DUNGEON CRAWLER", True, WHITE)
            title_rect = title_surf.get_rect(center=(640, 100))
            self.screen.blit(title_surf, title_rect)
            
            for button in self.buttons:
                button.draw(self.screen)
            
            pygame.display.update()
            
    def game_over(self):
        self.screen.fill(BLACK)
        game_over_font = pygame.font.Font(None, 100)
        game_over_surf = game_over_font.render("YOU DIED", True, WHITE)
        game_over_rect = game_over_surf.get_rect(center=(640, 360))
        self.screen.blit(game_over_surf, game_over_rect)
        pygame.mixer.music.stop()
        pygame.display.flip()
        pygame.time.delay(3000)

    def return_to_menu(self):
        
        menu = Menu(self.screen)
        menu.run()