from flask import Flask, render_template, request
import sqlite3
import random
import math
import time
import os 

app = Flask(__name__)

# === وظائف الخوارزمية الجينية ===
def fetch_locations():
    """جلب بيانات المواقع من قاعدة البيانات."""
    conn = sqlite3.connect('delivery.db')
    cursor = conn.cursor()
    cursor.execute('SELECT LocationID, X, Y FROM Locations')
    locations = cursor.fetchall()
    conn.close()
    return locations

def calculate_distance(x1, y1, x2, y2):
    """حساب المسافة الإقليدية."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def calculate_total_distance(path, locations):
    """حساب المسافة الإجمالية."""
    total_distance = 0
    for i in range(len(path) - 1):
        loc1 = locations[path[i] - 1]
        loc2 = locations[path[i + 1] - 1]
        total_distance += calculate_distance(loc1[1], loc1[2], loc2[1], loc2[2])
    return total_distance

def generate_initial_population(size, num_locations):
    """توليد السكان الأوليين."""
    return [random.sample(range(1, num_locations + 1), num_locations) for _ in range(size)]

def mutate(path):
    """تنفيذ طفرة."""
    idx1, idx2 = random.sample(range(len(path)), 2)
    path[idx1], path[idx2] = path[idx2], path[idx1]

def genetic_algorithm(locations, num_generations, population_size):
    """الخوارزمية الجينية."""
    num_locations = len(locations)
    population = generate_initial_population(population_size, num_locations)

    best_path = None
    best_cost = float('inf')

    for generation in range(num_generations):
        costs = [calculate_total_distance(path, locations) for path in population]
        sorted_population = [path for _, path in sorted(zip(costs, population))]

        if costs[0] < best_cost:
            best_cost = costs[0]
            best_path = sorted_population[0]

        next_generation = sorted_population[:population_size // 2]
        for _ in range(population_size // 2):
            parent1, parent2 = random.sample(next_generation, 2)
            cut = random.randint(1, num_locations - 2)
            child = parent1[:cut] + [gene for gene in parent2 if gene not in parent1[:cut]]
            mutate(child)
            next_generation.append(child)

        population = next_generation

    return best_path, best_cost

# === صفحات Flask ===
@app.route('/')
def index():
    """الصفحة الرئيسية."""
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run():
    """تشغيل الخوارزمية وعرض النتائج."""
    num_generations = int(request.form['generations'])
    population_size = int(request.form['population'])
    locations = fetch_locations()

    start_time = time.time()
    best_path, best_cost = genetic_algorithm(locations, num_generations, population_size)
    end_time = time.time()

    return render_template(
        'results.html',
        best_path=best_path,
        best_cost=round(best_cost, 2),
        execution_time=round(end_time - start_time, 2),
    )

if __name__ == '__main__':
 app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
