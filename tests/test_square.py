# import sys
# sys.path.append("../")
# from dog_tracking import dog_tracking
import dog_tracking

import unittest

class SquareTest(unittest.TestCase):
    def test_square_vertex(self):
        square = dog_tracking.Maze().load_image("mazes/square5.png")
    
        self.assertEqual(dog_tracking.calc_probability(square, 1, 1), 0.75, "Square test vertex failed.")
    
    def test_square5(self):
        square = dog_tracking.Maze().load_image("mazes/square5.png")
        
        self.assertEqual(dog_tracking.calc_probability(square), 0.75, "Square test 5 failed.")
        
    def test_square10(self):
        square = dog_tracking.Maze().load_image("mazes/square10.png")
        
        self.assertEqual(dog_tracking.calc_probability(square), 0.75, "Square test 10 failed.")


if __name__ == "__main__":
    # test_square()
    unittest.main()
    
    print("All tests passed!")
