from other import Button, CoinCounter
from creatures import *
from additional import play_sound


class StartScene:
    def __init__(self, screen):
        self.screen = screen
        width, height = screen.get_size()

        running = True

        clock = pygame.time.Clock()
        scene_sprites = pygame.sprite.Group()
        buttons = pygame.sprite.Group()

        btn_start = Button(load_image(r"buttons\start_button.png"),
                           (width // 2, height // 2), self.load_game, buttons, scene_sprites)

        btn_shop = Button(load_image(r"buttons\shop_btn.png"),
                          (width // 2, (height // 2) + 70), self.load_shop, buttons, scene_sprites)

        play_sound('background_music.mp3', -1)

        while running:
            clock.tick(FPS)

            font = pygame.font.Font(None, 100)
            text = font.render("DOOM 2D", True, (255, 206, 82))
            text_x = width // 2 - text.get_width() // 2
            text_y = 100
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONUP:
                    for btn in buttons:
                        if btn.check_focus():
                            play_sound('push_button.mp3')
                            btn.action()
                if event.type == pygame.KEYDOWN:
                    self.load_game()

            screen.fill(pygame.color.Color((112, 0, 0)))
            screen.blit(text, (text_x, text_y))
            scene_sprites.update()
            scene_sprites.draw(screen)
            pygame.display.flip()

    def load_game(self) -> None:
        GameScene(self.screen)

    def load_shop(self) -> None:
        Shop(self.screen)


class GameScene:
    def __init__(self, screen):
        self.screen = screen

        running = True

        clock = pygame.time.Clock()

        creatures = pygame.sprite.Group()
        buttons = pygame.sprite.Group()
        interface = pygame.sprite.Group()

        level_name = choice(LEVELS)

        player, x, y, spawn_points = generate_level(load_level(level_name), creatures, tile_size=TILE_SIZE)
        player.weapon = Gun(player, creatures)
        counter = CoinCounter((WIDTH - 165, 5), interface)

        spawner = EnemySpawner(spawn_points, creatures, [(Slime, 10)])
        spawner.spawn_mob()

        space_pressed = False

        while running:
            clock.tick(FPS)
            spawner.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    terminate()
                if event.type == pygame.MOUSEBUTTONUP:
                    for btn in buttons:
                        if btn.check_focus():
                            btn.action()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        space_pressed = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        space_pressed = False

                if event.type == GAME_OVER:
                    running = False

            if space_pressed:
                player.use_weapon()

            screen.fill(pygame.color.Color((227, 73, 45)))

            creatures.update(screen)
            creatures.draw(screen)

            interface.update(player_coins=player.coins)
            interface.draw(screen)

            pygame.display.flip()
        Shop(self.screen, counter.coins)


class Shop:
    def __init__(self, screen, score=None):
        self.screen = screen
        width, height = screen.get_size()
        record = get_stat("record")
        running = True

        record = get_stat("record")
        clock = pygame.time.Clock()
        scene_sprites = pygame.sprite.Group()
        buttons = pygame.sprite.Group()

        btn_pistol = Button(load_image(r"buttons\set_btn.png"),
                            (WIDTH // 4, (height // 2) + 100), self.load_game, buttons, scene_sprites)

        btn_rifle = Button(load_image(r"buttons\set_btn.png"),
                           (WIDTH - (WIDTH // 4), (height // 2) + 100), self.load_game, buttons, scene_sprites)

        btn_start = Button(load_image(r"buttons\start_button.png"),
                           (width // 2, (height // 2) + 500), self.load_game, buttons, scene_sprites)

        while running:
            clock.tick(FPS)

            font = pygame.font.Font(None, 100)
            text = font.render("GUN SHOP", True, (255, 206, 82))
            text_x = width // 2 - text.get_width() // 2
            text_y = 100

            interface = pygame.sprite.Group()

            counter = CoinCounter((WIDTH - 165, 5), interface)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONUP:
                    for btn in buttons:
                        if btn.check_focus():
                            play_sound('push_button.mp3')
                            btn.action()
                if event.type == pygame.KEYDOWN:
                    self.load_game()

            screen.fill(pygame.color.Color((112, 0, 0)))
            screen.blit(text, (text_x, text_y))
            draw_text(self.screen, "PISTOL", 40, (WIDTH // 4, height // 2), center=True)
            draw_text(self.screen, "RIFLE (COST 50 MONEY)", 40, (WIDTH - (WIDTH // 4), height // 2), center=True)

            scene_sprites.update()
            scene_sprites.draw(screen)

            interface.update(player_coins=record)
            interface.draw(screen)

            pygame.display.flip()

    def load_game(self) -> None:
        GameScene(self.screen)
