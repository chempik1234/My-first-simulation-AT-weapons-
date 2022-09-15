import os
from math import sqrt
import pygame
mixer = pygame.mixer
mixer.init()
#win = mixer.Sound('data/sounds/win.wav')
SPEED = 100
PING = 0
DISTANCE_FROM_TARGET = 2000
MAX_AIMED_DISTANCE = 3000
ROTATION_SPEED = 100
CORRECTION_SPEED = 100
TANK_SIZE = 1

WIDTH = 1280
HEIGHT = 480
RENDER_WIDTH_PERCENT = 70
screen_size = (WIDTH, HEIGHT)
FPS = 50
pygame.init()
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('AT weapons simulation')
clock = pygame.time.Clock()


# def click_rect(xy, xywh):
#     x, y = xy
#     x1, y1, w, h = xywh
#     return 0 <= x - x1 <= w and 0 <= y - y1 <= h


def load_image(name, color_key=None):
    fullname = os.path.join('data\\images', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не могу загрузить изображение:', name)
        raise SystemExit(message)
    except Exception as message:
        print('Не могу загрузить изображение:', name)
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        #else:
            #image.set_colorkey(image.get_at((49, 0)))
    else:
        image = image.convert_alpha()
    return image


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None
        self.origin_x = self.origin_y = None

    def get_event(self, event):
        pass


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.x, self.y, self.z = 0, 0, 0

    def apply(self, obj):
        obj.rect.x = obj.origin_x + self.dx
        obj.rect.y = obj.origin_y + self.dy

    def update(self, target):
        self.dx = -(target.origin_x + target.rect.w // 2 - WIDTH // 2) #150
        self.dy = -(target.origin_y + target.rect.h // 2 - HEIGHT // 2) #+50


tank_image = load_image('tank.png', -1)
rocket_image = load_image('rocket.png', -1)


class ROCKET(Sprite):
    def __init__(self, SPEED, PING, MAX_AIMED_DISTANCE, ROTATION_SPEED,
                 CORRECTION_SPEED):
        super().__init__((all_sprites, rocket_group))
        self.image = rocket_image
        self.SPEED = SPEED
        self.PING = PING
        self.MAX_AIMED_DISTANCE = MAX_AIMED_DISTANCE
        self.ROTATION_SPEED = ROTATION_SPEED
        self.CORRECTION_SPEED = CORRECTION_SPEED
        self.x, self.y, self.z = 0, 0, 0
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height()).move(self.x, self.y)
        self.origin_x, self.origin_y, self.origin_z = 0, 0, 0


class TANK(Sprite):
    def __init__(self, DISTANCE_FROM_TARGET, SIZE):
        super().__init__((all_sprites, tank_group))
        self.DISTANCE_FROM_TARGET = DISTANCE_FROM_TARGET
        self.SIZE = SIZE
        self.source_image = tank_image
        self.image = self.source_image
        self.img_size = self.source_image.get_size()
        self.x, self.y, self.z = 0, 0, DISTANCE_FROM_TARGET
        self.rect = pygame.Rect(0, 0,
                                self.image.get_width(),
                                self.image.get_height()).move(self.x, self.y)
        self.origin_x, self.origin_y, = 0, 0


def draw_text(text, text_coord_y, text_coord_x, size_font, color):
    font = pygame.font.Font(None, size_font)
    for line in text:
        string_rendered = font.render(line, 1, color)
        _rect = string_rendered.get_rect()
        text_coord_y += 10
        _rect.top = text_coord_y
        _rect.x = text_coord_x
        text_coord_y += _rect.height
        screen.blit(string_rendered, _rect)


def render(rocket, tank, camera):
    #global tank, rocket, camera
    tick = clock.tick(FPS)
    ######################### POSITIONS
    rocket.z += rocket.SPEED / tick
    camera.z = rocket.z - 100
    camera.x, camera.y = rocket.x, rocket.y
    ######################### BG
    screen.fill(pygame.Color('light blue'), (0, 0,
                                             WIDTH * RENDER_WIDTH_PERCENT / 100, HEIGHT))
    num = 2000 + int(tank.z - camera.z)
    for i in range(0, num, 10):
        c = (int(i*255/num) + 200) // 2
        RATIO_TO_LINES = 1000 / abs(num-i)
        screen.fill((0, c, 0), (0, camera.y * RATIO_TO_LINES + HEIGHT / 2,
                                WIDTH * RENDER_WIDTH_PERCENT / 100, HEIGHT // 2))
    ################### UI
    ui_size_x = WIDTH - WIDTH * (1 - (RENDER_WIDTH_PERCENT / 100))
    screen.fill(pygame.Color("white"), (ui_size_x, 0, WIDTH, HEIGHT))
    rects = {}
    rects_amount = 7
    rect_side_x = ui_size_x * 0.5
    rect_side_y = HEIGHT / 8 * 0.9
    rect_offset_x = WIDTH * RENDER_WIDTH_PERCENT // 100 + ui_size_x * 0.05
    rect_offset_y = HEIGHT / 8 * 0.1
    text_font = 14
    names = ["СКОРОСТЬ", "ПИНГ", "РАССТОЯНИЕ ДО ЦЕЛИ", "МАКСИМАЛЬНАЯ ПРИЦЕЛЬНАЯ ДИСТАНЦИЯ", "СКОРОСТЬ ВРАЩЕНИЯ",
            "СКОРОСТЬ ИЗМЕНЕНИЯ НАПРАВЛЕНИЯ", "РАЗМЕР ТАНКА"]
    for i in range(rects_amount):
        rects[names[i]] = pygame.Rect(rect_offset_x,
                                      rect_offset_y * (i + 1) + rect_side_y * i,
                                      rect_side_x, rect_side_y)
    for name, i in rects.items():
        screen.fill(pygame.Color('gray'), i)
        draw_text([name], i.y + i.h // 2 - text_font // 2,
                    i.x + i.w * 0.1,
                    text_font, pygame.Color('white'))

    draw_text(["РАССТОЯНИЕ ДО ЦЕЛИ: " + str(int(tank.z - rocket.z))], 10,
              30,
              60, pygame.Color('red'))
    ################### SCREEN POSITIONING
    RATIO = 1000 / abs(camera.z - tank.z)
    tank.image = pygame.transform.scale(tank.source_image,
                                        (int(tank.img_size[0] * RATIO / 10),
                                         int(tank.img_size[1] * RATIO / 10)))

    tank.rect.update(0, 0, tank.image.get_width(), tank.image.get_height())
    tank.origin_y = -tank.rect.height // 2
    tank.origin_x = -tank.rect.width // 2

    tank.origin_y += (rocket.y - tank.y) * RATIO
    tank.origin_x += RATIO * (tank.x - rocket.x)

    rocket.origin_x = -rocket.rect.width // 2
    rocket.origin_y = -rocket.rect.height // 2

    camera.update(rocket)

    for sprite in all_sprites:
        camera.apply(sprite)
    rad = 50 * (1 - (abs(camera.z - tank.z) /
                     sqrt(abs(camera.z - tank.z)**2 + abs(camera.y - tank.y)**2)))
    pygame.draw.ellipse(screen,
                        (00, 100, 00),
                        (tank.rect.x,
                         int((camera.y - rad / 2) * RATIO) + HEIGHT // 2 + tank.rect.height // 2,
                         tank.rect.width,
                         int(rad * RATIO)),
                        int(rad / 2 * RATIO))
    tank_group.draw(screen)
    rocket_group.draw(screen)


class ScreenFrame(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = (0, 0, 500, 500)


all_sprites = pygame.sprite.Group()
rocket_group = pygame.sprite.Group()
tank_group = pygame.sprite.Group()


running = True
rocket = None
tank = None
camera = Camera()
while running:
    if not rocket:
        rocket = ROCKET(SPEED, PING, MAX_AIMED_DISTANCE, CORRECTION_SPEED, ROTATION_SPEED)
        rocket.y = 120
    if not tank:
        tank = TANK(DISTANCE_FROM_TARGET, TANK_SIZE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
               rocket.y += 40
            if event.key == pygame.K_DOWN:
               rocket.y -= 40
            if event.key == pygame.K_LEFT:
               rocket.x -= 40
            if event.key == pygame.K_RIGHT:
               rocket.x += 40
    if rocket.z > tank.z or rocket.y < 0:
        running = False
    render(rocket, tank, camera)
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()