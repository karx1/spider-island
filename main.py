"""
Spider Island
"""
import random
import os

import arcade
import math

# Window constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Spider Island"

# Sprite scaling

PLAYER_SCALING = 1
COIN_SCALING = 0.0594
TILE_SCALING = 0.5
BULLET_SCALING = 0.5

NORMAL_SPEED = 2
WATER_SPEED = 1

PLAYER_MOVEMENT_SPEED = NORMAL_SPEED
GRAVITY = 1

NORMAL_JUMP_SPEED = 12.5
WATER_JUMP_SPEED = 6.25

PLAYER_JUMP_SPEED = NORMAL_JUMP_SPEED

NORMAL_BULLET_SPEED = 7
WATER_BULLET_SPEED = 3.5

BULLET_SPEED = NORMAL_BULLET_SPEED
SPIDER_SPEED = 2
SPIDER_CLIMB_SPEED = 1

UPDATES_PER_FRAME = 7
LEFT_FACING = 1
RIGHT_FACING = 0


def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class PlayerCharacter(arcade.Sprite):
    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        # Track out state
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False
        self.scale = PLAYER_SCALING
        self.texture = arcade.load_texture("assets/player_idle.png")

        # Adjust the collision box. Default includes too much empty space
        # side-to-side. Box is centered at sprite center, (0, 0)
        self.points = self.get_adjusted_hit_box()

        # --- Load Textures ---

        # Images from Kenney.nl's Asset Pack 3
        main_path = "assets/player"
        # main_path = ":resources:images/animated_characters/female_person/femalePerson"
        # main_path = ":resources:images/animated_characters/male_person/malePerson"
        # main_path = ":resources:images/animated_characters/male_adventurer/maleAdventurer"
        # main_path = ":resources:images/animated_characters/zombie/zombie"
        # main_path = ":resources:images/animated_characters/robot/robot"

        # Load textures for idle standing
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")

        # Load textures for walking
        self.walk_textures = []
        for i in range(5):
            texture = load_texture_pair(f"{main_path}_walk_{i}.png")
            self.walk_textures.append(texture)

    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Idle animation
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 4 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture // UPDATES_PER_FRAME][self.character_face_direction]


