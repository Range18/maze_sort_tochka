import sys
import heapq
from typing import Tuple, List

TARGETS = {0: 2, 1: 4, 2: 6, 3: 8}
COSTS = {0: 1, 1: 10, 2: 100, 3: 1000}
TYPES = {"A": 0, "B": 1, "C": 2, "D": 3}

Location = Tuple[int, int, int, int]
State = Tuple[int, Tuple[Location]]


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def is_finish_state(locations: tuple[Location]) -> bool:
    for i, obj in enumerate(locations):
        if obj[0] != TARGETS[obj[3]]:
            return False
    return True


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def get_initial_state(raw_rooms: list[str], depth: int) -> tuple[int, Tuple[Location]]:
    rows = [raw_room[3:10:2] for raw_room in raw_rooms]
    locations = []
    for i in range(depth):
        for j in range(len(rows[i])):
            locations.append(((j + 1) * 2, i + 1, -1, TYPES[rows[i][j]]))
    locations.sort(key=lambda x: x[3])
    return 0, tuple(locations)


def get_depth(maze: list[str]) -> int:
    return len(maze) - 3


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def check_blocking_obj_in_hall(locations: tuple[Location], obj_id: int, dest_room: int) -> bool:
    room, _, hall, _ = locations[obj_id]
    loc = max(room, hall)

    for i in range(len(locations)):
        _, _, other_hall, _ = locations[i]
        if i == obj_id or other_hall == -1:
            continue

        if (loc <= other_hall <= dest_room) or (
                dest_room <= other_hall <= loc):
            return True
    return False


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def get_type_objects(obj_id: int, state: tuple[Location]) -> tuple[Location]:
    locations = []
    _, _, _, obj_type = state[obj_id]
    for i in range(len(state)):
        _, _, _, other_type = state[i]
        if i != obj_id and other_type == obj_type:
            locations.append(state[i])
    return tuple(locations)


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def get_room_objects(state: tuple[Location], target: int, max_depth: int) -> list[int]:
    room = [-1] * max_depth
    for i in range(len(state)):
        room_id, depth, _, obj_type = state[i]
        if room_id == target:
            room[max_depth - depth] = obj_type
    return room


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def is_all_in_right_room(obj_id: int, state: tuple[Location]) -> bool:
    room_id, _, _, obj_type = state[obj_id]
    if room_id != TARGETS[obj_type]:
        return False
    for other in get_type_objects(obj_id, state):
        if other[0] != TARGETS[obj_type]:
            return False
    return True


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def is_target_with_foreigners(obj_id: int, state: tuple[Location]) -> bool:
    _, _, _, obj_type = state[obj_id]
    target = TARGETS[obj_type]
    for i in range(len(state)):
        other_room, other_depth, _, other_type = state[i]
        if i == obj_id or other_room == -1 or other_type == obj_type:
            continue
        if other_room == target:
            return True
    return False


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def is_any_in_target(obj_id: int, state: tuple[Location]) -> bool:
    obj = state[obj_id]
    target = TARGETS[obj[3]]
    for i in range(len(state)):
        other_room, other_depth, _, _ = state[i]
        if i == obj_id or other_room == -1:
            continue
        if other_room == target:
            return True
    return False


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def is_obj_blocked_in_room(obj_id: int, state: tuple[Location]) -> bool:
    room_id, obj_depth, _, _ = state[obj_id]
    for i in range(len(state)):
        other_room, other_depth, _, _ = state[i]
        if i == obj_id:
            continue
        if other_room == room_id and other_depth != -1 and other_depth < obj_depth:
            return True
    return False


# ObjectInfo (room_id: int = -1, depth: int = -1, hall_location: int = -1)
# MazeState (cost, (ObjectInfos))
def go_to_target(obj_index: int, maze_state: State, depth: int, room_out_cost: int,
                 object_location: int) -> State:
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
        room_id, obj_depth, hall, obj_type = obj
        if hall == -1:
            if room_id == TARGETS[obj_type]:
                if obj_depth == max_depth:
                    continue
                if get_room_objects(state, TARGETS[obj_type], max_depth)[:max_depth - obj_depth] == [obj_type] * (
                        max_depth - obj_depth):
                    continue

        room_out_cost = 0 if room_id == -1 else obj_depth
        object_location = max(room_id, hall)

        dest_room = TARGETS[obj_type]

        is_not_obj_blocked_in_room = True
        if room_id != -1 and obj_depth > 1:
            is_not_obj_blocked_in_room = not is_obj_blocked_in_room(i, state)

        if is_not_obj_blocked_in_room:
            if not is_target_with_foreigners(i, state):
                target_depth = max_depth
                room = get_room_objects(state, dest_room, max_depth)
                while room[max_depth - target_depth] != -1:
                    target_depth -= 1

                if not check_blocking_obj_in_hall(state, i, dest_room):
                    yield go_to_target(i, maze_state, target_depth, room_out_cost, object_location)

        if room_id == -1:
            continue

        if obj_depth > 1 and is_obj_blocked_in_room(i, state):
            continue

        for dest_loc in [0, 1, 3, 5, 7, 9, 10]:
            cost_to_move = COSTS[obj_type] * (abs(room_id - dest_loc) + obj_depth)

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
    pq: List[State] = [initial_state]
    while pq:
        curr_cost, curr_state = heapq.heappop(pq)
        key = frozenset(curr_state)
        if key in visited:
            continue
        visited.add(key)
        if is_finish_state(curr_state):
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
