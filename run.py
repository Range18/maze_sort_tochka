import sys
import heapq
from typing import Tuple, List, Union

TARGETS = {0: 2, 1: 4, 2: 6, 3: 8}
COSTS = {0: 1, 1: 10, 2: 100, 3: 1000}
TYPES = {"A": 0, "B": 1, "C": 2, "D": 3}

Location = Tuple[int, int, int]
State = Tuple[int, Tuple[Location]]


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
# class ObjectInfo:
#     def __init__(self, obj_type: str, room_id: int = -1, depth: int = -1, hall_location: int = -1) -> None:
#         if room_id == -1 and hall_location == -1:
#             raise ValueError("Either room_id and depth or hall_location must be specified")
#         self.type = obj_type
#         self.room_id = room_id
#         self.depth = depth
#         self.hall_location = hall_location
#
#     def __eq__(self, other):
#         return (self.type, self.room_id, self.depth, self.hall_location) == \
#             (other.type, other.room_id, other.depth, other.hall_location)
#
#     def __hash__(self):
#         return hash((self.type, self.room_id, self.depth, self.hall_location))
#
#
# class MazeState:
#     def __init__(self, locations: list[ObjectInfo], cost: int = 0) -> None:
#         self.locations = locations
#         self.cost = cost
#         self.state_key = frozenset(self.locations)


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def is_finish_state(locations: tuple[Location], max_depth: int) -> bool:
    for i, obj in enumerate(locations):
        if obj[0] != TARGETS[obj[3]]:
            return False
    return True


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def get_initial_state(raw_rooms: list[str], depth: int) -> tuple[Location]:
    rows = [raw_room[3:10:2] for raw_room in raw_rooms]
    locations = []
    for i in range(depth):
        for j in range(len(rows[i])):
            locations.append(((j + 1) * 2, i + 1, -1, TYPES[rows[i][j]]))
    locations.sort(key=lambda x: x[3])
    return tuple(locations)


def get_depth(maze: list[str]) -> int:
    return len(maze) - 3


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def check_blocking_obj_in_hall(locations: tuple[Location], obj_id: int, dest_room: int) -> bool:
    obj = locations[obj_id]
    loc = max(obj[0], obj[2])

    for i in range(len(locations)):
        if i == obj_id or locations[i][2] == -1:
            continue

        if (loc <= locations[i][2] <= dest_room) or (
                dest_room <= locations[i][2] <= loc):
            return True
    return False


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def get_type_objects(obj_id: int, state: tuple[Location], max_depth: int) -> tuple[Location]:
    locations = []
    obj = state[obj_id]
    for i in range(len(state)):
        if i != obj_id and (state[i][3]) == (obj[3]):
            locations.append(state[i])
    return tuple(locations)


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def get_room_objects(state: tuple[Location], target: int, max_depth: int) -> list[int]:
    room = [-1] * max_depth
    for i in range(len(state)):
        obj = state[i]
        if obj[0] == target:
            room[max_depth - obj[1]] = obj[3]
    return room


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def is_all_in_right_room(obj_id: int, state: tuple[Location], max_depth: int) -> bool:
    obj = state[obj_id]
    if obj[0] != TARGETS[obj[3]]:
        return False
    for other in get_type_objects(obj_id, state, max_depth):
        if other[0] != TARGETS[obj[3]]:
            return False
    return True


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def is_target_with_foreigners(obj_id: int, state: tuple[Location], max_depth: int) -> bool:
    obj = state[obj_id]
    target = TARGETS[obj[3]]
    for i in range(len(state)):
        other = state[i]
        if i == obj_id or other[0] == -1 or (other[3]) == (obj[3]):
            continue
        if other[0] == target:
            return True
    return False


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def is_any_in_target(obj_id: int, state: tuple[Location], max_depth: int) -> bool:
    obj = state[obj_id]
    target = TARGETS[obj[3]]
    for i in range(len(state)):
        other = state[i]
        if i == obj_id or other[0] == -1:
            continue
        if other[0] == target:
            return True
    return False


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def is_obj_blocked_in_room(obj_id: int, state: tuple[Location]) -> bool:
    obj = state[obj_id]
    for i in range(len(state)):
        other = state[i]
        if i == obj_id:
            continue
        if other[0] == obj[0] and other[1] != -1 and other[1] < obj[1]:
            return True
    return False


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def go_to_target(obj_index: int, maze_state: State, depth: int, room_out_cost: int,
                 object_location: int, max_depth: int) -> State:
    state_cost, state = maze_state
    obj_type = state[obj_index][3]
    cost_to_move = COSTS[obj_type] * (abs(object_location - TARGETS[obj_type]) + depth + room_out_cost)
    locations_copy = list(state)
    locations_copy[obj_index] = (TARGETS[obj_type], depth, -1, obj_type)
    return state_cost + cost_to_move, tuple(locations_copy)


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def get_all_sub_states(maze_state: State, max_depth: int) -> list[State]:
    state_cost, state = maze_state
    for i, obj in enumerate(state):
        obj_type = obj[3]
        if obj[2] == -1:
            if obj[0] == TARGETS[obj_type]:
                if obj[1] == max_depth:
                    continue
            if is_all_in_right_room(i, state, max_depth):
                continue

        room_out_cost = 0 if obj[0] == -1 else obj[1]
        object_location = max(obj[0], obj[2])

        if not is_obj_blocked_in_room(i, state):
            if not is_target_with_foreigners(i, state, max_depth):
                target_depth = max_depth
                room = get_room_objects(state, TARGETS[obj_type], max_depth)
                while room[max_depth - target_depth] != -1:
                    target_depth -= 1

                if not check_blocking_obj_in_hall(state, i, TARGETS[obj_type]):
                    yield go_to_target(i, maze_state, target_depth, room_out_cost, object_location, max_depth)

        if obj[0] == -1:
            continue

        if obj[1] > 1 and is_obj_blocked_in_room(i, state):
            continue

        for dest_loc in [0, 1, 3, 5, 7, 9, 10]:
            cost_to_move = COSTS[obj_type] * (abs(obj[0] - dest_loc) + obj[1])

            if check_blocking_obj_in_hall(state, i, dest_loc):
                continue

            locations_copy = list(state)
            locations_copy[i] = (-1, -1, dest_loc, obj_type)
            yield state_cost + cost_to_move, tuple(locations_copy)


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
    initial_state = get_initial_state(raw_rooms, max_depth)

    visited: set[frozenset] = set()
    pq: List[State] = [(0, initial_state)]
    while pq:
        curr_cost, curr_state = heapq.heappop(pq)
        key = frozenset(curr_state)
        if key in visited:
            continue
        visited.add(key)
        if is_finish_state(curr_state, max_depth):
            return curr_cost
        for cost, next_state in get_all_sub_states((curr_cost, curr_state), max_depth):
            if frozenset(next_state) in visited:
                continue
            heapq.heappush(pq, (cost, next_state))
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
