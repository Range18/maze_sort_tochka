import sys
from collections import defaultdict, deque


def get_best_distances(start: str, graph: dict[str, list[str]], gateways: set[str]) -> dict[str, int]:
    visited: set[str] = set()
    queue: deque[tuple[str, int]] = deque([(start, 0)])
    distances: dict[str, int] = {}
    while queue:
        node, distance = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        if node in gateways:
            distances[node] = distance
        for neighbor in graph[node]:
            if neighbor not in visited:
                queue.append((neighbor, distance + 1))
    return distances


def get_min_distance_gateway(distances: dict[str, int]) -> str:
    min_distance: float = float('inf')
    target: str | None = None
    for gateway, distance in distances.items():
        if distance < min_distance:
            min_distance = distance
            target = gateway
    return target


def get_virus_move(virus_position: str, graph: dict[str, list[str]], gateways: set[str]) -> str | None:
    distances: dict[str, int] = get_best_distances(virus_position, graph, gateways)
    if not distances:
        return None

    target: str = get_min_distance_gateway(distances)

    min_next_node: str | None = None
    min_distance: float = float('inf')
    for neighbor in sorted(graph[virus_position]):
        distance_to_target: int = (get_best_distances(neighbor, graph, {target})
                                   .get(target, float('inf')))
        if distance_to_target < min_distance:
            min_distance = distance_to_target
            min_next_node = neighbor
    return min_next_node


def solve(virus_start: str, edges: list[tuple[str, str]]) -> list[str]:
    """
    Решение задачи об изоляции вируса

    Args:
        virus_start: стартовая позиция вируса
        edges: список коридоров в формате (узел1, узел2)

    Returns:
        список отключаемых коридоров в формате "Шлюз-узел"
    """

    graph: dict[str, list[str]] = defaultdict(list)
    nodes: set[str] = set()
    gateways: set[str] = set()

    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

        if u.isupper():
            gateways.add(u)
        if v.isupper():
            gateways.add(v)

        nodes.add(u)
        nodes.add(v)

    virus_position: str = virus_start
    result: list[str] = []

    while True:
        possible_disconnects: list[tuple[str, str]] = []
        for gateway in sorted(gateways):
            for neighbor in sorted(graph[gateway]):
                if neighbor.islower():
                    possible_disconnects.append((gateway, neighbor))

        if not possible_disconnects:
            break

        disconnected_gateway, disconnected_neighbor = possible_disconnects[0]
        result.append(f'{disconnected_gateway}-{disconnected_neighbor}')

        graph[disconnected_gateway].remove(disconnected_neighbor)
        graph[disconnected_neighbor].remove(disconnected_gateway)

        next_virus_position: str = get_virus_move(virus_position, graph, gateways)
        if next_virus_position is None:
            break
        virus_position = next_virus_position

    return result


def main():
    edges = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            node1, sep, node2 = line.partition('-')
            if sep:
                edges.append((node1, node2))

    result = solve('a', edges)
    for edge in result:
        print(edge)


if __name__ == "__main__":
    main()