class SpiderIsland(arcade.View):
    """
    Main game class
    """

    def __init__(self):
        super().__init__()

        self.jump_needs_reset = False
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        self.coin_list = None
        self.player_list = None
        self.wall_list = None
        self.bullet_list = None
        self.spider_list = None
        self.ladder_list = None
        self.water_list = None

        self.player_sprite = None
        self.engine = None
        self.spider_engines = None

        self.score = 0
        self.score_text = None

        self.level = 1

    def setup(self, level, score=None):
        self.score = score or 0
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        # self.coin_list = arcade.SpriteList(use_spatial_hash=True)
        # self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.player_list.append(self.player_sprite)

        # for x in range(0, 1250, 64):
        #     wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
        #     wall.center_x = x
        #     wall.center_y = 32
        #     self.wall_list.append(wall)
        #
        # coordinate_list = [[512, 96],
        #                    [256, 96],
        #                    [768, 96]]
        #
        # for coordinate in coordinate_list:
        #     wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", TILE_SCALING)
        #     wall.position = coordinate
        #     self.wall_list.append(wall)
        #
        # for x in range(128, 1250, 256):
        #     coin = arcade.Sprite("assets/coin.png", COIN_SCALING)
        #     coin.center_x = x
        #     coin.center_y = 96
        #     self.coin_list.append(coin)

        # Check if the game is over
        num_maps = len(os.listdir("maps"))
        if level > num_maps:
            view = WinScreen()
            self.window.show_view(view)
            return

        map_name = f"maps/map_level_{level}.tmx"
        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = "Platforms"
        # Name of the layer that has items for pick-up
        coins_layer_name = "Coins"
        # Name of the layer that contains enemies
        spiders_layer_name = "Spiders"
        # Name of the layer that contains ladders
        ladders_layer_name = "Ladders"
        water_layer_name = "Water"

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platforms_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        self.coin_list = arcade.tilemap.process_layer(my_map, coins_layer_name, TILE_SCALING, use_spatial_hash=True)
        self.spider_list = arcade.tilemap.process_layer(my_map, spiders_layer_name, TILE_SCALING)
        self.ladder_list = arcade.tilemap.process_layer(my_map, ladders_layer_name, TILE_SCALING, use_spatial_hash=True)
        self.ladder_list = arcade.tilemap.process_layer(my_map, ladders_layer_name, TILE_SCALING, use_spatial_hash=True)
        self.water_list = arcade.tilemap.process_layer(my_map, water_layer_name, TILE_SCALING, use_spatial_hash=True)

        self.engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                     self.wall_list,
                                                     GRAVITY,
                                                     ladders=self.ladder_list)
        self.spider_engines = []
        for spider in self.spider_list:
            engine = arcade.PhysicsEnginePlatformer(spider, self.wall_list, GRAVITY)
            self.spider_engines.append(engine)

    def on_draw(self):
        arcade.start_render()

        # Render sprites
        self.water_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()
        self.ladder_list.draw()
        self.spider_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()

        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

    def on_update(self, delta_time):
        self.player_list.update()
        self.player_list.update_animation()
        self.engine.update()
        for engine in self.spider_engines:
            engine.update()

        water_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.water_list)
        global PLAYER_MOVEMENT_SPEED, BULLET_SPEED, PLAYER_JUMP_SPEED

        if len(water_hit_list) > 0:
            PLAYER_MOVEMENT_SPEED = WATER_SPEED
            BULLET_SPEED = WATER_BULLET_SPEED
            PLAYER_JUMP_SPEED = WATER_JUMP_SPEED
        else:
            PLAYER_MOVEMENT_SPEED = NORMAL_SPEED
            BULLET_SPEED = NORMAL_BULLET_SPEED
            PLAYER_JUMP_SPEED = NORMAL_JUMP_SPEED

        for spider in self.spider_list:
            follow_sprite(spider, self.player_sprite)

            wall_hit_list = arcade.check_for_collision_with_list(spider, self.wall_list)

            if len(wall_hit_list) > 0:
                for wall in wall_hit_list:
                    start_x = spider.center_x
                    start_y = spider.center_y

                    dest_x = wall.center_x
                    dest_y = wall.top + 100

                    x_diff = dest_x - start_x
                    y_diff = dest_y - start_y
                    angle = math.atan2(y_diff, x_diff)

                    spider.change_x = math.cos(angle) * SPIDER_SPEED
                    spider.change_y = math.sin(angle) * SPIDER_SPEED

            if spider.bottom > self.window.width or spider.top < 0 or spider.right < 0 or spider.left > self.window.width:
                spider.remove_from_sprite_lists()
            elif len(arcade.check_for_collision_with_list(spider, self.water_list)):
                spider.remove_from_sprite_lists()

        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)

        for coin in coin_hit_list:
            self.score += 1
            coin.remove_from_sprite_lists()

        self.bullet_list.update()

        for bullet in self.bullet_list:
            # Get bullet collisions
            bullet_hit_list = arcade.check_for_collision_with_list(bullet, self.spider_list)
            wall_hit_list = arcade.check_for_collision_with_list(bullet, self.wall_list)
            coin_hit_list = arcade.check_for_collision_with_list(bullet, self.coin_list)

            if len(wall_hit_list) > 0:
                bullet.remove_from_sprite_lists()

            if len(bullet_hit_list) > 0:
                bullet.remove_from_sprite_lists()

            if len(coin_hit_list) > 0:
                bullet.remove_from_sprite_lists()

            for spider in bullet_hit_list:
                spider.remove_from_sprite_lists()
                self.score += 1

            for coin in coin_hit_list:
                coin.remove_from_sprite_lists()
                self.score += 1

            # If bullet flies offscreen, remove it
            if bullet.bottom > self.window.width or bullet.top < 0 or bullet.right < 0 or bullet.left > self.window.width:
                bullet.remove_from_sprite_lists()

        if self.player_sprite.bottom > self.window.width or self.player_sprite.top < 0 or self.player_sprite.right < 0 or (
                self.player_sprite.left > self.window.width
        ):
            view = GameOverScreen()
            self.window.show_view(view)

        spider_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.spider_list)

        if len(spider_hit_list) > 0:
            view = GameOverScreen()
            self.window.show_view(view)

        if len(self.spider_list) == 0 and len(self.coin_list) == 0:
            self.level += 1
            self.setup(self.level, self.score)

    def process_keychange(self):
        """
        Called when we change a key up/down or we move on/off a ladder.
        """
        # Process up/down
        if self.up_pressed and not self.down_pressed:
            if self.engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif self.engine.can_jump() and not self.jump_needs_reset:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
        elif self.down_pressed and not self.up_pressed:
            if self.engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        # Process up/down when on a ladder and no movement
        if self.engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Process left/right
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        bullet = arcade.Sprite("assets/laser.png", BULLET_SCALING)

        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y

        dest_x = x
        dest_y = y

        # Bullet trajectory calculation
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # Bullet velocity calculation
        bullet.change_x = math.cos(angle) * BULLET_SPEED
        bullet.change_y = math.sin(angle) * BULLET_SPEED

        self.bullet_list.append(bullet)


