import pygame
import os
import sys
from load_image import load_image
import pytmx
import random


class Map:
    def __init__(self, filename, tile_size):
        self.map = pytmx.load_pygame(f"data/maps/{filename}")
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = tile_size

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                image1 = self.map.get_tile_image(x, y, 0)
                image2 = self.map.get_tile_image(x, y, 1)
                if image1:
                    screen.blit(image1, (x * self.tile_size, y * self.tile_size))

                if image2:
                    screen.blit(image2, (x * self.tile_size, y * self.tile_size))

    def get_tile_id(self, pos):
        return self.map[pos[1]][pos[0]]


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, x, y, scale=1.5):
        super().__init__(player_group)
        self.x = x
        self.y = y
        self.frames = []
        self.cut_sheet(load_image(f"png/walkcycle/{sheet}"), 9, 4, scale)
        self.cut_sheet(load_image(f"png/slash/{sheet}"), 6, 4, scale)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.direction = 'up'
        self.up = self.frames[0:9]
        self.left = self.frames[9:18]
        self.down = self.frames[18:27]
        self.right = self.frames[27:36]

        self.sup = self.frames[36:42]
        self.sleft = self.frames[42:48]
        self.sdown = self.frames[48:54]
        self.sright = self.frames[54:60]
        self.slashing = False
        self.slash_frame = 0
        self.slash_duration = 9

        self.health = Health(400, 80, 200, 20, 10)

    def load_image(self, name, colorkey=None):
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        return image

    def cut_sheet(self, sheet, columns, rows, scale):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                scaled_frame = pygame.transform.scale(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)),
                    (self.rect.w * scale, self.rect.h * scale))
                self.frames.append(scaled_frame)

    def move(self, x, y):
        self.x += x
        self.y += y

    def slash(self, kills):
        try:
            if not self.slashing:
                self.slashing = True
                self.slash_frame = 0
            slashed_enemy = pygame.sprite.spritecollideany(self, enemy_group)
            if slashed_enemy:
                slashed_enemy.health.hp -= 1
                if slashed_enemy.health.hp == 0:
                    slashed_enemy.explode()
                    kills += 1


        except AttributeError:
            pass

        finally:
            return kills

    def update(self, dest):
        self.rect.x = self.x
        self.rect.y = self.y

        if self.slashing:
            if self.direction == 'up':
                self.image = self.sup[self.slash_frame]
            elif self.direction == 'down':
                self.image = self.sdown[self.slash_frame]
            elif self.direction == 'left':
                self.image = self.sleft[self.slash_frame]
            elif self.direction == 'right':
                self.image = self.sright[self.slash_frame]

            self.slash_frame += 1
            if self.slash_frame >= len(self.sup):
                self.slashing = False
                self.slash_frame = 0
        else:
            if dest == 'up':
                self.direction = 'up'
                self.cur_frame = (self.cur_frame + 1) % len(self.up)
                self.image = self.up[self.cur_frame]
            elif dest == 'left':
                self.direction = 'left'
                self.cur_frame = (self.cur_frame + 1) % len(self.left)
                self.image = self.left[self.cur_frame]
            elif dest == 'down':
                self.direction = 'down'
                self.cur_frame = (self.cur_frame + 1) % len(self.down)
                self.image = self.down[self.cur_frame]
            elif dest == 'right':
                self.direction = 'right'
                self.cur_frame = (self.cur_frame + 1) % len(self.right)
                self.image = self.right[self.cur_frame]


