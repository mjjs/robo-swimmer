"""game.py holds all the game related functionality"""

from collections import deque
from random import randint
from time import time

from pygame import display
from pygame import event
from pygame import Rect
from pygame import time as pgtime
from pygame import Surface

from pygame import locals as pygame_vars

from gameutil import GameState
from gameutil import Color
from gameutil import surface_from_image
from gameutil import OBSTACLE_SPAWN_EVENT
from gameutil import OBSTACLE_SPAWN_RATE_MS
from gameutil import SECONDS_PER_FRAME


class GameObject():
    """A generic game object to extend from"""

    def __init__(self, x, y, surface):
        self.x = x
        self.y = y
        self._surface = surface

    def get_position(self):
        """Returns the position of the game object as a tuple"""
        return (self.x, self.y)

    def get_size(self):
        """Returns the size of the surface used by the game object"""
        return self._surface.get_size()

    def get_hitbox(self):
        """Returns a rectangle representing the hitbox of the object"""
        return Rect((self.x, self.y), self.get_size())

    def get_surface(self):
        """Returns the surface of the game object"""
        return self._surface

    def detect_collision(self, game_object):
        """Returns a boolean indicating whether the two game objects are colliding"""
        return self.get_hitbox().colliderect(game_object.get_hitbox())


class Obstacle(GameObject):
    """A single obstacle rolling down the screen"""

    def __init__(self, screen_height):
        self.screen_height = screen_height
        self._offset = randint(-100, 100)
        self.gap_size = 170
        self._speed = 5
        surface = self._init_surface()

        GameObject.__init__(self, 1200, 0, surface)

    def update(self):
        """Moves the obstacle according to its speed"""
        self.x -= self._speed

    def get_hitbox(self):
        top = Rect((self.x, self.y), self._top_surface.get_size())
        bot_y = self.y + (self.screen_height / 2) + (self.gap_size / 2) + self._offset
        bot = Rect((self.x, bot_y), self._bot_surface.get_size())
        return (top, bot)

    def detect_collision(self, game_object):
        """
        Checks whether a game object has collides
        with either of the rectangles of the obstacle
        """
        top, bot = self.get_hitbox()
        player_hitbox = game_object.get_hitbox()

        collide_top = top.colliderect(player_hitbox)
        collide_bot = bot.colliderect(player_hitbox)

        if collide_top or collide_bot:
            return True

        return False

    def _init_surface(self):
        """Creates the top and bottom surfaces of the obstacle"""
        block_size = self.screen_height / 2
        gap_center = self.gap_size / 2
        obstacle_width = 80

        self._top_surface = Surface((obstacle_width, block_size - gap_center + self._offset))
        self._bot_surface = Surface((obstacle_width, block_size + 200))
        self._top_surface.fill(Color.OBSTACLE.value)
        self._bot_surface.fill(Color.OBSTACLE.value)

        surface = Surface((obstacle_width, 1200))
        surface.set_colorkey(Color.BLACK.value)

        surface.blit(self._top_surface, (0, 0))
        surface.blit(self._bot_surface, (0, self.screen_height/2 + gap_center + self._offset))

        return surface


class Player(GameObject):
    """Represents the player character"""

    def __init__(self, game):
        surface = surface_from_image("assets/player.png")
        GameObject.__init__(self, 250, 200, surface)

        self.velocity_up = 0
        self.game = game

    def swim(self):
        """Increases the players upward velocity to move the player up"""
        self.velocity_up = 30

    def update(self):
        """Updates the player position"""
        if self.get_hitbox().bottom > self.game.window.get_height():
            self.y = 570
        elif self.get_hitbox().top < 0:
            self.y = 0
            self.velocity_up = 0

        self.y -= self.velocity_up / 2

        if self.velocity_up > 0:
            self.velocity_up -= self.game.gravity / 4

        self.y += self.game.gravity / 3


