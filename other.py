import pygame
from additional import load_image, get_scaled_image, draw_text, play_sound, play_sound
from PIL import Image


class Button(pygame.sprite.Sprite):
    def __init__(self, image, pos, action, *groups, scale=5):
        super().__init__(*groups)
        self.orig_image = image
        self.image1 = image
        self.scale = scale
        image = get_scaled_image(image, scale)
        self.rect = image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.action = action
        self.sound = False

    def get_pos(self):
        im = Image.open(self.image1)
        width, height = self.pos
        width1, height1 = im.size

        return (width, height, width1, height1)

    def update(self, *args, **kwargs) -> None:
        cof = self.scale
        if self.check_focus():
            cof = round(cof * 1.1)
        self.image = get_scaled_image(self.orig_image, cof)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def check_focus(self):
        if self.rect.collidepoint(*pygame.mouse.get_pos()):
            if self.sound:
                play_sound('select_button.mp3')
                self.sound = False
            return True
        self.sound = True
        pygame.time.delay(100)
        return False


class CoinCounter(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super(CoinCounter, self).__init__(*groups)
        self.pos = pos
        self.image = pygame.surface.Surface((160, 40))
        self.image.set_colorkey("grey")

        self.rect = self.image.get_rect()
        self.rect.topleft = pos

        self.coins = 0
        self.text_size = 50

        self.update_image()

    def update(self, *args, **kwargs) -> None:
        n = kwargs["player_coins"]
        self.set_coins(n)

    def add_coins(self, n=1):
        self.coins += 1
        self.update_image()

    def set_coins(self, n):
        if n != self.coins:
            self.coins = n
            self.update_image()

    def update_image(self):
        self.image.fill("grey")
        self.image.blit(get_scaled_image(load_image(r"others\coin.png"), 5), (0, 0))
        draw_text(self.image, str(self.coins), self.text_size, (40, 0), color=(255, 215, 0),
                  font_name=r"data/fonts/Teletactile.ttf")
