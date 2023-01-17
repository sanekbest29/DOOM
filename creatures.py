import pygame

from additional import *
from random import choice, randint


class Creature(pygame.sprite.Sprite):
    def __init__(self, image, pos, *groups, scale=BASE_SCALE, is_rigid=False, right=True):
        super().__init__(*groups)
        self.orig_image = get_scaled_image(image, scale)

        self.scale = scale
        self.image = self.orig_image
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = pos
        self.rigid = is_rigid
        self.right = right


class Tile(Creature):
    def __init__(self, pos, *groups, scale=BASE_SCALE):
        super().__init__(load_image(r"tiles\tile1.png"), pos, *groups, scale=scale, is_rigid=True)

class Spawn_Tile(Creature):
    def __init__(self, pos, *groups, scale=BASE_SCALE):
        super().__init__(load_image(r"tiles\spawner.png"), pos, *groups, scale=scale, is_rigid=True)


class MovingCreature(Creature):
    def __init__(self, image, pos, *groups, scale=BASE_SCALE, is_rigid=False, right=True, has_mass=True):
        super(MovingCreature, self).__init__(image, pos, *groups, scale=scale, is_rigid=is_rigid,
                                             right=right)
        self.xvel = 0
        self.yvel = 0
        self.on_ground = False
        self.xdir = 0  # лево, на месте или право
        self.effects = []
        self.effects_force = (0, 0)
        self.has_mass = has_mass

    def update(self, *args, **kwargs):
        self.move()
        self.update_effects()
        self.on_ground = False

        self.xvel += self.effects_force[0]
        self.yvel += self.effects_force[1]

        self.rect.x += self.xvel
        self.collide(self.xvel, 0)
        self.rect.y += self.yvel
        self.collide(0, self.yvel)

        if not self.on_ground and self.has_mass:
            self.yvel += GRAVITY / 60

    def move(self):
        pass

    def update_effects(self):

        self.effects_force = (0, 0)
        for effect in self.effects:
            effect.update()
            if effect.duration <= 0:
                self.effects.remove(effect)

    def collide(self, xvel, yvel):
        if self.rect.x + self.rect.width // 2 < 0:
            self.rect.x = -self.rect.width // 2
            self.xvel = 0
        elif self.rect.x + self.rect.width // 2 > WIDTH:
            self.rect.x = WIDTH - self.rect.width // 2 - 1
            self.xvel = 0

        for g in self.groups():
            p: Creature
            for p in g:
                if id(p) == id(self):
                    continue
                if p.rigid and p.rect.collidepoint(self.rect.bottomleft[0] + self.rect.w // 2,
                                                   self.rect.bottomleft[1] + 1):
                    self.on_ground = True
                if pygame.sprite.collide_rect(self, p):  # если есть пересечение платформы с игроком
                    if isinstance(p, LivingCreature):
                        self.collide_action(p)
                    if not p.rigid:  # проверяем только "твёрдые" спрайты
                        continue
                    if xvel > 0:  # если движется вправо
                        self.rect.right = p.rect.left  # то не движется вправо
                        self.xvel = 0

                    if xvel < 0:  # если движется влево
                        self.rect.left = p.rect.right  # то не движется влево
                        self.xvel = 0

                    if yvel > 0:  # если падает вниз
                        self.rect.bottom = p.rect.top  # то не падает вниз
                        self.on_ground = True  # и становится на что-то твердое
                        self.yvel = 0  # и энергия падения пропадает

                    if yvel < 0:  # если движется вверх
                        self.rect.top = p.rect.bottom  # то не движется вверх
                        self.yvel = 0  # и энергия прыжка пропадает

    def collide_action(self, target):
        pass


