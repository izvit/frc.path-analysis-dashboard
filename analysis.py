import numpy as np


class AnalysisObject:

    def __init__(self, events):
        self.events = events

    def distance(pos0, pos1) -> np.double:
        return np.sqrt((pos0.x-pos1.x)^2 + (pos0.y-pos1.y)^2)

    def event_distance(e0, e1) -> np.double:
        pass

