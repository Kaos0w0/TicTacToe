import pygame
import numpy as np

# Definición de una clase para botones
class Button:
    def __init__(self, rect):
        self.color = (255,255,255)
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface(self.rect.size)
        self.image.fill(self.color)
    def render(self, screen):
        screen.blit(self.image, self.rect)
    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                return True
    def get_rect(self):
        return self.rect

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
    def __init__(self, state, parent, operation, depth, cost, matrix):
        self.state = state
        self.parent = parent
        self.operation = operation
        self.depth = depth
        self.cost = cost
        self.matrix = matrix

    def move(self, direction, action):
        if action != None and action != 'Walk':
            operation = direction + ' and ' + action
        else:
            operation = direction

        match direction:
            case 'up': next_pos = self.state.currentPos.move_up()
            case 'down': next_pos = self.state.currentPos.move_down()
            case 'left': next_pos = self.state.currentPos.move_left()
            case 'right': next_pos = self.state.currentPos.move_right()

        next_state = State(next_pos, self.state.fire_number, self.state.bucket, self.state.bucket_state)
        node = Node(next_state, self, operation, self.depth + 1, self.cost + 1, np.copy(self.matrix))
        node.apply_action(action)

        return node

    def apply_action(node, action):
        match action:
            case 'fill': node.state.fill_bucket()
            case 'put_out': node.state.put_out_fire()
            case 'pick_up_small_bucket': node.state.bucket = 1
            case 'pick_up_big_bucket': node.state.bucket = 2

        if action != 'fill' and action != 'Walk' and action != None:
            node.matrix[node.state.currentPos.y][node.state.currentPos.x] = 0

class State:
    def __init__(self, currentPos, fire_number, bucket, bucket_state):
        self.currentPos = currentPos
        self.fire_number = fire_number
        self.bucket = bucket
        self.bucket_state = bucket_state
    def get_state(self):
        return ((self.currentPos.x, self.currentPos.y), self.fire_number, self.bucket, self.bucket_state)
    def put_out_fire(self):
        self.fire_number -= 1
        self.bucket_state -= 1
    def fill_bucket(self):
        self.bucket_state = self.bucket

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def move_up(self):
        return Position(self.x, self.y - 1)
    def move_down(self):
        return Position(self.x, self.y + 1)
    def move_left(self):
        return Position(self.x - 1, self.y)
    def move_right(self):
        return Position(self.x + 1, self.y)