class LivingCreature(MovingCreature, AnimatedSprite):
    def __init__(self, pos, *groups, image=load_image(r"tiles\tile1.png", colorkey=-1), health=100, col=1, row=1,
                 scale=BASE_SCALE):
        im = get_scaled_image(image, scale)
        self.set_frames(im, col, row)
        super().__init__(self.frames[0], pos, *groups, scale=1, is_rigid=False)
        self.jump_power = 13

        self.speed = 5
        self.weapon = None

        self.animation_tick = 0
        self.animation_speed = 15001

        self.health = health
        self.max_health = health

        self.invulnerable = 0
        self.invulnerable_time = 2

    def update_effects(self):
        if self.is_invulnerable():
            self.invulnerable -= 1 / FPS
        super(LivingCreature, self).update_effects()

    def update(self, *args, **kwargs):
        super(LivingCreature, self).update(*args, **kwargs)

        if self.animation_tick > 1000:
            self.animation_tick = 0
            self.update_frame()
        self.set_image()

        self.pos = (self.rect.x, self.rect.y)

        self.draw_health_bar(args[0])

    def move(self):
        pass

    def set_image(self):
        if self.is_invulnerable():
            if self.invulnerable * 20 % 4 <= 1:
                self.image = self.image.copy()
                self.image.set_alpha(30)
                return
        self.animation_tick += self.animation_speed / FPS
        if self.right and self.xdir == 0:
            self.image = pygame.transform.flip(self.frames[0], True, False)
        elif self.xdir == 0:
            self.image = self.frames[0]
        elif self.right and self.xdir == 1:
            self.image = pygame.transform.flip(self.frames[self.cur_frame], True, False)

    def get_effect(self, effect):
        if not self.is_invulnerable():
            self.effects.append(effect)

    def jump(self):
        if self.on_ground:  # прыгаем, только когда можем оттолкнуться от земли
            self.yvel = -self.jump_power

    def is_invulnerable(self):
        return self.invulnerable > 0

    def get_damage(self, dm):
        if self.is_invulnerable():
            return
        self.invulnerable = self.invulnerable_time
        self.health -= dm
        if self.health <= 0:
            self.die()

    def die(self):
        if self.weapon is not None:
            self.weapon.kill()
        self.kill()

    def use_weapon(self):
        if self.weapon is not None:
            self.weapon.activate()

    def heal(self, n):
        self.health += n
        if self.health > self.max_health:
            self.health = self.max_health

    def draw_health_bar(self, screen):
        a = (self.health / self.max_health - 0.5) * 255

        if a > 0:
            r = 255 - a
            g = 255
        else:
            r = 255
            g = 255 + a * 2
        if r > 255:
            r = 255
        if r < 0:
            r = 0
        pygame.draw.rect(screen, pygame.color.Color(int(r), int(g), 0), (self.rect.x, self.rect.y - 12,
                                                                         self.rect.width * self.health // self.max_health,
                                                                         10))
        pygame.draw.rect(screen, "black", (self.rect.x, self.rect.y - 12, self.rect.width, 10), width=2)


class Player(LivingCreature):
    def __init__(self, pos, *groups):
        super(Player, self).__init__(pos, *groups, image=load_image(r"hero\hero.png"), col=4)
        self.coins = 0

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.jump()
        if keys[pygame.K_a]:
            self.xdir = -1
            self.right = False
        elif keys[pygame.K_d]:
            self.xdir = 1
            self.right = True
        else:
            self.xdir = 0
        self.xvel = self.speed * self.xdir

    def get_coins(self, n=1):
        s = pygame.mixer.Sound(r"data\sounds\get_coin.ogg")
        s.play(loops=0)
        self.coins += 1

    def die(self):
        super(Player, self).die()
        if self.coins > int(get_stat("record")):
            set_stat("record", self.coins)
        pygame.time.set_timer(GAME_OVER, 1000, 1)

    def get_damage(self, dm):
        if not self.is_invulnerable():
            s = pygame.mixer.Sound(r"data\sounds\get_damage_8bit.mp3")
            s.set_volume(0.5)
            s.play(loops=0)
        super().get_damage(dm)


