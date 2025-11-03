from constants import TARGETS, COSTS
from maze_state import MazeState
from object_location import ObjectInfo


def check_blocking_obj_in_hall(maze_state: list[ObjectInfo], obj: ObjectInfo, dest_room: int) -> bool:
    loc = max(obj.hall_location, obj.room_id)

    for other in maze_state:
        if other == obj or other.hall_location == -1:
            continue

        if (loc <= other.hall_location <= dest_room) or (
                dest_room <= other.hall_location <= loc):
            return True
    return False


def get_type_objects(obj: ObjectInfo, state: MazeState) -> list[ObjectInfo]:
    locations = []
    for other in state.locations:
        if other.type == obj.type and other is not obj:
            locations.append(other)
    return locations


def is_all_in_right_room(obj: ObjectInfo, state: MazeState) -> bool:
    if obj.room_id != TARGETS[obj.type]:
        return False
    depths = [obj.depth]
    for other in get_type_objects(obj, state):
        if other.room_id != TARGETS[obj.type]:
            return False
        depths.append(other.depth)
    return depths == list(set(depths))


def is_target_with_foreigners(obj: ObjectInfo, state: MazeState) -> bool:
    target = TARGETS[obj.type]
    for other in state.locations:
        if other is obj or other.room_id == -1 or other.type == obj.type:
            continue
        if other.room_id == target:
            return True
    return False


def is_any_in_target(obj: ObjectInfo, state: MazeState) -> bool:
    target = TARGETS[obj.type]
    for other in state.locations:
        if other is obj or other.room_id == -1:
            continue
        if other.room_id == target:
            return True
    return False


def is_obj_blocked_in_room(obj: ObjectInfo, state: MazeState) -> bool:
    for other in state.locations:
        if other is obj:
            continue
        if other.room_id == obj.room_id and other.depth != -1 and other.depth < obj.depth:
            return True
    return False


def go_to_target(obj: ObjectInfo, obj_index: int, state: MazeState, depth: int, room_out_cost: int,
                 object_location: int) -> MazeState:
    cost_to_move = COSTS[obj.type] * (abs(object_location - TARGETS[obj.type]) + depth + room_out_cost)
    locations_copy = state.locations.copy()
    locations_copy[obj_index] = ObjectInfo(obj.type, room_id=TARGETS[obj.type], depth=depth)
    return MazeState(locations_copy, state.cost + cost_to_move)
