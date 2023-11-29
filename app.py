from flask import Flask, render_template, request, jsonify
import heapq

app = Flask(__name__)

# Define a simple map between cities and their straight-line distances to the goal
city_map = {
    'A': {'B': 5, 'C': 9, 'D': 4},
    'B': {'A': 5, 'C': 3, 'E': 7},
    'C': {'A': 9, 'B': 3, 'D': 2, 'E': 6, 'F': 3},
    'D': {'A': 4, 'C': 2, 'F': 8},
    'E': {'B': 7, 'C': 6, 'F': 5},
    'F': {'C': 3, 'D': 8, 'E': 5}
}

# Assume we have heuristics data for each city
heuristics = {
    'A': 10,
    'B': 8,
    'C': 3,
    'D': 7,
    'E': 4,
    'F': 0  # Goal
}

average_duration_per_km = 1
speed_reduction_per_package = 0.1

class Node:
    def __init__(self, location, parent=None, g=0, h=0):
        self.location = location
        self.parent = parent
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, other):
        return self.f < other.f

def heuristic(location, goal, num_packages, w1, w2, w3):
    h1 = heuristics[location]
    h2 = average_duration_per_km
    h3 = speed_reduction_per_package * num_packages
    return (w1 * h1) + (w2 * h2 * h1) + (w3 * h3 * h1)

def a_star(start, goal, num_packages, w1, w2, w3):
    open_list = []
    closed_list = set()

    start_node = Node(start, None, 0, heuristic(start, goal, num_packages, w1, w2, w3))
    heapq.heappush(open_list, start_node)

    while open_list:
        current_node = heapq.heappop(open_list)
        closed_list.add(current_node.location)

        if current_node.location == goal:
            path = []
            while current_node:
                path.append(current_node.location)
                current_node = current_node.parent
            return path[::-1]

        for neighbor, distance in city_map[current_node.location].items():
            if neighbor in closed_list:
                continue

            g_cost = current_node.g + distance
            h_cost = heuristic(neighbor, goal, num_packages, w1, w2, w3)
            neighbor_node = Node(neighbor, current_node, g_cost, h_cost)

            if neighbor in (n.location for n in open_list):
                open_node = next(n for n in open_list if n.location == neighbor_node.location)
                if neighbor_node.g < open_node.g:
                    open_list.remove(open_node)
                    heapq.heappush(open_list, neighbor_node)
            else:
                heapq.heappush(open_list, neighbor_node)

    return None  # No path found

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_route', methods=['POST'])
def search_route():
    start = request.form.get('start').upper()
    goal = request.form.get('goal').upper()
    num_packages = int(request.form.get('num_packages'))
    w1 = float(request.form.get('w1'))
    w2 = float(request.form.get('w2'))
    w3 = float(request.form.get('w3'))

    if start not in city_map or goal not in city_map:
        return jsonify({'result': 'Invalid start or goal city.'})

    path = a_star(start, goal, num_packages, w1, w2, w3)
    
    if path is not None:
        result = "Rute ditemukan: " + " -> ".join(path)
    else:
        result = "Rute tidak ditemukan"

    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