class Enemy(pygame.sprite.Sprite):
    def __init__(self, sheet, x, y, columns, rows, scale=1.5):
        super().__init__(enemy_group)
        self.x = x
        self.y = y
        self.sheet = sheet
        self.frames = []
        self.cut_sheet(load_image(f"enemies/{sheet}"), columns, rows, scale)
        self.frame_group_1 = self.frames[0:columns]
        self.frame_group_2 = self.frames[columns:columns * 2]
        self.frame_group_3 = self.frames[columns * 2:columns * 3]
        self.frame_group_4 = self.frames[columns * 3:columns * 4]
        sf = []
        sf.append(self.frame_group_1)
        sf.append(self.frame_group_2)
        sf.append(self.frame_group_3)
        sf.append(self.frame_group_4)
        self.frames = []
        self.frames = sf[random.randint(0, 3)]
        self.health = Health(self.rect.x + 22, self.rect.y - 20, 50, 10, 3)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

        self.animation_speed = 0.2
        self.frame_time = 0
        self.is_exploding = False
        self.explode_frame = 0
        self.explode_duration = 11
        self.explodion_shift = 0

    def load_image(self, name, colorkey=None):
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        return image

    def cut_sheet(self, sheet, columns, rows, scale):
        self.rect = pygame.Rect(self.x, self.y, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                scaled_frame = pygame.transform.scale(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)),
                    (self.rect.w * scale, self.rect.h * scale))
                self.frames.append(scaled_frame)

    def update(self):
        if self.is_exploding:
            self.frame_time += 1 / FPS
            if self.frame_time >= self.animation_speed:
                self.explode_frame += 1
                if self.explode_frame >= len(self.frames):
                    self.kill()
                    return
                else:
                    self.image = self.frames[self.explode_frame]

                self.frame_time = 0
        else:
            self.frame_time += 1 / FPS
            if self.frame_time >= self.animation_speed:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
                if self.image == self.frames[4]:
                    p = pygame.sprite.spritecollideany(self, player_group)
                    if p and p.health.hp > 0:
                        p.health.hp -= 1
                        if player.health.hp == 0:
                            return True
                self.frame_time = 0
                if self.sheet == 'bee.png':
                    self.health.update_position(self.rect.x, self.rect.y - 20)
                else:
                    self.health.update_position(self.rect.x + 22, self.rect.y - 20)
        try:
            self.health.draw(screen)
        except AttributeError:
            pass

        return False

    def explode(self):
        self.is_exploding = True
        self.animation_speed = 0.05
        self.explode_frame = 0
        self.frames = []
        self.cut_sheet(load_image(f"particles/explosion.png"), 12, 1, 1.5)
        self.rect = self.rect.move(self.x - 30, self.y - 20)
        self.health = None


class Health:
    def __init__(self, x, y, w, h, max_hp):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hp = max_hp
        self.max_hp = max_hp

    def update_position(self, x, y):
        self.x = x
        self.y = y

    def draw(self, surface):
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, "white", (self.x, self.y, self.w, self.h), border_radius=5)

        for i in range(int(self.w * ratio)):
            color = (int(255 * (1 - i / (self.w * ratio))), int(255 * (i / (self.w * ratio))), 0)
            pygame.draw.rect(surface, color, (self.x + i, self.y, 1, self.h), border_radius=5)

        pygame.draw.rect(surface, "white", (self.x, self.y, self.w, self.h), 2, border_radius=5)


