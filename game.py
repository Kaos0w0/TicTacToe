import time
import mouse
import pygame
import numpy as np
from tkinter import Tk
from queue import Queue
from tkinter.filedialog import askopenfilename
from classes import Button, Node, Text, State, Position

# Setup para pygame
X = 1280
Y = 720
pygame.init()
running = True
screen_number = 0
clock = pygame.time.Clock()
screen = pygame.display.set_mode((X, Y))
pygame.display.set_caption('Bombero inteligente')

# Titulo de la ventana
text_title = Text('Bombero inteligente', (X // 2, Y // 9), (0, 0, 0), 32)

# Botones para el juego
button_load = Button((200, 200, 200, 200))
text_button_load = Text('Cargar configuración', (X // 4 - 20, Y // 2 + 75), (0, 0, 0), 25)
button_load_image = pygame.image.load('./images/upload.png').convert_alpha()

# Mensajes de error
text_load_error = Text('', (X // 2, Y - (Y // 6)), (255, 0, 0), 32)
text_error_reason = Text('', (X // 2, Y - (Y // 9)), (255, 0, 0), 25)

cell_width = 50
cell_height = 50

# Seleccion del tipo de solucion
text_your_configuration = Text('Tu configuración', (350, 75), (0, 0, 0), 32)
text_solution_type = Text('Seleccione el tipo solución que desee', (X - (X // 4), 75), (0, 0, 0), 25)
text_uninformed = Text('Búsqueda no informada', (X - (X // 4), 225), (255, 0, 0), 25)
text_informed = Text('Búsqueda informada', (X - (X // 4), 275), (255, 0, 0), 25)

# Para busqueda no informada
text_amplitud = Text('', (X - (X // 4), 325), (0, 0, 0), 25, False)
text_costo_uniforme = Text('', (X - (X // 4), 375), (0, 0, 0), 25, False)
text_profundidad = Text('', (X - (X // 4), 425), (0, 0, 0), 25, False)
uninformed_list = [text_amplitud, text_costo_uniforme, text_profundidad]
uninformed_list_messages = ['Búsqueda por amplitud', 'Búsqueda por costo uniforme', 'Búsqueda por profundidad (evitando ciclos)']

# Para busqueda informada
text_avara = Text('', (X - (X // 4), 375), (0, 0, 0), 25, False)
text_a_estrella = Text('', (X - (X // 4), 425), (0, 0, 0), 25, False)
informed_list = [text_avara, text_a_estrella]
informed_list_messages = ['Búsqueda avara', 'Búsqueda A*']

# Carpeta donde se encuentran ubicadas las imágenes
path = "./images/"

# Funcion de dibuja un cuadrado blanco en la posición (x, y) con la imagen especificada
# El tamaño del cuadrado está definido por cell_width y cell_height
def createSquare(x, y, image=None):
    pygame.draw.rect(screen, (255,255,255), [x, y, cell_width, cell_height ])
    img = pygame.image.load(path + image).convert_alpha()
    screen.blit(img, [x, y, cell_width, cell_height ])

# Función que dibuja la Matriz de juego
def visualizeGrid():
    y = 125 
    for row in map:
        x = 100
        for item in row:
            match item:
                case 0: createSquare(x, y, 'ground.png')
                case 1: createSquare(x, y, 'wall.png')
                case 2: createSquare(x, y, 'fire.png')
                case 3: createSquare(x, y, 'bucket1.png')
                case 4: createSquare(x, y, 'bucket2.png')
                case 5: createSquare(x, y, 'fireman_start.png')
                case 6: createSquare(x, y, 'hydrant.png')
            x += cell_width 
        y += cell_height   
    pygame.display.update()

# Función que deshabilita un texto (lo vuelve 'invisible' y no se puede clickear)
def disableText(text):
    text.set_clickable()
    text.update_text('', (128, 128, 128))

# Función que habilita un texto (lo vuelve 'visible' y se puede clickear)
def enableText(text, message):
    text.set_clickable()
    text.update_text(message, (0, 0, 0))

# Función que checa si se puede realizar una acción en una casilla, y en caso de ser así, cual será
# None = No se puede realizar ninguna acción en esa casilla
def checkAction(x, y, bucket, liters, mat):
    if x <= 9 and y <= 9 and x >= 0 and y >= 0:
        match mat[y][x]:
            case 1: return None
            case 2 if liters == 0: return None
            case 2 if liters != 0: return 'put_out'
            case 3 if bucket == False: return 'pick_up_small_bucket'
            case 4 if bucket == False: return 'pick_up_big_bucket'
            case 6 if liters == 0 and bucket: return 'fill'
            case _: return 'Walk'
    else:
        return None
    
# Función que simula la condición "Evite devolverse al estado anterior" si el tipo es "returning"
# o la condición "Evite ciclos" si el tipo es "cicles"
def avoid(node, parent, type='returning'):
    if type == 'returning':
        if(node.state.get_state() == parent.state.get_state()): return True
        return False
    
    elif type == 'cicles':
        while parent.parent != None:
            if(node.state.get_state() == parent.state.get_state()):
                return True
            parent = parent.parent
        return False

# Función que checa los movimientos posibles que puede realizar el bombero
def checkPossibleMovements(node, directions=['right', 'down', 'left', 'up']):
    movements = []
    x = node.state.currentPos.x
    y = node.state.currentPos.y
    liters = node.state.bucket_state   
    bucket = (node.state.bucket != 0)
    
    if node.parent == None: parent = node
    else: parent = node.parent    

    action_up = checkAction(x, y - 1, bucket, liters, map)
    action_down = checkAction(x, y + 1, bucket, liters, map)
    action_left = checkAction(x - 1, y, bucket, liters, map)
    action_right = checkAction(x + 1, y, bucket, liters, map)
    actions = [action_right, action_down, action_left, action_up]

    for i in range(0, 4):
        if actions[i] != None and not avoid(node.move(directions[i], actions[i]), parent):
            movements.append([directions[i], actions[i]])

    return movements

# Función que dibuja la cubeta (con su respectivo estado) que el bombero tiene en su poder
def draw_bucket(bucket_number, state):
    empty = pygame.image.load(path + 'empty_bucket.png').convert_alpha()
    full = pygame.image.load(path + 'full_bucket.png').convert_alpha()

    if bucket_number == 1:
        if state == 0: states = [empty]
        else: states = [full]
    else:
        if state == 0: states = [empty, empty]
        elif state == 1: states = [empty, full]
        elif state == 2: states = [full, full]

    separation = 0
    for image in states:
        square = [X - (X // 2) - 20, 125 + separation, cell_width, cell_height]
        screen.blit(image, square)
        separation += 50

# Función que anima el movimiento del bombero
def animate(matrix, state, direction, action=None):
    x = state[0][0]
    y = state[0][1]
    past_x = x
    past_y = y
    bucket_number = state[2]
    bucket_state = state[3]

    match direction:
        case 'up': past_y = y + 1
        case 'down': past_y = y - 1
        case 'left': past_x = x + 1
        case 'right': past_x = x - 1        
    
    past_cell = matrix[past_y][past_x]
    actual_cell = matrix[y][x]

    match past_cell:
        case 0 | 2 | 3 | 4: past_image = 'ground.png'
        case 5: past_image = 'start.png'
        case 6: past_image = 'hydrant.png'

    match action:
        case None:
            if actual_cell == 0: actual_image = 'fireman.png'
            elif actual_cell == 5: actual_image = 'fireman_start.png'
            elif actual_cell == 6: actual_image = 'fireman_hydrant.png'
            else: actual_image = 'fireman.png'
        case 'fill':
            draw_bucket(bucket_number, bucket_state)
            actual_image = 'fireman_fill.png'
        case 'put_out':
            draw_bucket(bucket_number, bucket_state)
            actual_image = 'fireman_ashes.png'
        case 'pick_up_small_bucket' | 'pick_up_big_bucket':
            draw_bucket(bucket_number, bucket_state)
            actual_image = 'fireman.png'
        case _: actual_image = 'ground.png'

    createSquare(100 + (50 * past_x), 125 + (50 * past_y), past_image)
    createSquare(100 + (50 * x), 125 + (50 * y), actual_image)
    pygame.display.update()

# Función que realiza la busqueda por amplitud
def busqueda_amplitud():
    start_time = time.time()
    end = False
    expanded_nodes = 0
    fire_number = 0
    fire_pos = []

    for i in range(0,10):
        for j in range(0,10):
            if map[j][i] == 5:
                pos_x = i
                pos_y = j
            if map[j][i] == 2:
                fire_number += 1
                fire_pos.append((j, i))

    pos = Position(pos_x, pos_y)
    state = State(pos, fire_number, 0, 0)
    node = Node(state, None, None, 0, 0, 0, fire_pos)    
    
    q = Queue()
    solution = []
    q.put(node)
    
    while(end == False):
        for text in uninformed_list:
            text.update_text('', (0, 0, 0))

        text_solution_type.update_text('', (0, 0, 0))
        text_uninformed.update_text("", (255, 0, 0))

        if q.empty():
            end = True  
            text_amplitud.update_text("No hay solucion", (255, 0, 0))
            print("No hay solucion")
        else:
            actual = q.get()
            expanded_nodes += 1
            if actual.state.fire_number == 0:
                screen_number = 2
                end = True
                text_solution_type.update_text("Solucion Encontrada", (0, 255, 0))
                text_uninformed.update_text("Nodos expandidos: " + str(expanded_nodes), (0, 0, 0))
                text_amplitud.update_text("Profundidad: " + str(actual.depth), (0, 0, 0))
                text_costo_uniforme.update_text("Costo: ---", (0, 0, 0))
                text_profundidad.update_text("Tiempo: " + str(time.time() - start_time), (0, 0, 0))

                while actual.parent != None:
                    operations = [map, actual.state.get_state()]
                    operations.append(actual.operation.split(' and '))
                    solution.append(operations)
                    actual = actual.parent

                solution = reversed(solution)
                for elem in solution:
                    if len(elem[2]) == 1:
                        animate(elem[0], elem[1], elem[2][0])
                    else:
                        animate(elem[0], elem[1], elem[2][0], elem[2][1])
                    time.sleep(1.5) 

            else:
                movements = checkPossibleMovements(actual)
                for movement in movements:
                    q.put(actual.move(movement[0], movement[1]))

# Código que se ejecuta mientras la ventana de pygame siga abierta
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN: # Checa si el botón izquierdo del mouse fue presionado
                # Obtiene la posición del mouse
                pos = pygame.mouse.get_pos()
    
                # Checa si el mouse está sobre el botón o su texto
                if button_load.get_event(event):
                    text_load_error.update_text('', (255, 0, 0))
                    text_error_reason.update_text('')
                    Tk().withdraw()
                    filename = askopenfilename()
                    if filename != '':
                        try:
                            map = np.loadtxt(filename, dtype=int)
                            if map.shape != (10, 10):
                                raise Exception
                            screen_number = 1
                            mouse.move(X // 2, Y // 2, absolute=True, duration=0)
                            mouse.click('left')
                            fire_number = 0
                        except:
                            mouse.move(X // 2, Y // 2, absolute=True, duration=0)
                            mouse.double_click('left')
                            text_load_error.update_text('Error al cargar el archivo', (255, 0, 0))
                            text_error_reason.update_text('El archivo no es txt o no contiene una matriz 10x10')

                elif text_informed.get_event(event):
                    disableText(text_uninformed)
                    text_informed.set_clickable()
                    n = 0
                    for text in informed_list:
                        enableText(text, informed_list_messages[n])
                        n += 1

                elif text_uninformed.get_event(event):
                    disableText(text_informed)
                    text_uninformed.set_clickable()
                    n = 0
                    for text in uninformed_list:
                        enableText(text, uninformed_list_messages[n])
                        n += 1

                elif text_amplitud.get_event(event):
                    busqueda_amplitud()

    # Llena la ventana de un color para limpiarla de ejecuciones de juego anteriores
    screen.fill("white")

    # Dibuja el texto en la ventana
    if screen_number == 0:
        text_title.draw(screen)

        # Dibuja el botón en la ventana
        button_load.render(screen)
        text_button_load.draw(screen)
        screen.blit(button_load_image, button_load_image.get_rect(center = button_load.get_rect().center))

        # Mensajes de error
        text_load_error.draw(screen)
        text_error_reason.draw(screen)

    elif screen_number == 1:
        text_your_configuration.draw(screen)
        text_solution_type.draw(screen)
        text_uninformed.draw(screen)
        text_informed.draw(screen)
        for text in uninformed_list:
            text.draw(screen)
        for text in informed_list:
            text.draw(screen)
        visualizeGrid()

    # Actualiza la ventana
    pygame.display.flip()

    # Limita los FPS a 60
    clock.tick(60)

# El usuario cierra la ventana del juego
pygame.quit()