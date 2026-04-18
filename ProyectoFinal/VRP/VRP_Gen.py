import random
import csv
import matplotlib.pyplot as plt
import os

script_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_path, "data")
if not os.path.exists(data_path):
    os.makedirs(data_path)

# Function to generate a VRP instance
def generate_vrp(num_clients, num_vehicles, vehicle_capacity, file_name, seed_value):
    """
    Generate a basic Vehicle Routing Problem (VRP) instance.
    """
    # Generate random coordinates and demand for each client
    random.seed(seed_value)
    clients = []
    for client_id in range(1, num_clients):
        x, y = random.uniform(-100, 100), random.uniform(-100, 100)  # 2D coordinates in a 100x100 grid
        demand = random.randint(3, 20)
        clients.append({"ID": client_id, "X": x, "Y": y, "Demand": demand})

    # generate depot at average coordinates of clients
    depot = {
        "ID": 0,
        "X": sum(client["X"] for client in clients) / num_clients,
        "Y": sum(client["Y"] for client in clients) / num_clients,
        "Demand": 0
    }

    print(f"Depot selected: {depot}")
    print(f"Number of vehicles: {num_vehicles}, Vehicle capacity: {vehicle_capacity}")

    # Save data to CSV
    save_to_csv(clients, depot, num_vehicles, vehicle_capacity, file_name)


# Function to save the VRP instance to CSV
def save_to_csv(clients, depot, num_vehicles, vehicle_capacity, file_name):
    """
    Save the VRP instance into CSV.
    """
    # Save client and depot data
    file_path = os.path.join(data_path, file_name)
    with open(file_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["ID", "X", "Y", "Demand"], delimiter=";")
        writer.writeheader()
        writer.writerow(depot)  # Write depot as the first row
        writer.writerows(clients)  # Write clients

    vehicle_file_path = os.path.join(data_path, "vehicles-" + file_name)
    # Save vehicle data
    with open(vehicle_file_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Vehicle_ID", "Capacity"], delimiter=";")
        writer.writeheader()
        for vehicle_id in range(1, num_vehicles + 1):
            writer.writerow({"Vehicle_ID": vehicle_id, "Capacity": vehicle_capacity})

    print("Data saved as CSV files: 'vrp_clients.csv' and 'vrp_vehicles.csv'")


# Function to read CSV data for plotting
def read_vrp_data(file_name):
    """
    Read the VRP data from CSV files and prepare it for plotting.

    Returns:
        depot (dict): Information about the depot.
        clients (list): List of all clients (excluding the depot).
    """
    clients = []
    depot = None

    # Read client and depot data
    file_path = os.path.join(data_path, file_name)
    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            client = {
                "ID": int(row["ID"]),
                "X": float(row["X"]),
                "Y": float(row["Y"]),
                "Demand": int(row["Demand"])
            }
            if client["ID"] == 0:  # Depot has ID 0
                depot = client
            else:
                clients.append(client)

    # Read vehicle data
    vehicle_file_path = os.path.join(data_path, "vehicles-" + file_name)
    vehicles = []
    if os.path.exists(vehicle_file_path):
        with open(vehicle_file_path, mode="r") as file:
            reader = csv.DictReader(file, delimiter=";")

            for row in reader:
                vehicle = {
                    "Vehicle_ID": int(row["Vehicle_ID"]),
                    "Capacity": int(row["Capacity"])
                }
                vehicles.append(vehicle)
    return depot, clients, vehicles


# Plot the VRP instance
def plot_vrp(file_name):
    """
    Plot the generated VRP instance using matplotlib.
    """
    # Read the data
    depot, clients, vehicles = read_vrp_data(file_name)

    # Separate x and y coordinates for clients and depot
    client_x = [client["X"] for client in clients]
    client_y = [client["Y"] for client in clients]
    demands = [client["Demand"] for client in clients]

    # Plot the clients
    plt.scatter(client_x, client_y, c="blue", label="Clients", s=[d * 10 for d in demands], alpha=0.7)

    # Plot the depot
    plt.scatter(depot["X"], depot["Y"], c="red", label="Depot", s=100, marker="X")

    # Add labels and legend
    plt.title("Generated VRP Instance")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend()
    plt.grid(True)
    plt.show()


# Example usage
if __name__ == "__main__":
    _num_clients = 100
    _num_vehicles = 2
    _vehicle_capacity = 20
    _seed_value = 125
    _problem_name = "vrp.csv"

    # Generate and save the VRP problem
    generate_vrp(_num_clients, _num_vehicles, _vehicle_capacity, _problem_name, _seed_value)
    # Read and plot the generated VRP instance
    plot_vrp(_problem_name)
