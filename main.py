import math
import random

import pygame

import cubic_noise
import to_iso

# Инициализация библиотеки Pygame
pygame.init()

# Параметры окна
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("Isometric lands")

# Параметры игрока
player_x = 40
player_y = 40

# Загрузка изображений
player_img = pygame.image.load("media/graphics/player.png").convert_alpha()
deepwater_img = pygame.image.load("media/graphics/tiles/deepwater.png").convert_alpha()
water_img = pygame.image.load("media/graphics/tiles/water.png").convert_alpha()
sand_img = pygame.image.load("media/graphics/tiles/sand.png").convert_alpha()
grass_img = pygame.image.load("media/graphics/tiles/grass.png").convert_alpha()

# Распределение идентификаторов блоков
block_codes = {
    -3: water_img,
    -2: player_img,
    -1: "air",
    0: sand_img,
    1: sand_img,
    2: sand_img,
    3: sand_img,
    4: sand_img,
    5: grass_img,
    6: grass_img,
    7: grass_img,
    8: deepwater_img
}

# Параметры карты
SEED = random.randint(0, 10000)
MAP_SIZE = 101

# Параметры тайлов
TILE_WIDTH = 30
TILE_HEIGHT = 30
TILE_DEPTH = 22
tiles = []

# Параметры рендера карты
RENDER_DEPTH = 1
RENDER_DISTANCE = 24
cur_rotation = 0

# Параметры ландшафта
HEIGHT_LIMIT = 12
SEA_LEVEL = 4
height_map = []

# Генерация карты высот
for i in range(MAP_SIZE):
    column = []
    for j in range(MAP_SIZE):
        column.append(
            math.floor(cubic_noise.sample2d(i / 8, j / 8, SEED, 1) ** 2 * (HEIGHT_LIMIT - 2) + 2)
        )
    height_map.append(column)

# Генерация карты
for i in range(MAP_SIZE):
    column = []
    for j in range(MAP_SIZE):
        stack = []
        for k in range(height_map[i][j]):
            stack.append(
                math.floor(cubic_noise.sample2d(i / 8, j / 8, SEED, 1) * 6) + 2
            )

        if i == player_x and j == player_y:
            stack.append(-2)

        for k in range(height_map[i][j], HEIGHT_LIMIT):
            if k < SEA_LEVEL:
                stack.append(-3)
            else:
                stack.append(-1)

        column.append(stack)
    tiles.append(column)

# Значения функций синуса и косинуса хранятся в словаре и нужные их значения
# выносятся в отдельные переменные в виду ограниченного набора возможных значений
cos = {0: 0, 1: 1, 2: 0, 3: -1}
sin = {0: 1, 1: 0, 2: -1, 3: 0}
cur_r_cos = cos[cur_rotation]
cur_r_sin = sin[cur_rotation]


# Функция адаптации координат к текущему повороту карты
def rotated_cords(x, y):
    return ((x * cur_r_cos + y * cur_r_sin),
            (y * cur_r_cos + x * cur_r_sin))


# Рендеринг карты
def redrawn_field():
    t_field = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    player_rend = rotated_cords(player_x, player_y)
    for x in range(
            -RENDER_DISTANCE,
            RENDER_DISTANCE + 1
    ):
        for y in range(
                -RENDER_DISTANCE,
                RENDER_DISTANCE + 1
        ):
            # Поворот осей координат по углу поворота камеры
            cords = rotated_cords(x, y)
            wcord = player_x + cords[0]
            hcord = player_y + cords[1]
            if 0 <= wcord < MAP_SIZE \
                    and \
                    0 <= hcord < MAP_SIZE:
                # Последовательная отрисовка блоков
                for z in range(height_map[wcord][hcord] - RENDER_DEPTH, HEIGHT_LIMIT):
                    # Проверка не блок ли воздуха обрабатываемый блок
                    # (Воздух не нужно отрисовывать)
                    if tiles[wcord][hcord][z] != -1:
                        rend_x = (to_iso.x(x, y) + SCREEN_WIDTH // TILE_WIDTH // 2)
                        rend_y = (to_iso.y(x, y) + SCREEN_HEIGHT // TILE_HEIGHT // 2)

                        t_field.blit(
                            block_codes[tiles[wcord][hcord][z]],
                            (rend_x * TILE_WIDTH,
                             rend_y * TILE_HEIGHT - TILE_DEPTH * (
                                         z - height_map[player_rend[0]][player_rend[1]] / 4 - 5)
                             )
                        )
    return t_field


# Предварительный рендер карты
field = redrawn_field()


# Удаление копии игрока с его прошлого местоположения
def delete_trail():
    if height_map[player_x][player_y] >= SEA_LEVEL:
        tiles[player_x][player_y][height_map[player_x][player_y]] = -1
    else:
        tiles[player_x][player_y][height_map[player_x][player_y]] = -3


# Добавление игрока на текущие координаты
def update_player():
    tiles[player_x][player_y][height_map[player_x][player_y]] = -2


# Функция перемещения игрока
def move_player(x, y):
    global player_x, player_y
    processed_move = rotated_cords(x, y)
    new_x = player_x + processed_move[0]
    new_y = player_y + processed_move[1]
    if 0 <= new_x < MAP_SIZE \
            and \
            0 <= new_y < MAP_SIZE:
        delete_trail()
        player_x = new_x
        player_y = new_y
        update_player()


# Функия поворота карты
def rotate_map(rot):
    global cur_rotation, cur_r_cos, cur_r_sin
    cur_rotation = (cur_rotation + rot) % 4
    cur_r_cos = cos[cur_rotation]
    cur_r_sin = sin[cur_rotation]


# Отображение карты на экране
def draw_map():
    screen.blit(field, (0, 0))


# Игровой цикл
game_over = False
clock = pygame.time.Clock()

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

    # Обработка клавиш для движения игрока
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        move_player(-1, 1)

    if keys[pygame.K_RIGHT]:
        move_player(1, -1)

    if keys[pygame.K_UP]:
        move_player(-1, -1)

    if keys[pygame.K_DOWN]:
        move_player(1, 1)

    # Обработка клавиш для поворота карты
    if keys[pygame.K_q]:
        rotate_map(3)
    if keys[pygame.K_e]:
        rotate_map(1)

    # Отрисовка объектов на экране
    field = redrawn_field()
    draw_map()
    pygame.display.update()

    # Ограничение количества кадров в секунду
    clock.tick(20)

# Завершение игры
pygame.quit()
