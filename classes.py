import pygame
import numpy as np

# Definición de una clase para botones
class Button:
    def __init__(self, rect):
        self.color = (255,255,255)
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface(self.rect.size)
        self.image.fill(self.color)
        self.active = True
    def render(self, screen):
        screen.blit(self.image, self.rect)
    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.active:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                return True
    def get_rect(self):
        return self.rect
    def set_active(self):
        self.active = not self.active

# Definicion de una clase para el texto
class Text:
    def __init__(self, text, pos, color, font_size, clikable=True):
        self.text = text
        self.pos = pos
        self.color = color
        self.font_size = font_size
        self.font = pygame.font.Font('freesansbold.ttf', self.font_size)
        self.clickable = clikable
        self.render()
    def render(self):
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
    def update_text(self, text, color=(0,0,0)):
        self.color = color
        self.text = text
        self.render()
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                return True
    def set_clickable(self):
        self.clickable = not self.clickable
    def get_clickable(self):
        return self.clickable
    def get_text(self):
        return self.text
    
class Node: 
    def __init__(self, matrix, player, parent, best_movement, depth = 0, utility = 0):
        self.matrix = matrix
        self.player = player
        self.parent = parent
        self.best_movement = best_movement
        self.depth = depth
        self.utility = utility
    def get_matrix(self):
        return self.matrix
    def get_player(self):
        return self.player
    def get_parent(self):
        return self.parent
    def get_best_movement(self):
        return self.best_movement
    def get_depth(self):
        return self.depth
    def get_utility(self):
        return self.utility
    def set_player(self, player):
        self.player = player
    def set_utility(self, utility):
        self.utility = utility
    def set_best_movement(self, best_movement):
        self.best_movement = best_movement