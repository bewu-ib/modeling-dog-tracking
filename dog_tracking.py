import numpy as np
from PIL import Image
from enum import Enum
import copy
import configparser
# import tqdm
from tqdm import tqdm
from tqdm.contrib.telegram import tqdm as tqdm_telegram
import multiprocessing as mp
import os


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

        self.corridor_points = []

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

                    self.corridor_points.append((x, y))
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
        if x < 0 or y < 0:
            return False
        if x >= len(self.map) or y >= len(self.map[0]):
            return False

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

            if not self.can_move(self.dog[0]+direction[0], self.dog[1]):
                angle_b = float('inf')
            if not self.can_move(self.dog[0], self.dog[1]+direction[1]):
                angle_a = float('inf')

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


def calc_probability(maze_initial, debug=0, girl_range_i=None, disable_vertices=True, telegram=None):
    n_win = 0
    n_stuck = 0

    if girl_range_i is None:
        girl_range_i = range(len(maze_initial.corridor_points))

    bar_title = f"Testing girl ({os.getpid()})"

    if telegram is not None and bool(int(telegram['enabled'])):
        g_range = tqdm_telegram(girl_range_i, desc=bar_title,
                                token=telegram['token'], chat_id=telegram['chat'])
    else:
        g_range = tqdm(girl_range_i, desc=bar_title)

    for g_i in g_range:
        # for l in girl_range_j:
        # if not maze_initial.can_move(k, l):
        #     continue

        k, l = maze_initial.corridor_points[g_i]

        # check if point is a vertex
        if disable_vertices:
            if (maze_initial.can_move(k+1, l) ^ maze_initial.can_move(k-1, l)) or \
                    (maze_initial.can_move(k, l+1) ^ maze_initial.can_move(k, l-1)):

                continue

        if debug > 1:
            print("g", k, l)
        girl_position = [k, l]
        
        d_range = range(len(maze_initial.corridor_points))
        if debug > 0:
            d_range = tqdm(d_range, desc="Testing dog", leave=False)

        for d_i in d_range:
            # for i in range(len(maze_initial.map)):
            #     for j in range(len(maze_initial.map[0])):
            #         if not maze_initial.can_move(i, j):
            #             continue

            i, j = maze_initial.corridor_points[d_i]

            # check if point is a vertex
            if disable_vertices:
                if (maze_initial.can_move(i+1, j) ^ maze_initial.can_move(i-1, j)) or \
                        (maze_initial.can_move(i, j+1) ^ maze_initial.can_move(i, j-1)):

                    continue

            if debug > 1:
                print("\t d", i, j)
            dog_position = [i, j]

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
        print()

    return n_win / (n_win + n_stuck), n_win, n_stuck


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.txt")

    debug_level = int(config['debug']['level'])

    # load image
    maze_initial = Maze()
    maze_initial.load_image(config['input']['image'])

    # debug_one(maze_initial.map, [4, 4], [0, 3], debug_level)
    # quit()

    # debug_one(maze_initial.map, [4, 3], [0, 0], debug_level)
    # quit()

    # test for different positions

    # p = calc_probability(maze_initial, 1, 1, debug_level)
    
    def calc_process(maze_initial, range_, win_value, stuck_value, debug_level, config):
        p, w, s = calc_probability(maze_initial, girl_range_i=range_, debug=debug_level, telegram=config['telegram'] if "telegram" in config else None)
        
        win_value.value = w
        stuck_value.value = s
    
    processes = []
    win_values = []
    stuck_values = []
    for process in range(int(config['processes']['number'])):
        # p = calc_probability(maze_initial, debug=debug_level,
        #                  telegram=config['telegram'] if "telegram" in config else None)
        
        p_range = range(process, len(maze_initial.corridor_points), int(config['processes']['number']))
        
        w = mp.Value('i', 0)
        s = mp.Value('i', 0)
        
        processes.append(mp.Process(target=calc_process, args=(maze_initial, p_range, w, s, debug_level, config)))

        win_values.append(w)
        stuck_values.append(s)

    for p in processes:
        p.start()
        
    for p in processes:
        p.join()
        
    print("\nFinished all processes\n")
    
    t_win = 0
    t_stuck = 0
    for i in range(len(processes)):
        print(f"process {i} win {win_values[i].value} stuck {stuck_values[i].value}")
        
        t_win += win_values[i].value
        t_stuck += stuck_values[i].value
        
    print(f"\ntotal win {t_win} stuck {t_stuck}")
    print(f"total win chance {t_win / (t_win + t_stuck)}")
