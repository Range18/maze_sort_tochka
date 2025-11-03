from constants import TARGETS
from object_location import ObjectInfo


class MazeState:
    def __init__(self, locations: list[ObjectInfo], cost: int = 0) -> None:
        self.locations = locations
        self.cost = cost

    def state_key(self) -> tuple:
        return tuple(sorted((obj.type, obj.room_id, obj.depth, obj.hall_location) for obj in self.locations))

    def is_finish_state(self) -> bool:
        for obj in self.locations:
            if obj.room_id != TARGETS[obj.type]:
                return False
        return True
