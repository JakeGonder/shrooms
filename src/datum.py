# This represents one datapoint
class Datum:

    def __init__(self, coord, trees, soils):
        self.coord = coord
        self.trees = trees
        self.soils = soils
        self.mushrooms = {}
        self.probabilities = {}
