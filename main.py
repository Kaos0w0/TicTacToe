import math
import time
import pygame
import asyncio
import numpy as np
import multiprocessing
from itertools import count
from classes import Button, Node, Text
from queue import PriorityQueue, LifoQueue

# Setup para pygame
X = 1280
Y = 628
pygame.init()
running = True
screen_number = 0
last_movement = None
clock = pygame.time.Clock()
pygame.display.set_caption('Triqui')
screen = pygame.display.set_mode((X, Y))

# Titulo de la ventana
text_title = Text('Triqui', (X // 2, Y // 9), (0, 0, 0), 32)

# Botones para el juego
button_min = Button((200, 200, 200, 200))
text_button_min = Text('Inicia jugador', (X // 4 - 20, Y // 2 + 75), (0, 0, 0), 25)
button_min_image = pygame.image.load('./images/human.png').convert_alpha()

button_max = Button((200, 200, X + 200, 200))
text_button_max = Text('Inicia Máquina', (X - X // 4 - 20, Y // 2 + 75), (0, 0, 0), 25)
button_max_image = pygame.image.load('./images/robot.png').convert_alpha()

button_clock = Button((10, Y - 100, 100, 100))
button_clock_image1 = pygame.image.load('./images/clock1.png').convert_alpha()
button_clock_image2 = pygame.image.load('./images/clock2.png').convert_alpha()

text_result = Text('', (X // 2, Y - Y // 4), (0, 0, 0), 32)

# Imagenes para el juego
x_image = pygame.image.load('./images/x.png').convert_alpha()
o_image = pygame.image.load('./images/o.png').convert_alpha()

# Variables para el juego
matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
node = Node(np.copy(matrix), None, None, None, 0)
next_player = 'min'

def available_movements(matrix):
    movements = []
    for i in range(3):
        for j in range(3):
            if matrix[i][j] == 0:
                movements.append((i, j))
    return movements

def check_winner(matrix):
    # Checkea las filas
    for i in range(3):
        if matrix[i][0] != 0 and matrix[i][0] == matrix[i][1] and matrix[i][1] == matrix[i][2]:
            return matrix[i][0]
    # Checkea las columnas
    for i in range(3):
        if matrix[0][i] != 0 and matrix[0][i] == matrix[1][i] and matrix[1][i] == matrix[2][i]:
            return matrix[0][i]
    # Checkea las diagonales
    if matrix[0][0] != 0 and matrix[0][0] == matrix[1][1] and matrix[1][1] == matrix[2][2]:
        return matrix[0][0]
    if matrix[0][2] != 0 and matrix[0][2] == matrix[1][1] and matrix[1][1] == matrix[2][0]:
        return matrix[0][2]
    return 0

def restart(text):
    global screen_number
    screen_number = 0
    screen.fill("white")
    match text:
        case 'Empate': text_result.update_text('Empate')
        case 'Ganó la máquina': text_result.update_text('Ganó la máquina', (255, 0, 0))
        case _: text_result.update_text('', (0, 0, 0))
    button_min.set_active()
    button_min.set_active()
    button_max.set_active()
    button_max.set_active()
    global matrix
    matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    global node
    node = Node(np.copy(matrix), None, None, None, 0)
    
# Función que ejecuta el movimiento de la máquina
def machine_movement(node):
    global next_player
    screen.blit(button_clock_image1, button_clock_image1.get_rect(center = button_clock.get_rect().center))
    pygame.display.update()
    global screen_number
    q = LifoQueue()
    utilities = PriorityQueue()
    q.put(node)
    ended = False
    unique = count()
    if check_winner(node.get_matrix()) != 0:
        restart('Ganó el usuario')
        ended = True
    else:
        while not ended and not q.empty():
            actual_node = q.get()
            actual_matrix = actual_node.get_matrix()
            player = actual_node.get_player()
            if check_winner(actual_matrix) != 0:
                actual_node.set_utility(-1 if player == 'max' else 1)
                utilities.put((-actual_node.get_depth(), next(unique), actual_node))
            elif len(available_movements(actual_matrix)) == 0:
                actual_node.set_utility(0)
                utilities.put((-actual_node.get_depth(), next(unique), actual_node))
            else:
                available_movs = available_movements(actual_matrix)
                if len(available_movs) == 9:
                    available_movs = [(2, 2)]
                for movement in available_movs:
                    new_matrix = np.copy(actual_matrix)
                    new_matrix[movement[0]][movement[1]] = 1 if player == 'min' else 2
                    new_utility = math.inf if player == 'max' else -math.inf
                    new_node = Node(new_matrix, 'min' if player == 'max' else 'max', actual_node, movement, actual_node.get_depth() + 1, new_utility)
                    q.put(new_node)
                utilities.put((-actual_node.get_depth(), next(unique), actual_node))
        while not utilities.empty():
            actual_node = utilities.get()[2]
            parent = actual_node.get_parent()
            if parent != None:
                if parent.get_player() == 'max':
                    if actual_node.get_utility() > parent.get_utility():
                        if parent.get_depth() == 0:
                            parent.set_best_movement(actual_node.get_best_movement())
                        parent.set_utility(actual_node.get_utility())
                else:
                    if actual_node.get_utility() < parent.get_utility():
                        parent.set_utility(actual_node.get_utility())
            else:
                if(len(available_movements(actual_node.get_matrix())) == 0):
                    restart('Empate')
                    button_min.set_active()
                    ended = True
                else:
                    movement = actual_node.get_best_movement()
                    matrix[movement[0]][movement[1]] = 2
                    draw(movement[1], movement[0], o_image)
                    if check_winner(matrix) != 0:
                        restart('Ganó la máquina')
                        button_max.set_active()
                        ended = True
                    elif len(available_movements(matrix)) == 0:
                        restart('Empate')
                        button_max.set_active()
                        ended = True
                    else:
                        next_player = 'min'
                        screen.blit(button_clock_image2, button_clock_image1.get_rect(center = button_clock.get_rect().center))
                        pygame.display.update()

def draw(col, row, image):
    screen.blit(image, (col * X / 3 + 10, row * Y / 3 + 10))
    pygame.display.update()

# Código que se ejecuta mientras la ventana de pygame siga abierta
async def main():
    global running
    global next_player
    global screen_number
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN: # Checa si el botón izquierdo del mouse fue presionado
                    # Obtiene la posición del mouse
                    x, y = pygame.mouse.get_pos()

                    if screen_number == 1 and next_player == 'min':
                        if x < X / 3: col = 0
                        elif x < X / 3 * 2: col = 1
                        else: col = 2

                        if y < Y / 3: row = 0
                        elif y < Y / 3 * 2: row = 1
                        else: row = 2

                        if matrix[row][col] == 0:        
                            screen.blit(x_image, (col * X / 3 + 50, row * Y / 3 + 10))
                            pygame.display.update()
                            matrix[row][col] = 1
                            new_matrix = np.copy(matrix)             
                            next_player = 'max'           
                            machine_movement(Node(new_matrix, 'max', None, None, 0, -math.inf))
            
                        # Checa si el mouse está sobre el botón o su texto
                    if button_min.get_event(event) and screen_number == 0:
                        next_player = 'min'
                        screen_number = 1
                        screen.fill("white")
                        button_min.set_active()
                        node.set_player('min')
                        node.set_utility(math.inf)

                    if button_max.get_event(event) and screen_number == 0:
                        screen_number = 1
                        screen.fill("white")
                        button_max.set_active()
                        node.set_player('max')
                        node.set_utility(-math.inf)
                        machine_movement(node)

        # Dibuja el texto en la ventana
        if screen_number == 0:
            screen.fill("white")
            text_title.draw(screen)
            text_result.draw(screen)

            # Dibuja los botones en la ventana
            button_min.render(screen)
            button_max.render(screen)
            text_button_min.draw(screen)
            text_button_max.draw(screen)
            screen.blit(button_min_image, button_min_image.get_rect(center = button_min.get_rect().center)) 
            screen.blit(button_max_image, button_max_image.get_rect(center = button_max.get_rect().center))

        elif screen_number == 1:
            # drawing vertical lines
            pygame.draw.line(screen, (0,0,0), (X / 3, 0), (X / 3, Y), 7)
            pygame.draw.line(screen, (0,0,0), (X / 3 * 2, 0), (X / 3 * 2, Y), 7)
    
            # drawing horizontal lines
            pygame.draw.line(screen, (0,0,0), (0, Y / 3), (X, Y / 3), 7)
            pygame.draw.line(screen, (0,0,0), (0, Y / 3 * 2),  (X, Y / 3 * 2), 7)

            button_clock.render(screen)


        # Actualiza la ventana
        pygame.display.flip()

        # Limita los FPS a 60
        clock.tick(60)

    # El usuario cierra la ventana del juego
    pygame.quit()
    await asyncio.sleep(0)

asyncio.run(main())