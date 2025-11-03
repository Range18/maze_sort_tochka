from maze_state import MazeState
from object_location import ObjectInfo


def get_initial_state(raw_rooms: list[str], depth: int) -> MazeState:
    rows = [raw_room[3:10:2] for raw_room in raw_rooms]
    print(rows)
    locations = []
    for i in range(depth):
        for j in range(len(rows[i])):
            locations.append(ObjectInfo(rows[i][j], (j + 1) * 2, i + 1, -1))
    return MazeState(locations)


def get_depth(maze: list[str]) -> int:
    return len(maze) - 3