class Button:
    def __init__(self, x, y, w, h, text, font):
        self.btn = pygame.Surface((250, 50))
        self.btn_text = font.render(text, True, (0, 0, 0))
        self.btn_text_rect = self.btn_text.get_rect(
            center=(self.btn.get_width() / 2,
                    self.btn.get_height() / 2))
        self.btn_rect = pygame.Rect(x, y, w, h)

    def collidebtn(self, mouse):
        if self.btn_rect.collidepoint(mouse):
            pygame.draw.rect(self.btn, (200, 200, 200), (1, 1, 248, 48))
        else:
            pygame.draw.rect(self.btn, (0, 0, 0), (0, 0, 250, 50))
            pygame.draw.rect(self.btn, (255, 255, 255), (1, 1, 248, 48))
            pygame.draw.rect(self.btn, (0, 0, 0), (1, 1, 248, 1), 2)
            pygame.draw.rect(self.btn, (0, 100, 0), (1, 48, 248, 10), 2)

    def blitting(self):
        self.btn.blit(self.btn_text, self.btn_text_rect)
        screen.blit(self.btn, (self.btn_rect.x, self.btn_rect.y))


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["SKELE-HERO",
                  "RULES:",
                  "Kill the",
                  "most enemies",
                  "within a",
                  "given time."]

    c_enemy_txt = 'Choose enemy'

    fon = load_image('start/fon5.jpg')
    fon = pygame.transform.scale(fon, (fon.get_width(), fon.get_height()))
    screen.blit(fon, (0, 0))

    dungeon_font = "data/dungeon_font/ThaleahFat.ttf"
    font = pygame.font.Font(dungeon_font, 50)
    font2 = pygame.font.Font(dungeon_font, 30)
    button_group = []
    start_button = Button(5, 400, 250, 50, "NEW GAME", font2)
    eyeball_button = Button(350, 100, 400, 100, "EYEBALL", font2)
    pumpking_button = Button(350, 180, 400, 100, "PUMPKING", font2)
    bee_button = Button(350, 260, 400, 100, "BEE", font2)

    button_group.append(start_button)
    button_group.append(eyeball_button)
    button_group.append(pumpking_button)
    button_group.append(bee_button)

    enemy_type = 'eyeball'

    text_coord = 50
    c_enemy_txt_rendered = font.render(c_enemy_txt, 1, pygame.Color("white"))
    c_enemy_rect = c_enemy_txt_rendered.get_rect()
    screen.blit(c_enemy_txt_rendered, c_enemy_rect.move(350, 50))

    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.btn_rect.collidepoint(pygame.mouse.get_pos()):
                    return enemy_type

                if eyeball_button.btn_rect.collidepoint(pygame.mouse.get_pos()):
                    enemy_type = 'eyeball'

                if pumpking_button.btn_rect.collidepoint(pygame.mouse.get_pos()):
                    enemy_type = 'pumpking'

                if bee_button.btn_rect.collidepoint(pygame.mouse.get_pos()):
                    enemy_type = 'bee'

        pos = pygame.mouse.get_pos()
        for button in button_group:
            button.collidebtn(pos)
            button.blitting()

        pygame.display.flip()
        clock.tick(FPS)


size = width, height = 640, 480
FPS = 20
tile_width = tile_height = tile_size = 16
steps = 10
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()


