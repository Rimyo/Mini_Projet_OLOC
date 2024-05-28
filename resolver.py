import pulp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file_path = 'inst_100000.flp'
num_cities: int
data = []

with open(file_path, 'r') as file:
    # Read the first line to get the number of cities
    num_cities = int(file.readline().strip())
    
    # Read the rest of the file
    for _ in range(num_cities):
        line = file.readline().strip()
        parts = line.split()
        # Append the data as a dictionary
        data.append({
            'id': int(parts[0]),
            'code_postal': int(parts[1]),
            'x': float(parts[2]),
            'y': float(parts[3]),
        })


# Convert to DataFrame for easier manipulation
df = pd.DataFrame(data)

print(df)

#Create a tab for each case i:j, stocks the distance between city i and city j
num_cities = df.shape[0]
distances = np.zeros((num_cities, num_cities))

for i in range(num_cities):
    for j in range(num_cities):
        if i != j:
            distances[i][j] = np.sqrt((df.iloc[i]['x'] - df.iloc[j]['x'])**2 + 
                                        (df.iloc[i]['y'] - df.iloc[j]['y'])**2)
        else:
            distances[i][j] = 0  # Distance to itself is zero


# Number of points (example, adjust as needed)
n = num_cities
p = 20  # Example value for number of antennas
#cplex_solver = pulp.CPLEX_CMD() #define the solver used: CPLEX here

# Define the problem
problem = pulp.LpProblem("p-centre Problem", pulp.LpMinimize)

# Define decision variables
x = pulp.LpVariable.dicts("x", (range(n), range(n)), cat='Binary')
z = pulp.LpVariable('z', lowBound=0)

# Objective function
problem += z

# Constraints
for i in range(n):
    problem += pulp.lpSum(x[i][j] for j in range(n)) == 1
for j in range(n):
    problem += pulp.lpSum(x[i][i] for i in range(n)) <= p
    for i in range(n):
        problem += x[i][j] <= x[j][j]
    problem += pulp.lpSum(distances[i][j] * x[i][j] for i in range(n)) <= z

# Solve the problem
problem.solve()

def plot_cities_and_assignments(df, assignments):
    plt.figure(figsize=(10, 8))
    
    # Plot cities
    plt.scatter(df['x'], df['y'], color='blue', s=100, zorder=5)
    
    # Plot assignments
    colors = plt.cm.get_cmap('tab10', len(assignments)).colors
    for idx, (city, antenna) in enumerate(assignments.items()):
        city_coords = df.loc[df['id'] == city, ['x', 'y']].values[0]
        antenna_coords = df.loc[df['id'] == antenna, ['x', 'y']].values[0]
        plt.plot([city_coords[0], antenna_coords[0]], [city_coords[1], antenna_coords[1]], 
                 color=colors[idx % len(colors)], linewidth=2)
    
    # Plot antennas with a different marker
    antennas = list(assignments.values())
    antenna_coords = df[df['id'].isin(antennas)]
    plt.scatter(antenna_coords['x'], antenna_coords['y'], color='red', s=150, zorder=5, marker='x')
    
    plt.title('City Assignments to Antennas')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()

assignments = np.zeros(num_cities)
for j in range(num_cities):
    if pulp.value(x[j][j]) == 1:
        assignments[j] = 1

print(assignments)

print('Optimal value of z:', pulp.value(problem.objective))
plot_cities_and_assignments(df, assignments)

# print('Optimal value of z:', pulp.value(problem.objective))
# for i in range(n):
#     for j in range(n):
#         if pulp.value(x[i][j]) == 1:
#             print(f'Point {i} is assigned to antenna {j}')
