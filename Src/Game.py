import sys, os, json, random, math

import pygame as pg
import pygame_gui as pg_gui
from PIL import Image
import numpy as np

from .Player import Player
from .Tree import Tree
from .Coin import Coin
from .Color import WHITE

class Game:

    def __init__(self, frame_rate: int = 30):

        pg.init()

        self.current_level = 1

        self.FPS = frame_rate
        self.clock = clock = pg.time.Clock()
        self.time_elapsed = pg.time.get_ticks()

        self.screen_size = self.width, self.height = self.screen_width, self.screen_height = 400, 700

        self.screen = pg.display.set_mode(self.screen_size)
        self.manager = pg_gui.UIManager(self.screen_size, "Src/theme.json")

        self.running = True
        self.in_menu = True
        self.pause = False

        self.load_textures()

        self.init_ui()

        self.reset()

    def init_ui(self):

        self.start_btn = pg_gui.elements.UIButton(
            relative_rect=pg.Rect((self.screen_width/2 - 100, 275), (200, 50)),
            text='Play',
            manager=self.manager,
            object_id=pg_gui.core.ObjectID(
                class_id='@menu_btn',
                object_id='#start_btn'
            )
        )

        self.quit_btn = pg_gui.elements.UIButton(
            relative_rect=pg.Rect((self.screen_width/2 - 100, 330), (200, 50)),
            text='Quit',
            manager=self.manager,
            object_id=pg_gui.core.ObjectID(
                class_id='@menu_btn',
                object_id='#quit_btn'
            )
        )

        self.title = pg_gui.elements.UILabel(
            relative_rect=pg.Rect((self.screen_width/2 - 200, 200), (400, 50)),
            text='Ski runner',
            manager=self.manager,
            object_id=pg_gui.core.ObjectID(
                class_id='@menu_label',
                object_id='#title'
            )
        )

        self.coin_counter_label = pg_gui.elements.UILabel(
            relative_rect=pg.Rect((1, 1), (200, 40)),
            text='0',
            manager=self.manager,
            object_id=pg_gui.core.ObjectID(
                class_id='@game_label',
                object_id='#coin_counter'
            ),
            visible=False
        )

        self.speed_counter_label = pg_gui.elements.UILabel(
            relative_rect=pg.Rect((1, 25), (200, 50)),
            text='0',
            manager=self.manager,
            object_id=pg_gui.core.ObjectID(
                class_id='@game_label',
                object_id='#speed_counter'
            ),
            visible=False
        )

        self.gameover_panel = pg_gui.elements.UIPanel(
            relative_rect=pg.Rect((self.screen_width/2 - 150, 100), (300, 250)),
            manager=self.manager,
            object_id=pg_gui.core.ObjectID(
                class_id='@gameover',
                object_id='#gameover_panel'
            ),
            visible=False,
            starting_layer_height = 3
        )

        self.gameover_title = pg_gui.elements.UILabel(
            relative_rect=pg.Rect((50, 20), (200, 50)),
            text='Game Over',
            manager=self.manager,
            object_id=pg_gui.core.ObjectID(
                class_id='@gameover',
                object_id='#gameover_title'
            ),
            container = self.gameover_panel,
            visible = False
        )

        self.gameover_replay_btn = pg_gui.elements.UIButton(
            relative_rect=pg.Rect((75, 80), (150, 50)),
            text='Play Again',
            manager=self.manager,
            object_id=pg_gui.core.ObjectID(
                class_id='@gameover_btn',
                object_id='#gameover_replay_btn'
            ),
            visible = False,
            container = self.gameover_panel
        )

        self.gameover_tomenu_btn = pg_gui.elements.UIButton(
            relative_rect=pg.Rect((75, 140), (150, 50)),
            text='Menu',
            manager=self.manager,
            object_id=pg_gui.core.ObjectID(
                class_id='@gameover_btn',
                object_id='#gameover_tomenu_btn'
            ),
            visible = False,
            container = self.gameover_panel
        )

        self.menu_elements = [
            self.start_btn,
            self.quit_btn,
            self.title,
        ]

        self.game_elements = [
            self.coin_counter_label,
            self.speed_counter_label,
        ]

    def reset(self):
        self.camera_X = 0
        self.camera_Y = 0

        self.speed_Y = 4
        self.speed_X = 4

        self.player = Player(self.screen_width / 2, 100)
        self.trees = pg.sprite.Group()
        self.coins = pg.sprite.Group()

        self.coin_counter = 0
        self.coin_counter_label.set_text("Coins: ")
        self.speed_counter_label.set_text("Speed: ") 

    def load_textures(self):

        self.player_texture_right = pg.image.load("assets/skier.png")
        self.player_texture_left = pg.transform.flip(self.player_texture_right, True, False)
        self.tree_texture = pg.image.load("assets/tree.png")
        self.coin_texture = pg.image.load("assets/coin.png")

    def load_level(self, level_id: int):

        level_path = f"levels/{level_id}.level.png"
        metadata_path = f"levels/{level_id}.metadata.json"

        if not os.path.isfile(level_path) or not os.path.isfile(metadata_path):
            raise ValueError(f"The level {level_id} can't be loaded.")

        with open(metadata_path, "r") as file:
            metadata = json.loads(file.read())

        nb_rows = metadata["nb_rows"]
        nb_columns = metadata["nb_columns"]

        img = Image.open(level_path)
        arr = np.array(img)
        self.level = np.ndarray(
            shape=(nb_rows, nb_columns), 
            dtype=int
        )

        first_tree_placed = False

        for row in range(nb_rows):
            for el in range(nb_columns):
                if arr[row][el][3] != 0:
                    first_tree_placed = True
                    new_tree = Tree(el * 20 + 10, row * 20 + 10)
                    self.trees.add(new_tree)
                elif first_tree_placed and random.randint(0, 50) == 0:
                    new_coin = Coin(el * 20 + 10, row * 20 + 10)
                    self.coins.add(new_coin)

    def game_over(self):

        self.pause = True

        for el in self.game_elements:
            el.hide()
        self.gameover_panel.show()

    def to_menu(self):
        
        self.pause = False
        self.gameover_panel.hide()

        self.in_menu = True
        for el in self.menu_elements:
            el.show()
        
    def play_again(self):
        
        self.pause = False
        self.gameover_panel.hide()
        self.reset()
        self.load_level(self.current_level)

        for el in self.game_elements:
            el.show()

    def start_game(self):
        self.in_menu = False
        for el in self.menu_elements:
            el.hide()
        for el in self.game_elements:
            el.show()

        self.reset()
        self.load_level(self.current_level)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            self.manager.process_events(event)

            if event.type == pg_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.start_btn:
                    self.start_game()
                if event.ui_element == self.quit_btn:
                    self.running = False
                if event.ui_element == self.gameover_replay_btn:
                    self.play_again()
                if event.ui_element == self.gameover_tomenu_btn:
                    self.to_menu()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.speed_Y -= 0.1
                    if abs(self.speed_X) > 0.2:
                        if self.speed_X > 0:
                            self.speed_X = - self.speed_X + 0.1
                        else :
                            self.speed_X = - self.speed_X -  0.1
                    else:
                        self.speed_X *= -1
                    
    def update(self):

        self.player.pos[0] += self.speed_X
        self.player.pos[1] += self.speed_Y

        self.speed_Y += 0.005
        if self.speed_X > 0:
            self.speed_X += 0.005
        else:
            self.speed_X -= 0.005

        self.speed_counter_label.set_text(f"Speed: {round(self.speed_Y * math.sqrt(2), 1)}")

        self.player.rect.center = tuple(self.player.pos)

        self.camera_Y += self.speed_Y

        # Test collison

        trees_collided = any((
            self.player.pos[0] < 0,
            self.player.pos[0] > self.width,
            pg.sprite.spritecollide(self.player, self.trees, False)
        ))

        if trees_collided:
            self.game_over()

        coins_collided = pg.sprite.spritecollide(self.player, self.coins, True)

        self.coin_counter += len(coins_collided)

    def draw(self):
        # Draw
        self.screen.blit(
            self.player_texture_right if self.speed_X > 0 else self.player_texture_left,
            self.player.rect.move(-self.camera_X, -self.camera_Y)
        )

        for tree in self.trees.sprites():
            self.screen.blit(self.tree_texture, tree.rect.move(-self.camera_X, -self.camera_Y))

        for coin in self.coins.sprites():
            self.screen.blit(self.coin_texture, coin.rect.move(-self.camera_X, -self.camera_Y))

        self.coin_counter_label.set_text(f"Coin: {self.coin_counter}")

    def run(self):
        while self.running:

            time_delta = self.clock.tick(self.FPS)/1000.0

            self.handle_events()

            self.manager.update(time_delta)

            self.screen.fill(WHITE)

            if not self.in_menu:

                if not self.pause:
                    self.update()
                self.draw()

            self.manager.draw_ui(self.screen)

            pg.display.flip()