"""gameutil.py holds utility enums and functions used in the game"""
from enum import auto
from enum import Enum

from pygame import image
from pygame import Surface
from pygame import RLEACCEL

from pygame.locals import USEREVENT


OBSTACLE_SPAWN_EVENT = USEREVENT + 1
OBSTACLE_SPAWN_RATE_MS = 1000
SECONDS_PER_FRAME = 0.016


class GameState(Enum):
    """States of the game"""
    RUNNING = auto()
    OVER = auto()
    PAUSED = auto()
    NOT_STARTED = auto()


class Color(Enum):
    """Colors"""
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    SEA = (15, 94, 156)
    OBSTACLE = (72, 46, 33)


def surface_from_image(filename):
    """Loads an image and creates a surface with the image blitted on it"""
    img = image.load(filename)

    surface = Surface(img.get_size())
    surface.blit(img, (0, 0))

    ckey = surface.get_at((0, 0))
    surface.set_colorkey(ckey, RLEACCEL)

    return surface
