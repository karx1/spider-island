"""
Spider Island
"""
import arcade

# Window constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Spider Island"


class SpiderIsland(arcade.Window):
    """
    Main game class
    """
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        pass

    def on_draw(self):
        arcade.start_render()


def main():
    """ Main method """
    window = SpiderIsland()
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()
