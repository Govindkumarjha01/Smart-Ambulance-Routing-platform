import csv
import heapq


def load_roads(filename):
    graph = {}

    with open(filename, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            start = row["from"]
            end = row["to"]
            distance = float(row["distance"])

            if start not in graph:
                graph[start] = []

            if end not in graph:
                graph[end] = []

            graph[start].append((end, distance))
            graph[end].append((start, distance))

    return graph


def shortest_path(graph, start, destination):
    distances = {node: float("inf") for node in graph}
    previous = {node: None for node in graph}

    distances[start] = 0

    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node == destination:
            break

        if current_distance > distances[current_node]:
            continue

        for neighbor, distance in graph[current_node]:
            new_distance = current_distance + distance

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node

                heapq.heappush(
                    priority_queue,
                    (new_distance, neighbor)
                )

    path = []
    current = destination

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()

    return path, distances[destination]