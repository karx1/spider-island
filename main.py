"""
Spider Island
"""
import arcade

# Window constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Spider Island"

# Sprite scaling

PLAYER_SCALING = 0.4
COIN_SCALING = 0.0594
TILE_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

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

        self.player_sprite = None
        self.engine = None

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList(use_spatial_hash=True)
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        self.player_sprite = arcade.Sprite("assets/player.png", PLAYER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.player_list.append(self.player_sprite)

        for x in range(0, 1250, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)

        coordinate_list = [[512, 96],
                           [256, 96],
                           [768, 96]]

        for coordinate in coordinate_list:
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", TILE_SCALING)
            wall.position = coordinate
            self.wall_list.append(wall)

        for x in range(128, 1250, 256):
            coin = arcade.Sprite("assets/coin.png", COIN_SCALING)
            coin.center_x = x
            coin.center_y = 96
            self.coin_list.append(coin)

        self.engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, GRAVITY)

    def on_draw(self):
        arcade.start_render()

        # Render sprites

        self.wall_list.draw()
        self.coin_list.draw()
        self.player_list.draw()

    def on_update(self, delta_time):
        self.engine.update()

        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)

        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W:
            if self.engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
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


def main():
    """ Main method """
    window = SpiderIsland()
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()
