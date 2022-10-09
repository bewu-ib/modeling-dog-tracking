import numpy as np
from PIL import Image
from enum import Enum
import copy
import configparser


class Tile(Enum):
    EMPTY = 0
    CORRIDOR = 1
    DOG = 2
    GIRL = 3


class Result(Enum):
    CONTINUE = 0
    WIN = 1
    STUCK = 2


class Maze:
    def __init__(self):
        self.map = []
        self.dog = [0, 0]
        self.girl = [0, 0]

    def load_image(self, image_path):
        # Load an image from the given path.
        im = Image.open(image_path)

        # Read black pixels as 1 and white pixels as 0.
        pixels = im.load()
        # p = np.array([[1 if pixels[x, y] == (0, 0, 0) else 0 for x in range(im.size[0])] for y in range(im.size[1])])
        p = []
        for x in range(im.size[0]):
            p.append([0 for i in range(im.size[1])])
            for y in range(im.size[1]):
                if pixels[x, y] == (0, 0, 0):
                    p[x][y] = Tile.CORRIDOR.value
                else:
                    p[x][y] = Tile.EMPTY.value

        self.map = p

        return self

    def print_map(self):
        for y in range(len(self.map[0])):
            for x in range(len(self.map)):
                v = self.map[x][y]

                p = v
                if p == Tile.EMPTY.value:
                    p = " "
                elif p == Tile.CORRIDOR.value:
                    p = "="
                else:
                    p = Tile(p).name[0]

                print(p, end=" ")
            print()

    def start(self, dog_pos, girl_pos):
        self.map[dog_pos[0]][dog_pos[1]] = Tile.DOG.value
        self.map[girl_pos[0]][girl_pos[1]] = Tile.GIRL.value

        self.dog = dog_pos.copy()
        self.girl = girl_pos.copy()

    def copy(self):
        m = Maze()
        m.map = copy.deepcopy(self.map)

        return m

    def can_move(self, x, y):
        return self.map[x][y] in (Tile.CORRIDOR.value, Tile.GIRL.value)

    def move(self, debug=False):
        # calculate the distance between the self.dog and the girl
        d_x = self.girl[0] - self.dog[0]
        d_y = self.girl[1] - self.dog[1]

        if debug:
            print("dog", self.dog[0], self.dog[1])
            print("dis", d_x, d_y)

        move = None

        if d_x == 0 and d_y == 0:
            # print("The self.dog has reached the girl")
            return Result.WIN.value

        if d_x == 0:
            y_sign = int(d_y/abs(d_y))

            if self.can_move(self.dog[0], self.dog[1]+y_sign):
                move = [0, y_sign]
        elif d_y == 0:
            x_sign = int(d_x/abs(d_x))

            if self.can_move(self.dog[0]+x_sign, self.dog[1]):
                move = [x_sign, 0]
        else:
            angle_a = abs(np.arctan(d_x / d_y))
            angle_b = abs(np.arctan(d_y / d_x))

            # get the direction of the self.dog
            direction = [0, 0]
            if d_x > 0:
                direction[0] = 1
            elif d_x < 0:
                direction[0] = -1

            if d_y > 0:
                direction[1] = 1
            elif d_y < 0:
                direction[1] = -1

            if debug:
                print("angles", angle_a, angle_b)
                print("dir", direction)

            if angle_a < angle_b and self.can_move(self.dog[0], self.dog[1]+direction[1]):
                move = [0, direction[1]]
            elif angle_a != angle_b and self.can_move(self.dog[0]+direction[0], self.dog[1]):
                move = [direction[0], 0]

        if move:
            self.map[self.dog[0]][self.dog[1]] = 1

            if move[0] and self.can_move(self.dog[0]+move[0], self.dog[1]):
                # move in x direction
                self.dog[0] += move[0]
            elif self.can_move(self.dog[0], self.dog[1]+move[1]):
                # move in y direction
                self.dog[1] += move[1]

            self.map[self.dog[0]][self.dog[1]] = Tile.DOG.value
            return Result.CONTINUE.value

        else:
            # print("Stuck!")
            return Result.STUCK.value


def debug_one(map, dog_pos, girl_pos, debug=False):
    m = Maze()
    m.map = map

    m.start(dog_pos, girl_pos)
    m.print_map()

    c = Result.CONTINUE.value
    while c == Result.CONTINUE.value:
        c = m.move(debug)

        input()
        m.print_map()

    print(Result(c).name)


def calc_probability(maze_initial, girl_range_i=None, girl_range_j=None, debug=0):
    n_win = 0
    n_stuck = 0

    if girl_range_i is None:
        girl_range_i = len(maze_initial.map)
    if girl_range_j is None:
        girl_range_j = len(maze_initial.map[0])

    for k in range(girl_range_i):
        for l in range(girl_range_j):
            if not maze_initial.can_move(k, l):
                continue

            if debug > 1:
                print(k, l)
            girl_position = [k, l]

            for i in range(len(maze_initial.map)):
                for j in range(len(maze_initial.map[0])):
                    if not maze_initial.can_move(i, j):
                        continue

                    dog_position = [i, j]

                    if debug > 1:
                        print("\t", i, j)
                        # print(girl_position_, dog_position_)

                    maze = maze_initial.copy()

                    maze.start(dog_position, girl_position)

                    c = Result.CONTINUE.value
                    while c == Result.CONTINUE.value:
                        c = maze.move()

                    if debug > 1:
                        print("\t", Result(c).name)

                    if c == Result.WIN.value:
                        n_win += 1
                    elif c == Result.STUCK.value:
                        n_stuck += 1

    if debug > 0:
        print()
        print("win", n_win)
        print("stuck", n_stuck)
        print("win chance", n_win / (n_win + n_stuck))

    return n_win / (n_win + n_stuck)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.txt")

    debug_level = int(config['debug']['level'])

    # load image
    maze_initial = Maze()
    maze_initial.load_image(config['input']['image'])

    # # debug_one(map_initial.map, [4, 4], [0, 3], print_d)
    # # quit()

    # test for different positions
    n_girl_i = len(maze_initial.map)
    n_girl_j = len(maze_initial.map[0])

    p = calc_probability(maze_initial, n_girl_i, n_girl_j, debug_level)

    print(p)
