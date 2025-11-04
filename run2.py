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
        if distance == min_distance:
            if target is None or gateway < target:
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
        if distance_to_target == min_distance:
            if min_next_node is None or neighbor < min_next_node:
                min_distance = distance_to_target
                min_next_node = neighbor
    return min_next_node


def encode_state(virus_pos: str, graph: dict[str, list[str]], gateways: set[str]) -> tuple:
    gateway_edges = []
    for gateway in sorted(gateways):
        for neighbor in graph[gateway]:
            if neighbor.islower():
                gateway_edges.append((gateway, neighbor))
    return virus_pos, tuple(gateway_edges)


def solve_recursive(virus_pos: str, graph: dict[str, list[str]], gateways: set[str], cache: dict) -> list[str] | None:
    key = encode_state(virus_pos, graph, gateways)
    if key in cache:
        return cache[key]

    possible_disconnects = []
    for gateway in sorted(gateways):
        for neighbor in sorted(graph[gateway]):
            if neighbor.islower():
                possible_disconnects.append((gateway, neighbor))

    if not possible_disconnects:
        cache[key] = []
        return []

    for gateway, neighbor in possible_disconnects:
        graph[gateway].remove(neighbor)
        graph[neighbor].remove(gateway)

        next_move = get_virus_move(virus_pos, graph, gateways)
        if next_move is None:
            graph[gateway].append(neighbor)
            graph[neighbor].append(gateway)
            graph[gateway].sort()
            graph[neighbor].sort()
            cache[key] = [f"{gateway}-{neighbor}"]
            return cache[key]

        if next_move in gateways:
            graph[gateway].append(neighbor)
            graph[neighbor].append(gateway)
            graph[gateway].sort()
            graph[neighbor].sort()
            continue

        result = solve_recursive(next_move, graph, gateways, cache)
        graph[gateway].append(neighbor)
        graph[neighbor].append(gateway)
        graph[gateway].sort()
        graph[neighbor].sort()

        if result is not None:
            cache[key] = [f"{gateway}-{neighbor}"] + result
            return cache[key]

    cache[key] = None
    return None


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
        nodes.add(u)
        nodes.add(v)
        if u.isupper():
            gateways.add(u)
        if v.isupper():
            gateways.add(v)

    for n in list(graph.keys()):
        graph[n].sort()

    cache = {}
    result = solve_recursive(virus_start, graph, gateways, cache)
    return result or []


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
