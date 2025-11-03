from constants import COSTS


class ObjectInfo:
    def __init__(self, obj_type: str, room_id: int = -1, depth: int = -1, hall_location: int = -1) -> None:
        if room_id == -1 and hall_location == -1:
            raise ValueError("Either room_id and depth or hall_location must be specified")
        self.type = obj_type
        self.room_id = room_id
        self.depth = depth
        self.hall_location = hall_location
        self.energy = COSTS[self.type]

    def __str__(self):
        return f"{self.type}: room_id: {self.room_id} depth: {self.depth} hall_location: {self.hall_location}"

    def __eq__(self, other):
        return (self.type, self.room_id, self.depth, self.hall_location) == \
            (other.type, other.room_id, other.depth, other.hall_location)

    def __hash__(self):
        return hash((self.type, self.room_id, self.depth, self.hall_location))