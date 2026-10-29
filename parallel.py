from multiprocessing import Pool
from routing import shortest_path


def calculate_route(args):
    graph, start, destination = args

    path, distance = shortest_path(
        graph,
        start,
        destination
    )

    return path, distance


def parallel_routes(graph, start, destinations):
    tasks = []

    for destination in destinations:
        tasks.append(
            (graph, start, destination)
        )

    with Pool() as pool:
        results = pool.map(
            calculate_route,
            tasks
        )

    return results