def new_game(width, height, tile_size, player_group, enemy_group, enemy_type):
    for i in player_group:
        i.kill()
    for i in enemy_group:
        i.kill()
    player = Player("BODY_skeleton.png", width / 2 - 40, height / 2 - 50)
    weapon = Player("WEAPON.png", width / 2 - 40, height / 2 - 50)
    max_x = width // tile_size
    max_y = height // tile_size
    rx, ry = [_ for _ in range(1, 15)], [_ for _ in range(1, 10)]
    kills = 0
    random.shuffle(rx)
    random.shuffle(ry)
    for i in range(4):
        if enemy_type == "eyeball":
            enemy = Enemy("eyeball.png", rx[i] * tile_size, ry[i] * tile_size, 7, 4)
            enemy_group.add(enemy)
        if enemy_type == "pumpking":
            enemy = Enemy("pumpking.png", rx[i] * tile_size, ry[i] * tile_size, 6, 4)
            enemy_group.add(enemy)
        if enemy_type == "bee":
            enemy = Enemy("bee.png", rx[i] * tile_size, ry[i] * tile_size, 6, 4)
            enemy_group.add(enemy)

    player_group.add(player)
    player_group.add(weapon)
    health_flag = False
    stop = False
    return player, weapon, max_x, max_y, rx, ry, stop, kills, health_flag


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    map = Map("ma.tmx", tile_size)
    clock = pygame.time.Clock()

    enemy_type = start_screen()

    player, weapon, max_x, max_y, rx, ry, stop, kills, health_flag = new_game(width, height, tile_size,
                                                                              player_group, enemy_group, enemy_type)

    counter, text = 20, ' 20'
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    font = pygame.font.Font("data/dungeon_font/ThaleahFat.ttf", 60)
    button_surface = pygame.Surface((150, 50))
    font2 = pygame.font.Font("data\dungeon_font\ThaleahFat.ttf", 30)
    health_text = font2.render("health:", True, "white")
    new_game_text = font2.render("NEW GAME", True, (0, 0, 0))
    new_game_text_rect = new_game_text.get_rect(
        center=(button_surface.get_width() / 2,
                button_surface.get_height() / 2))
    button_rect = pygame.Rect(60, 110, 150, 50)
    running = True
    while running:
        if not stop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if (event.type == pygame.MOUSEBUTTONDOWN) or (event.type == pygame.KEYDOWN and event.key == pygame.K_e):
                    kills = player.slash(kills)

                if event.type == pygame.USEREVENT:
                    counter -= 1
                    if counter > 0:
                        text = " " + str(counter)
                    else:
                        text = ' GAME OVER'
                        screen.blit(font.render(text, 0, "white"), (32, 48))
                        stop = True

        if not stop:
            if not enemy_group:
                text = ' VICTORY'
                screen.fill('black')
                screen.blit(font.render(text, 0, "white"), (32, 48))
                stop = True

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[ord('a')]:
                if player.x > -10:
                    player.move(-steps, 0)
                    player.update('left')
                    weapon.move(-steps, 0)
                    weapon.update('left')
            elif keys[pygame.K_RIGHT] or keys[ord('d')]:
                if player.x < width - player.rect.width - 50:
                    player.move(steps, 0)
                    player.update('right')
                    weapon.move(steps, 0)
                    weapon.update('right')
            elif keys[pygame.K_UP] or keys[ord('w')]:
                if player.y > -35:
                    player.move(0, -steps)
                    player.update('up')
                    weapon.move(0, -steps)
                    weapon.update('up')
            elif keys[pygame.K_DOWN] or keys[ord('s')]:
                if player.y < height - player.rect.height - 100:
                    player.move(0, steps)
                    player.update('down')
                    weapon.move(0, steps)
                    weapon.update('down')

            player.update(None)
            weapon.update(None)

            for enemy in enemy_group:
                health_flag = enemy.update()
                if health_flag is True:
                    text = ' GAME OVER'
                    screen.blit(font.render(text, 0, "white"), (32, 48))
                    stop = True

            if player.slashing:
                if player.direction == 'up':
                    player.image = player.sup[player.slash_frame]
                    weapon.image = weapon.sup[player.slash_frame]
                elif player.direction == 'down':
                    player.image = player.sdown[player.slash_frame]
                    weapon.image = weapon.sdown[player.slash_frame]
                elif player.direction == 'left':
                    player.image = player.sleft[player.slash_frame]
                    weapon.image = weapon.sleft[player.slash_frame]
                elif player.direction == 'right':
                    player.image = player.sright[player.slash_frame]
                    weapon.image = weapon.sright[player.slash_frame]

                player.slash_frame += 1
                weapon.slash_frame += 1
                if player.slash_frame >= len(player.sup):
                    player.slashing = False
                    player.slash_frame = weapon.slash_frame = 0

            screen.fill((0, 0, 0))
            map.render(screen)
            enemy_group.draw(screen)
            tiles_group.draw(screen)
            player_group.draw(screen)
            player.health.draw(screen)
            for enemy in enemy_group:
                if enemy.health:
                    enemy.health.draw(screen)

            screen.blit(font.render(text, 0, "white"), (32, 48))
            screen.blit(font.render(str(kills), 0, "white"), (550, 370))
            screen.blit(health_text, (400, 50))

        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        player, weapon, max_x, max_y, rx, ry, stop, kills, health_flag = new_game(width, height,
                                                                                                  tile_size,
                                                                                                  player_group,
                                                                                                  enemy_group,
                                                                                                  enemy_type)
                        counter, text = 20, ' 20'

            if button_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(button_surface, (200, 200, 200), (1, 1, 148, 48))
            else:
                pygame.draw.rect(button_surface, (0, 0, 0), (0, 0, 150, 50))
                pygame.draw.rect(button_surface, (255, 255, 255), (1, 1, 148, 48))
                pygame.draw.rect(button_surface, (0, 0, 0), (1, 1, 148, 1), 2)
                pygame.draw.rect(button_surface, (0, 100, 0), (1, 48, 148, 10), 2)

            button_surface.blit(new_game_text, new_game_text_rect)
            screen.blit(button_surface, (button_rect.x, button_rect.y))
        pygame.display.flip()
        clock.tick(FPS)
