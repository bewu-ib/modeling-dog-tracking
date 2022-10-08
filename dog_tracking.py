from PIL import Image
import numpy as np
from enum import Enum
import copy


class Entity(Enum):
    DOG = 2
    GIRL = 3
    

class Result(Enum):
    CONTINUE = 0
    WIN = 1
    STUCK = 2


def load_image(image_path):
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
                p[x][y] = 1
            else:
                p[x][y] = 0
            
    return p


def print_map(map):
    for y in range(len(map[0])):
        for x in range(len(map)):
            v = map[x][y]
            
            p = v
            if p == 0:
                p = " "
            elif p == 1:
                p = "="
            elif p > 1:
                p = Entity(p).name[0]
            
            print(p, end=" ")
        print()


def start(map, dog_pos, girl_pos):
    map[dog_pos[0]][dog_pos[1]] = Entity.DOG.value
    map[girl_pos[0]][girl_pos[1]] = Entity.GIRL.value


def move(map, dog, girl, debug=False):
    # calculate the distance between the dog and the girl
    d_x = girl[0] - dog[0]
    d_y = girl[1] - dog[1]
    
    if debug:
        print("dog", dog[0], dog[1])
        print("dis", d_x, d_y)
    
    move = None
    
    if d_x == 0 and d_y == 0:
        # print("The dog has reached the girl")
        return Result.WIN.value
    
    if d_x == 0:
        y_sign = int(d_y/abs(d_y))

        if map[dog[0]][dog[1]+y_sign] in (1, Entity.GIRL.value):
            move = [0, y_sign]
    elif d_y == 0:
        x_sign = int(d_x/abs(d_x))
                
        if map[dog[0]+x_sign][dog[1]] in (1, Entity.GIRL.value):
            move = [x_sign, 0]
    else:
        angle_a = abs(np.arctan(d_x / d_y))
        angle_b = abs(np.arctan(d_y / d_x))
                
        # get the direction of the dog
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
            print(angle_a, angle_b)
            print(map[dog[0]][dog[1]+direction[1]])
            print(direction)
            
        if angle_a < angle_b and map[dog[0]][dog[1]+direction[1]] in (1, Entity.GIRL.value):
            move = [0, direction[1]]
        elif angle_a != angle_b and map[dog[0]+direction[0]][dog[1]] in (1, Entity.GIRL.value):
            move = [direction[0], 0]
        
    if move:
        map[dog[0]][dog[1]] = 1
        
        if move[0] and map[dog[0]+move[0]][dog[1]] in (1, Entity.GIRL.value):
            # move in x direction
            dog[0] += move[0]
        elif map[dog[0]][dog[1]+move[1]] in (1, Entity.GIRL.value): 
            # move in y direction
            dog[1] += move[1]

        map[dog[0]][dog[1]] = Entity.DOG.value
        return Result.CONTINUE.value
        
    else:
        # print("Stuck!")
        return Result.STUCK.value


def debug_one(map, dog_pos, girl_pos):
    start(map, dog_pos, girl_pos)
    print_map(map)

    c = Result.CONTINUE.value
    while c == Result.CONTINUE.value:
        c = move(map, dog_pos, girl_pos)
        
        input()
        print_map(map)
        
    print(Result(c).name)


if __name__ == "__main__":
    
    print_d = False
    
    # load image
    map_initial = load_image("square.png")
    
    # # [19, 19] [0, 8]
    # debug_one(map_initial, [19, 19], [0, 8])
    # quit()
    
    # test for dog positions
    n_win = 0
    n_stuck = 0
    
    n_girl_i = 1 # len(map_initial)
    n_girl_j = 1 # len(map_initial[0])
    
    for k in range(n_girl_i):
        for l in range(n_girl_j):
            if map_initial[k][l] == 0:
                continue
            
            if print_d:
                print(k, l)
            girl_position_ = [k, l]
    
            for i in range(len(map_initial)):
                for j in range(len(map_initial[0])):
                    if map_initial[i][j] == 0:
                        continue
                    
                    dog_position_ = [i, j]
                    
                    if print_d:
                        print("\t", i, j)
                        print(girl_position_, dog_position_)
                    
                    map = copy.deepcopy(map_initial)
                    
                    start(map, dog_position_, girl_position_)
                    
                    c = Result.CONTINUE.value
                    while c == Result.CONTINUE.value:
                        c = move(map, dog_position_, girl_position_)
                        
                    if print_d:
                        print(Result(c).name)
                    
                    if c == Result.WIN.value:
                        n_win += 1
                    elif c == Result.STUCK.value:
                        n_stuck += 1
                
    print()
    print("win", n_win)
    print("stuck", n_stuck)
    print("win chance", n_win / (n_win + n_stuck))
