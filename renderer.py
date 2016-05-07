import pygame

class SDLRenderer:
    def __init__(self, size):
        self.screen = pygame.display.set_mode(size)
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0, 255))
        self.minimap = None
        self.minimapPos = None

    def render(self, ui, game, minimap):
        self.screen.blit(self.background, (0, 0))
        self.renderUI(ui, game, self.screen)
        if minimap:
            self.minimapPos, self.minimap = game.renderMinimap(self.screen, ui.vp)
        if self.minimap is not None:
            self.screen.blit(self.minimap, self.minimapPos)



renderer = SDLRenderer((1024, 768))