class Weapon(Creature):
    def __init__(self, owner: Creature, *groups, scale=BASE_SCALE, reload_speed=1000, level=1,
                 image=load_image(r"tiles\tile1.png")):
        super().__init__(image, owner.pos, *groups, scale=scale, is_rigid=False)
        self.owner = owner
        self.level = level
        self.reload_speed = reload_speed
        self.reload_tick = 0
        self.power = 20
        self.fire_sound = None
        self.fire_sound_duration = None

    def update(self, *args, **kwargs) -> None:
        self.set_pos()
        self.reload_tick += self.reload_speed / FPS

    def set_pos(self):
        self.pos = self.owner.rect.center
        if self.owner.right:
            self.pos = (self.pos[0] + self.owner.rect.width // 2, self.pos[1] - self.owner.rect.height // 4)
            self.image = self.orig_image
        else:
            self.pos = (self.pos[0] - self.owner.rect.width // 2, self.pos[1] - self.owner.rect.height // 4)
            self.image = pygame.transform.flip(self.orig_image, True, False)
        self.rect.y = self.pos[1]
        self.rect.x = self.pos[0] - self.rect.width // 2

    def activate(self):
        if self.reload_tick >= 1000:
            self.reload_tick = 0
            self.fire()

    def fire(self):
        self.play_fire_sound()
        b = Bullet(self, load_image(r"tiles\tile1.png"), *self.groups(), damage=self.power)

    def play_fire_sound(self):
        if self.fire_sound is not None:
            if self.fire_sound_duration is not None:
                s = pygame.mixer.Sound(self.fire_sound)
                s.set_volume(0.5)
                s.play(loops=0, maxtime=self.fire_sound_duration)
            else:
                s = pygame.mixer.Sound(self.fire_sound)
                s.set_volume(0.5)
                s.play(loops=0)


class Gun(Weapon):
    def __init__(self, owner: Creature, *groups, scale=BASE_SCALE, reload_speed=1000, level=1):
        super(Gun, self).__init__(owner, *groups, scale=scale, reload_speed=reload_speed, level=1,
                                  image=load_image(r"weapons\rifle.png"))
        self.fire_sound = r"data\sounds\gun_with_silencer.mp3"
        self.fire_sound_duration = 400
        self.power = 40

    def update(self, *args, **kwargs) -> None:
        super(Gun, self).update(*args, **kwargs)
        if self.owner.right:
            self.rect.x += 15
        else:
            self.rect.x -= 15

    def fire(self):
        self.play_fire_sound()
        b = Bullet(self, load_image(r"weapons\bullet.png"), *self.groups(), speed=15, distanse=1200,
                   damage=self.power + self.level)


class Bullet(Creature):
    def __init__(self, weapon: Weapon, image, *groups, speed=10, damage=10, distanse=1000, scale=BASE_SCALE):
        if weapon.owner.right:
            self.pos = weapon.rect.topright
            self.right = True
        else:
            self.pos = weapon.rect.topleft
            self.right = False
        super().__init__(image, self.pos, *groups, scale=scale, is_rigid=False, right=self.right)
        if not self.right:
            self.pos = (self.pos[0] - self.rect.width, self.pos[1])
        self.weapon = weapon
        self.speed = speed
        self.damage = damage
        self.distance = distanse

    def update(self, *args, **kwargs) -> None:
        self.distance -= self.speed

        if self.distance <= 0:
            self.kill()
            return
        if self.right:
            self.pos = (self.pos[0] + self.speed, self.pos[1])
        else:
            self.pos = (self.pos[0] - self.speed, self.pos[1])
        self.rect.topleft = self.pos
        self.collide()

    def collide(self):
        for p in self.groups()[0]:
            if pygame.sprite.collide_rect(self, p):
                if isinstance(p, LivingCreature):
                    if isinstance(self.weapon.owner, Enemy) and isinstance(p, Enemy):
                        continue
                    p.get_damage(self.damage)
                    self.kill()
                elif p.rigid:  # проверяем только "твёрдые" спрайты
                    self.kill()


class Enemy(LivingCreature):
    def __init__(self, pos, *groups, image=load_image(r"hero\hero.png"), col=4, row=1, drop=None):
        super(Enemy, self).__init__(pos, *groups, image=image, col=col, row=row)
        self.jump_chance = 3
        self.drop = drop
        self.use_weapon_chance = 5

    def move(self):
        if roulette(self.jump_chance):
            self.jump()
        if self.xvel == 0:
            self.right = not self.right
        if self.right:
            self.xdir = 1
        else:
            self.xdir = -1

        self.xvel = self.speed * self.xdir

    def update(self, *args, **kwargs):
        super(Enemy, self).update(*args, **kwargs)
        if roulette(self.use_weapon_chance):
            self.use_weapon()

    def die(self):
        if self.drop is not None:
            p = self.rect.center
            p = (p[0], p[1] - self.rect.h // 3)
            drop = self.drop(p, *self.groups())
        super(Enemy, self).die()


class Slime(Enemy):
    def __init__(self, pos, *groups, drop=None):
        super(Slime, self).__init__(pos, *groups, image=load_image(r"enemies\slime.png"), col=2, drop=drop)
        self.animation_speed = 6000
        self.power = 20
        self.invulnerable_time = 0
        self.speed = 4

    def set_image(self):
        if self.yvel < 0:
            self.cur_frame = 0
        super(Slime, self).set_image()

    def collide_action(self, target):
        if isinstance(target, Player):
            target.get_effect(Knockback(self, target))
            target.get_damage(self.power)
        elif isinstance(target, Slime):
            for ef in target.effects:
                if id(ef.dealer) == id(self):
                    return
            kb = Knockback(self, target, power=4)
            target.xvel = 0
            target.get_effect(kb)


class Loot(MovingCreature):
    pass


class Coin(Loot):
    def __init__(self, pos, *groups):
        super(Coin, self).__init__(load_image(r"others\coin.png"), pos, *groups)
        self.cost = 1

    def collide_action(self, target):
        if isinstance(target, Player):
            target.get_coins()
            self.kill()


class Heart(Loot):
    def __init__(self, pos, *groups):
        super(Heart, self).__init__(load_image(r"others\heart.png"), pos, *groups)
        self.power = 20

    def collide_action(self, target):
        if isinstance(target, Player):
            target.heal(self.power)
            s = pygame.mixer.Sound(r"data\sounds\heal.mp3")
            s.play(loops=0)
            self.kill()


class EnemySpawner:
    # mobs = [(Slime, 30(chance)), (Zombie, 10)]
    def __init__(self, spawn_points: list, group: pygame.sprite.Group, mobs):
        self.spawn_points = spawn_points
        self.group = group
        self.enemies = []
        self.mobs = mobs
        for i in range(1, len(mobs)):
            self.mobs[i] = (self.mobs[i][0], self.mobs[i][1] + self.mobs[i - 1][1])
        self.sum_chance = sum([i[1] for i in self.mobs])
        self.tiles = len(self.group)

    def spawn_mob(self):
        n = randint(0, self.sum_chance)
        for i in self.mobs:
            if i[1] >= n:
                mob = i[0]
        spawn_point = choice(self.spawn_points)
        sprite: Enemy
        if roulette(85):
            dr = Coin
        else:
            dr = Heart

        sprite = mob(spawn_point, self.group, drop=dr)
        if isinstance(sprite, Slime):
            if roulette(6):
                sprite.weapon = Gun(sprite, self.group)
        sprite.right = choice([True, False])

    def update(self):
        cur_mobs = len(self.group) - self.tiles
        if cur_mobs == 0:
            self.spawn_mob()
        elif cur_mobs <= 3:
            if roulette(3 * FPS / 60):
                self.spawn_mob()
        elif cur_mobs <= 10:
            if roulette(0.7 * FPS / 60):
                self.spawn_mob()
        elif cur_mobs <= 30:
            if roulette(0.5 * FPS / 60):
                self.spawn_mob()
        else:
            if roulette(0.1 * FPS / 60):
                self.spawn_mob()


def generate_level(level, *groups, tile_size=TILE_SIZE):
    new_player, x, y = None, None, None
    spawn_points = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                pass
            elif level[y][x] == '#':
                Tile((x * tile_size, y * tile_size), *groups)
            elif level[y][x] == '@':
                new_player = Player((x * tile_size, y * tile_size), *groups)
            elif level[y][x] == 's':
                Spawn_Tile((x * tile_size, y * tile_size), *groups)
                spawn_points.append((x * tile_size, y * tile_size))

    return new_player, x, y, spawn_points
