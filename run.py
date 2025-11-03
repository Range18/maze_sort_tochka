import sys
import heapq
from typing import Tuple, List

TARGETS = {"A": 2, "B": 4, "C": 6, "D": 8}
COSTS = {"A": 1, "B": 10, "C": 100, "D": 1000}
TYPES = {"A": 0, "B": 1, "C": 2, "D": 3}


class ObjectInfo:
    def __init__(self, obj_type: str, room_id: int = -1, depth: int = -1, hall_location: int = -1) -> None:
        if room_id == -1 and hall_location == -1:
            raise ValueError("Either room_id and depth or hall_location must be specified")
        self.type = obj_type
        self.room_id = room_id
        self.depth = depth
        self.hall_location = hall_location

    def __eq__(self, other):
        return (self.type, self.room_id, self.depth, self.hall_location) == \
            (other.type, other.room_id, other.depth, other.hall_location)

    def __hash__(self):
        return hash((self.type, self.room_id, self.depth, self.hall_location))


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


def get_initial_state(raw_rooms: list[str], depth: int) -> MazeState:
    rows = [raw_room[3:10:2] for raw_room in raw_rooms]
    locations = []
    for i in range(depth):
        for j in range(len(rows[i])):
            locations.append(ObjectInfo(rows[i][j], (j + 1) * 2, i + 1, -1))
    return MazeState(locations)


def get_depth(maze: list[str]) -> int:
    return len(maze) - 3


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


def get_room_objects(state: MazeState, target: int, max_depth: int) -> list[int]:
    room = [-1] * max_depth
    for obj in state.locations:
        if obj.room_id == target:
            room[max_depth - obj.depth] = TYPES[obj.type]
    return room


def is_all_in_right_room(obj: ObjectInfo, state: MazeState) -> bool:
    if obj.room_id != TARGETS[obj.type]:
        return False
    for other in get_type_objects(obj, state):
        if other.room_id != TARGETS[obj.type]:
            return False
    return True


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


def get_all_sub_states(state: MazeState, max_depth: int) -> list[MazeState]:
    for i, obj in enumerate(state.locations):
        if obj.hall_location == -1:
            if obj.room_id == TARGETS[obj.type]:
                if obj.depth == max_depth:
                    continue
            if is_all_in_right_room(obj, state):
                continue

        room_out_cost = 0 if obj.room_id == -1 else obj.depth
        object_location = max(obj.room_id, obj.hall_location)

        if not is_obj_blocked_in_room(obj, state):
            if not is_target_with_foreigners(obj, state):
                target_depth = max_depth
                room = get_room_objects(state, TARGETS[obj.type], max_depth)

                while room[max_depth - target_depth] != -1:
                    target_depth -= 1

                if not check_blocking_obj_in_hall(state.locations, obj, TARGETS[obj.type]):
                    yield go_to_target(obj, i, state, target_depth, room_out_cost, object_location)

        if obj.room_id == -1:
            continue

        if obj.depth > 1 and is_obj_blocked_in_room(obj, state):
            continue

        for dest_loc in [0, 1, 3, 5, 7, 9, 10]:
            cost_to_move = COSTS[obj.type] * (abs(obj.room_id - dest_loc) + obj.depth)

            if check_blocking_obj_in_hall(state.locations, obj, dest_loc):
                continue

            locations_copy = state.locations.copy()
            locations_copy[i] = ObjectInfo(obj.type, hall_location=dest_loc)
            yield MazeState(locations_copy, state.cost + cost_to_move)


def solve(lines: list[str]) -> int | None:
    """
    Решение задачи о сортировке в лабиринте

    Args:
        lines: список строк, представляющих лабиринт

    Returns:
        минимальная энергия для достижения целевой конфигурации
    """
    raw_rooms: list[str] = lines[2:-1]
    max_depth: int = get_depth(lines)
    initial_state: MazeState = get_initial_state(raw_rooms, max_depth)

    visited: set[tuple] = set()
    pq: List[Tuple[int, int, MazeState]] = [(initial_state.cost, 0, initial_state)]
    counter: int = 1
    while pq:
        curr_cost, _, curr_state = heapq.heappop(pq)
        key = curr_state.state_key()
        if key in visited:
            continue
        visited.add(key)
        if curr_state.is_finish_state():
            return curr_cost
        for next_state in get_all_sub_states(curr_state, max_depth):
            heapq.heappush(pq, (next_state.cost, counter, next_state))
            counter += 1
    return None


def main():
    # Чтение входных данных
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip('\n'))

    result = solve(lines)
    print(result)


if __name__ == "__main__":
    main()
