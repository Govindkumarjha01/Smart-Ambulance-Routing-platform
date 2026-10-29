import tkinter as tk
from tkinter import ttk, messagebox
import csv
import time
import multiprocessing

from routing import load_roads, shortest_path
from parallel import parallel_routes



def load_ambulances(filename):
    ambulances = []

    with open(filename, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            ambulances.append(row)

    return ambulances



def load_hospitals(filename):
    hospitals = []

    with open(filename, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            hospitals.append(row)

    return hospitals



def main():

    
    graph = load_roads("data/roads.csv")
    ambulances = load_ambulances("data/ambulances.csv")
    hospitals = load_hospitals("data/hospitals.csv")

    
    def find_route():

        patient_location = location_box.get()
        emergency_level = emergency_box.get()

        if patient_location == "":
            messagebox.showwarning(
                "Input Error",
                "Please select patient location."
            )
            return

        if emergency_level == "":
            messagebox.showwarning(
                "Input Error",
                "Please select emergency level."
            )
            return

        
        nearest_ambulance = None
        nearest_ambulance_distance = float("inf")

        for ambulance in ambulances:

            if ambulance["status"].lower() != "available":
                continue

            ambulance_location = ambulance["location"]

            path, distance = shortest_path(
                graph,
                ambulance_location,
                patient_location
            )

            if distance < nearest_ambulance_distance:
                nearest_ambulance_distance = distance
                nearest_ambulance = ambulance

       
        nearest_hospital = None
        nearest_hospital_distance = float("inf")
        nearest_hospital_path = []

        for hospital in hospitals:

            hospital_location = hospital["location"]

            path, distance = shortest_path(
                graph,
                patient_location,
                hospital_location
            )

            if distance < nearest_hospital_distance:
                nearest_hospital_distance = distance
                nearest_hospital = hospital
                nearest_hospital_path = path

       
        hospital_locations = []

        for hospital in hospitals:
            hospital_locations.append(
                hospital["location"]
            )

        
        start_time = time.perf_counter()

        for destination in hospital_locations:

            shortest_path(
                graph,
                patient_location,
                destination
            )

        sequential_time = (
            time.perf_counter() - start_time
        )

       
        start_time = time.perf_counter()

        parallel_results = parallel_routes(
            graph,
            patient_location,
            hospital_locations
        )

        parallel_time = (
            time.perf_counter() - start_time
        )

        
        if parallel_time > 0:
            speedup = sequential_time / parallel_time
        else:
            speedup = 0

       
        result_text.config(
            state="normal"
        )

        result_text.delete(
            "1.0",
            tk.END
        )

        result_text.insert(
            tk.END,
            "🚑 SMART AMBULANCE ROUTING PLATFORM\n"
        )

        result_text.insert(
            tk.END,
            "========================================\n\n"
        )

        result_text.insert(
            tk.END,
            "📍 PATIENT INFORMATION\n"
        )

        result_text.insert(
            tk.END,
            "Patient Location : "
            + patient_location
            + "\n"
        )

        result_text.insert(
            tk.END,
            "Emergency Level  : "
            + emergency_level
            + "\n\n"
        )

        result_text.insert(
            tk.END,
            "🚑 AMBULANCE\n"
        )

        result_text.insert(
            tk.END,
            "Nearest Ambulance : "
            + nearest_ambulance["name"]
            + "\n"
        )

        result_text.insert(
            tk.END,
            "Location          : "
            + nearest_ambulance["location"]
            + "\n"
        )

        result_text.insert(
            tk.END,
            "Distance          : "
            + str(nearest_ambulance_distance)
            + " km\n\n"
        )

        result_text.insert(
            tk.END,
            "🏥 HOSPITAL & ROUTE\n"
        )

        result_text.insert(
            tk.END,
            "Nearest Hospital  : "
            + nearest_hospital["name"]
            + "\n"
        )

        result_text.insert(
            tk.END,
            "Hospital Location : "
            + nearest_hospital["location"]
            + "\n"
        )

        result_text.insert(
            tk.END,
            "Shortest Route    : "
            + " → ".join(nearest_hospital_path)
            + "\n"
        )

        result_text.insert(
            tk.END,
            "Distance          : "
            + str(nearest_hospital_distance)
            + " km\n\n"
        )

        result_text.insert(
            tk.END,
            "⚡ HPC PERFORMANCE\n"
        )

        result_text.insert(
            tk.END,
            "========================================\n"
        )

        result_text.insert(
            tk.END,
            "Sequential Time : "
            + str(round(sequential_time, 6))
            + " seconds\n"
        )

        result_text.insert(
            tk.END,
            "Parallel Time   : "
            + str(round(parallel_time, 6))
            + " seconds\n"
        )

        result_text.insert(
            tk.END,
            "Speedup         : "
            + str(round(speedup, 2))
            + "x\n"
        )

        result_text.config(
            state="disabled"
        )

  
    window = tk.Tk()

    window.title(
        "Smart Ambulance Routing Platform"
    )

    window.geometry(
        "700x750"
    )

    window.resizable(
        False,
        False
    )

    
    header = tk.Frame(
        window,
        padx=20,
        pady=20
    )

    header.pack(
        fill="x"
    )

    title = tk.Label(
        header,
        text="🚑 Smart Ambulance Routing",
        font=("Arial", 24, "bold")
    )

    title.pack()

    subtitle = tk.Label(
        header,
        text="HPC Based Emergency Route Planning",
        font=("Arial", 11)
    )

    subtitle.pack(
        pady=5
    )

 
    input_frame = tk.LabelFrame(
        window,
        text="  Emergency Information  ",
        font=("Arial", 12, "bold"),
        padx=20,
        pady=15
    )

    input_frame.pack(
        padx=30,
        pady=10,
        fill="x"
    )

  
    location_label = tk.Label(
        input_frame,
        text="Patient Location:",
        font=("Arial", 11, "bold")
    )

    location_label.grid(
        row=0,
        column=0,
        padx=10,
        pady=10
    )

    location_box = ttk.Combobox(
        input_frame,
        values=[
    "Knowledge park",
    "jagat",
    "pari Chowk",
    "Suraj pur",
    "sutyana",
    "Kulesra",
    "Alpha 2"
],
        state="readonly",
        width=25
    )

    location_box.grid(
        row=0,
        column=1,
        padx=10,
        pady=10
    )

   
    emergency_label = tk.Label(
        input_frame,
        text="Emergency Level:",
        font=("Arial", 11, "bold")
    )

    emergency_label.grid(
        row=1,
        column=0,
        padx=10,
        pady=10
    )

    emergency_box = ttk.Combobox(
        input_frame,
        values=[
            "Critical",
            "Serious",
            "Normal"
        ],
        state="readonly",
        width=25
    )

    emergency_box.grid(
        row=1,
        column=1,
        padx=10,
        pady=10
    )

   
    route_button = tk.Button(
        window,
        text="🔎  FIND BEST ROUTE",
        command=find_route,
        font=("Arial", 12, "bold"),
        padx=20,
        pady=10,
        cursor="hand2"
    )

    route_button.pack(
        pady=15
    )

    
    result_frame = tk.LabelFrame(
        window,
        text="  Routing Result  ",
        font=("Arial", 12, "bold"),
        padx=10,
        pady=10
    )

    result_frame.pack(
        padx=30,
        pady=10,
        fill="both",
        expand=True
    )

    result_text = tk.Text(
        result_frame,
        height=20,
        width=70,
        font=("Consolas", 11),
        wrap="word"
    )

    result_text.pack(
        fill="both",
        expand=True
    )

    result_text.insert(
        tk.END,
        "Select patient location and emergency level,\n"
        "then click 'FIND BEST ROUTE'."
    )

    result_text.config(
        state="disabled"
    )

    
    window.mainloop()



if __name__ == "__main__":

    multiprocessing.freeze_support()

    main()