import sys
import heapq
from typing import Tuple, List

from constants import COSTS, TARGETS
from maze_state import MazeState
from object_location import ObjectInfo
from objects_service import is_all_in_right_room, is_obj_blocked_in_room, is_target_with_foreigners, get_type_objects, \
    check_blocking_obj_in_hall, is_any_in_target, go_to_target
from utils import get_depth, get_initial_state


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
                partner = get_type_objects(obj, state)[0]

                if partner.room_id == TARGETS[obj.type]:
                    if partner.depth != 1:

                        if not check_blocking_obj_in_hall(state.locations, obj, TARGETS[obj.type]):
                            yield go_to_target(obj, i, state, 1, room_out_cost, object_location)

                else:
                    if not is_any_in_target(obj, state):
                        if not check_blocking_obj_in_hall(state.locations, obj, TARGETS[obj.type]):
                            yield go_to_target(obj, i, state, 2, room_out_cost, object_location)
        if obj.room_id == -1:
            continue

        if obj.depth == max_depth and is_obj_blocked_in_room(obj, state):
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