class Game():
    """The main class for the game"""

    def __init__(self):
        window_width = 1280
        window_height = 640
        self.window = display.set_mode((window_width, window_height))
        self.state = GameState.NOT_STARTED

        self.player = Player(self)
        self.obstacles = deque()

        self.obstacles_passed = 0
        self.gravity = 8
        self.distance_traveled = 0.0

    def process_input(self):
        """Processes user input and calls suitable actions"""
        for game_event in event.get():
            if game_event.type == pygame_vars.QUIT:
                exit()

            if game_event.type == OBSTACLE_SPAWN_EVENT:
                self.add_obstacle()

            if game_event.type == pygame_vars.KEYDOWN:
                key = game_event.key
                if key == pygame_vars.K_SPACE:
                    self.player.swim()
                if key == pygame_vars.K_o:
                    self.add_obstacle()
                if key == pygame_vars.K_q:
                    exit()

    def update(self):
        """Updates the game state"""
        self.player.update()
        self.distance_traveled += 1

        for obstacle in self.obstacles:
            obstacle.update()

            if obstacle.detect_collision(self.player):
                self.state = GameState.OVER

            self.obstacles = self.get_on_screen_obstacles()

    def render(self):
        """Renders the game"""
        self.window.fill(Color.SEA.value)

        player_pos = self.player.get_hitbox()
        self.window.blit(self.player.get_surface(), player_pos)

        for obstacle in self.obstacles:
            self.window.blit(
                obstacle.get_surface(),
                obstacle.get_position()
            )

        display.flip()

    def add_obstacle(self):
        """Adds a new obstacle to the game"""
        self.obstacles.append(Obstacle(self.window.get_height()))

    def get_next_obstacle(self):
        """Returns the closest obstacle to the player which is not behind the player

        Returns None if no obstacles exist
        """
        closest_obstacle = None
        closest_pos = None
        player_pos = self.player.get_hitbox().centerx

        for obstacle in self.obstacles:
            obstacle_pos = obstacle.get_hitbox()[0].centerx

            if obstacle_pos > player_pos:
                if closest_obstacle is None:
                    closest_obstacle = obstacle
                    closest_pos = obstacle.get_hitbox()[0].centerx
                elif closest_pos > obstacle_pos:
                    closest_obstacle = obstacle

        return closest_obstacle

    def distance_to_obstacle(self, obstacle):
        """Returns the distance between the player and the given obstacle"""
        obstacle_center = obstacle.get_hitbox()[0].centerx
        player_center = self.player.get_hitbox().centerx
        return obstacle_center - player_center

    def height_to_obstacle(self, obstacle):
        """Returns the height difference between the player and the given obstacle"""
        obstacle_gap_center = obstacle.get_hitbox()[0].bottom + obstacle.gap_size / 2
        player_center_height = self.player.get_hitbox().centery
        return obstacle_gap_center - player_center_height

    def get_on_screen_obstacles(self):
        """Returns a deque of obstacles that are still on screen"""
        ocount = len(self.obstacles)
        obstacles = deque(obstacle for obstacle in self.obstacles
                          if obstacle.x + obstacle.get_surface().get_width() > 9)
        self.obstacles_passed += ocount - len(obstacles)

        return obstacles

    def get_score(self):
        """Returns the amount of obstacles the player passed"""
        return self.obstacles_passed

    def init_game(self):
        """Initializes the game"""
        self.state = GameState.RUNNING
        pgtime.set_timer(OBSTACLE_SPAWN_EVENT, OBSTACLE_SPAWN_RATE_MS)

    def calculate_fitness(self):
        """Calculates the fitness of the game after finishing.

        Fitness is calculated with the formula: d - (dist + abs(height))
        where d = distance traveled,
        dist = distance to the next obstacle,
        height = height difference to the next obstacle
        """
        next_obstacle = self.get_next_obstacle()
        delta_distance = self.distance_to_obstacle(next_obstacle)
        delta_height = abs(self.height_to_obstacle(next_obstacle))
        fitness = self.distance_traveled - (delta_distance + delta_height)
        return fitness

    def start(self):
        """Starts the game, keeps it running and updates it"""
        self.init_game()

        previous = time()
        lag = 0.0

        while self.state == GameState.RUNNING:
            current = time()
            delta_time = current - previous
            previous = current
            lag += delta_time

            self.process_input()

            while lag >= SECONDS_PER_FRAME:
                self.update()
                lag -= SECONDS_PER_FRAME

            self.render()

        print("Obstacles passed:", self.get_score())
        print("Fitness: ", self.calculate_fitness())

if __name__ == "__main__":
    Game().start()
