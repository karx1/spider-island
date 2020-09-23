"""
Spider Island
"""
import random

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

PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20
BULLET_SPEED = 7
SPIDER_SPEED = 2
SPIDER_CLIMB_SPEED = 1


class SpiderIsland(arcade.Window):
    """
    Main game class
    """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        self.coin_list = None
        self.player_list = None
        self.wall_list = None
        self.bullet_list = None
        self.spider_list = None

        self.player_sprite = None
        self.engine = None
        self.spider_engines = None

        self.score = 0
        self.score_text = None

    def setup(self, score=None):
        self.score = score or 0
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        # self.coin_list = arcade.SpriteList(use_spatial_hash=True)
        # self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        self.player_sprite = arcade.Sprite("assets/player.png", PLAYER_SCALING)
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

        map_name = "maps/map.tmx"
        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Platforms'
        # Name of the layer that has items for pick-up
        coins_layer_name = 'Coins'

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platforms_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        # -- Coins
        self.coin_list = arcade.tilemap.process_layer(my_map, coins_layer_name, TILE_SCALING, use_spatial_hash=True)
        self.spider_list = arcade.tilemap.process_layer(my_map, "Spiders", TILE_SCALING)

        self.engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, GRAVITY)
        self.spider_engines = []
        for spider in self.spider_list:
            engine = arcade.PhysicsEnginePlatformer(spider, self.wall_list, GRAVITY)
            self.spider_engines.append(engine)

    def on_draw(self):
        arcade.start_render()

        # Render sprites

        self.wall_list.draw()
        self.coin_list.draw()
        self.spider_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()

        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

    def on_update(self, delta_time):
        self.engine.update()
        for engine in self.spider_engines:
            engine.update()

        for spider in self.spider_list:
            follow(spider, self.player_sprite)

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
            if bullet.bottom > self.width or bullet.top < 0 or bullet.right < 0 or bullet.left > self.width:
                bullet.remove_from_sprite_lists()

        spider_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.spider_list)

        if len(spider_hit_list) > 0:
            self.setup()

        if len(self.spider_list) == 0 and len(self.coin_list) == 0:
            self.setup(self.score)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W:
            if self.engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.texture = arcade.load_texture("assets/player-flipped.png")
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.texture = arcade.load_texture("assets/player.png")
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

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


def follow(first, second):
    first.center_x += first.change_x
    first.center_y += first.change_y

    # Random 1 in 100 chance that we'll change from our old direction and
    # then re-aim toward the player
    if random.randrange(100) == 0:
        start_x = first.center_x
        start_y = first.center_y

        dest_x = second.center_x
        dest_y = second.center_y

        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        first.change_x = math.cos(angle) * SPIDER_SPEED
        # first.change_y = math.sin(angle) * SPIDER_SPEED


def main():
    """ Main method """
    window = SpiderIsland()
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()
