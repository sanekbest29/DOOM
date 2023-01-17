import pygame
import os
import sys
from random import random
import csv

WIDTH, HEIGHT = 1920, 1080
FPS = 60
BASE_SCALE = 3
TILE_SIZE = BASE_SCALE * 16
GRAVITY = 25

GAME_OVER = pygame.USEREVENT + 1

LEVELS = ["2.txt", "2.txt", "2.txt"]


class Effect:
    def __init__(self, name, duration, dealer, owner):
        self.name = name
        self.duration = duration
        self.owner = owner
        self.dealer = dealer
        self.start_duration = duration

    def update(self):
        self.duration -= 1 / FPS


class Knockback(Effect):
    def __init__(self, dealer, owner, duration=0.2, power=7):
        super(Knockback, self).__init__("knockback", duration, dealer, owner)
        self.power = power

    def update(self):
        if self.duration == self.start_duration:
            self.owner.effects_force = (self.owner.effects_force[0], self.owner.effects_force[1] - self.power)
        super(Knockback, self).update()
        if self.owner.rect.x - self.dealer.rect.x >= 0:
            self.owner.effects_force = (self.owner.effects_force[0] + self.power, self.owner.effects_force[1])
        else:
            self.owner.effects_force = (self.owner.effects_force[0] - self.power, self.owner.effects_force[1])


class AnimatedSprite(pygame.sprite.Sprite):
    def set_frames(self, sheet, columns, rows):
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update_frame(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


def load_image(name, colorkey=-1):
    fullname = os.path.join("data\images", name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    image.set_colorkey(colorkey)
    return image


def load_level(filename):
    filename = "data/maps/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def get_scaled_image(image, scale):
    return pygame.transform.scale(image, (image.get_rect().width * scale,
                                          image.get_rect().height * scale))


def terminate():
    pygame.quit()
    sys.exit()


def roulette(chance):
    # шанс указывается в процентах
    if random() * 100 <= chance:
        return True
    return False


def draw_text(surf, text, size, pos, font_name=None, color="white", center=False):
    x, y = pos
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    if center:
        text_rect.center = (x, y)
    surf.blit(text_surface, text_rect)


def get_stat(name):
    with open(r"data\stats.csv", encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        for player in reader:
            return player[name]


def set_stat(name, value):
    with open(r"data\stats.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        data = []
        res = {}
        for player in reader:
            data.append(player)
        for i in range(len(data[0])):
            if data[0][i] == name:
                res[data[0][i]] = value
            else:
                res[data[0][i]] = res[data[1][i]]

        with open(r"data\stats.csv", "w") as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=list(res.keys()),
                delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            writer.writerow(res)

def play_sound(name, loops=0):
    fullname = os.path.join("data\sounds", name)
    if not os.path.isfile(fullname):
        sys.exit()
    sound = pygame.mixer.Sound(fullname)
    pygame.mixer.Sound.play(sound, loops)