def follow_sprite(self, player_sprite):
    """
        This function will move the current sprite towards whatever
        other sprite is specified as a parameter.

        We use the 'min' function here to get the sprite to line up with
        the target sprite, and not jump around if the sprite is not off
        an exact multiple of SPRITE_SPEED.
        """

    self.center_x += self.change_x
    self.center_y += self.change_y

    # Random 1 in 100 chance that we'll change from our old direction and
    # then re-aim toward the player
    if random.randrange(100) == 0:
        start_x = self.center_x
        start_y = self.center_y

        # Get the destination location for the bullet
        dest_x = player_sprite.center_x
        dest_y = player_sprite.center_y

        # Do math to calculate how to get the bullet to the destination.
        # Calculation the angle in radians between the start points
        # and end points. This is the angle the bullet will travel.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        if x_diff > 0:
            self.texture = arcade.load_texture("assets/spider.png", flipped_horizontally=True)
        else:
            self.texture = arcade.load_texture("assets/spider.png")

        # Taking into account the angle, calculate our change_x
        # and change_y. Velocity is how fast the bullet travels.
        self.change_x = math.cos(angle) * SPIDER_SPEED
        # self.change_y = math.sin(angle) * SPIDER_SPEED


def get_tip():
    tips = [
        "Spiders hate water!",
        "Bullets are an excellent way to get coins!",
        "Use your mouse to shoot at enemies and coins!",
        "You move slower in water!",
        "Spiders can't climb ladders!"
    ]
    return random.choice(tips)


class StartScreen(arcade.View):
    def __init__(self,
                 window: arcade.Window = None):
        super().__init__(window)
        self.tip = get_tip()

    def on_show(self):
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Spider Island", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Click to start", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-75, arcade.color.WHITE, font_size=20, anchor_x="center")
        arcade.draw_text(f"TIP: {self.tip}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100, arcade.color.WHITE, font_size=15, anchor_x="center")

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        view = InstructionScreen()
        self.window.show_view(view)


class GameOverScreen(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("You died!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Click to restart", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-75, arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        game_view = SpiderIsland()
        game_view.setup(game_view.level)
        self.window.show_view(game_view)


class WinScreen(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Congratulations!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("You killed all the spiders and made it to the rescue boat.", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-75, arcade.color.WHITE, font_size=20, anchor_x="center")
        arcade.draw_text("Click to restart.", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-100, arcade.color.WHITE, font_size=15, anchor_x="center")

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        game_view = SpiderIsland()
        game_view.setup(game_view.level)
        self.window.show_view(game_view)


class InstructionScreen(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Instructions", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Use your mouse to aim and click to shoot a bullet!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-75, arcade.color.WHITE, font_size=20, anchor_x="center")
        arcade.draw_text("Kill the spiders and collect the rubies.", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-100, arcade.color.WHITE, font_size=15, anchor_x="center")

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        game_view = SpiderIsland()
        game_view.setup(game_view.level)
        self.window.show_view(game_view)


def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartScreen()
    window.show_view(start_view)
    arcade.run()


if __name__ == '__main__':
    main()
