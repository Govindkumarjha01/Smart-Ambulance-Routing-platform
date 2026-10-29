import csv
import time
from pathlib import Path

from routing import load_roads, shortest_path
from parallel import parallel_routes


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def load_ambulances(filename):
    with open(filename, "r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def find_available_ambulances(ambulances):
    return [
        ambulance
        for ambulance in ambulances
        if ambulance.get("status", "").strip().lower() == "available"
    ]


def load_hospitals(filename):
    with open(filename, "r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def get_valid_location(graph):
    while True:
        location = input(
            "Enter Patient Location (A-F): "
        ).strip().upper()

        if location in graph:
            return location

        print("Invalid location!")
        print("Available locations:", ", ".join(sorted(graph.keys())))


def get_emergency_level():
    valid_levels = {"CRITICAL", "SERIOUS", "NORMAL"}

    while True:
        level = input(
            "Enter Emergency Level (Critical/Serious/Normal): "
        ).strip().upper()

        if level in valid_levels:
            return level.title()

        print("Invalid emergency level! Try again.")


def get_safe_route(graph, source, destination):
    source = str(source).strip().upper()
    destination = str(destination).strip().upper()

    if source not in graph or destination not in graph:
        return [], float("inf")

    if source == destination:
        return [source], 0

    try:
        path, distance = shortest_path(
            graph, source, destination
        )

        if not path or distance == float("inf"):
            return [], float("inf")

        return path, distance

    except (KeyError, TypeError, ValueError) as error:
        print(f"Routing error ({source} -> {destination}): {error}")
        return [], float("inf")


def main():
    print("\n======================================")
    print(" SMART AMBULANCE ROUTING PLATFORM")
    print("======================================")

    try:
        graph = load_roads(str(DATA_DIR / "roads.csv"))
        ambulances = load_ambulances(DATA_DIR / "ambulances.csv")
        hospitals = load_hospitals(DATA_DIR / "hospitals.csv")

    except (FileNotFoundError, OSError, csv.Error) as error:
        print("Data loading error:", error)
        return

    if not graph:
        print("Road network is empty.")
        return

    if not hospitals:
        print("No hospitals found.")
        return

    available_ambulances = find_available_ambulances(ambulances)

    if not available_ambulances:
        print("No available ambulances found.")
        return

    print("\nAvailable Ambulances:")
    print("--------------------------------------")

    for ambulance in available_ambulances:
        print(
            f'{ambulance["id"]} - '
            f'{ambulance["name"]} - '
            f'Location: {ambulance["location"]}'
        )

    patient_location = get_valid_location(graph)
    emergency_level = get_emergency_level()

    nearest_ambulance = None
    nearest_distance = float("inf")
    nearest_ambulance_route = []

    for ambulance in available_ambulances:
        ambulance_location = ambulance["location"].strip().upper()

        route, distance = get_safe_route(
            graph,
            ambulance_location,
            patient_location
        )

        if distance < nearest_distance:
            nearest_distance = distance
            nearest_ambulance = ambulance
            nearest_ambulance_route = route

    if nearest_ambulance is None:
        print("\nNo reachable ambulance found.")
        return

    print("\nNearest Ambulance:")
    print("--------------------------------------")

    print(
        nearest_ambulance["id"],
        "-",
        nearest_ambulance["name"]
    )

    print(
        "Ambulance Location:",
        nearest_ambulance["location"]
    )

    print(
        "Ambulance Route:",
        " -> ".join(nearest_ambulance_route)
    )

    print(
        "Distance to Patient:",
        nearest_distance,
        "km"
    )

    nearest_hospital = None
    nearest_hospital_distance = float("inf")
    nearest_hospital_route = []

    for hospital in hospitals:
        hospital_location = hospital["location"].strip().upper()

        route, distance = get_safe_route(
            graph,
            patient_location,
            hospital_location
        )

        if distance < nearest_hospital_distance:
            nearest_hospital_distance = distance
            nearest_hospital = hospital
            nearest_hospital_route = route

    if nearest_hospital is None:
        print("\nNo reachable hospital found.")
        return

    print("\nNearest Hospital:")
    print("--------------------------------------")

    print(
        nearest_hospital["id"],
        "-",
        nearest_hospital["name"]
    )

    print(
        "Hospital Location:",
        nearest_hospital["location"]
    )

    print(
        "Hospital Route:",
        " -> ".join(nearest_hospital_route)
    )

    print(
        "Distance from Patient:",
        nearest_hospital_distance,
        "km"
    )

    hospital_locations = [
        hospital["location"].strip().upper()
        for hospital in hospitals
    ]

    start_time = time.perf_counter()

    sequential_results = []

    for destination in hospital_locations:
        path, distance = get_safe_route(
            graph,
            patient_location,
            destination
        )

        sequential_results.append((path, distance))

    sequential_time = time.perf_counter() - start_time

    start_time = time.perf_counter()

    try:
        parallel_results = parallel_routes(
            graph,
            patient_location,
            hospital_locations
        )
    except Exception as error:
        print("\nParallel processing error:", error)
        parallel_results = None

    parallel_time = time.perf_counter() - start_time

    if (
        parallel_results is not None
        and len(parallel_results) == len(hospitals)
    ):
        print("\nParallel Route Results:")
        print("--------------------------------------")

        for hospital, result in zip(hospitals, parallel_results):
            path, distance = result

            route_text = (
                " -> ".join(path)
                if path else "No route found"
            )

            print(
                hospital["name"],
                ":",
                route_text,
                "| Distance:",
                distance,
                "km"
            )

        print("\nPerformance Comparison:")
        print("--------------------------------------")

        print(
            "Sequential Time:",
            round(sequential_time, 6),
            "seconds"
        )

        print(
            "Parallel Time:",
            round(parallel_time, 6),
            "seconds"
        )

        if parallel_time > 0:
            speedup = sequential_time / parallel_time
            print("Speedup:", round(speedup, 2), "x")

        if sequential_results == parallel_results:
            print("Route Comparison: MATCHED")
        else:
            print("Route Comparison: RESULTS DIFFER")

    else:
        print("\nParallel results unavailable.")

    print("\nShortest Hospital Route:")
    print("--------------------------------------")

    print(" -> ".join(nearest_hospital_route))

    print(
        "Distance:",
        nearest_hospital_distance,
        "km"
    )

    print("\nEmergency Summary:")
    print("--------------------------------------")

    print("Patient Location:", patient_location)
    print("Emergency Level:", emergency_level)

    print(
        "Selected Ambulance:",
        nearest_ambulance["name"]
    )

    print(
        "Selected Hospital:",
        nearest_hospital["name"]
    )

    print(
        "Total Route Distance:",
        nearest_distance + nearest_hospital_distance,
        "km"
    )

    print("\nRouting completed successfully!")


if __name__ == "__main__":
    main()
