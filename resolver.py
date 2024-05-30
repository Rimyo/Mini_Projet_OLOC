import pulp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file_path = 'inst_100000.flp'
num_cities: int
data = []


# Ouvrir le fichier et lit les données afin de les stocker dans un dataframe
with open(file_path, 'r') as file:
    # Lis la première ligne qui correspong au nombre de ville dans le fichier
    num_cities = int(file.readline().strip())
    
    #Les données sont stockées dans un dictionnaire avant d'éetre converti en dataframe
    for _ in range(num_cities):
        line = file.readline().strip()
        parts = line.split()
        data.append({
            'id': int(parts[0]),
            'code_postal': int(parts[1]),
            'x': float(parts[2]),
            'y': float(parts[3]),
        })


# Convertir en dataframe
df = pd.DataFrame(data)

print(df)

#Creation d'un tableau de distance dont la valeur d'une case i j correspond à la distance entre la ville i et la ville j
num_cities = df.shape[0]
distances = np.zeros((num_cities, num_cities))

for i in range(num_cities):
    for j in range(num_cities):
        if i != j:
            distances[i][j] = np.sqrt((df.iloc[i]['x'] - df.iloc[j]['x'])**2 + 
                                        (df.iloc[i]['y'] - df.iloc[j]['y'])**2)
        else:
            distances[i][j] = 0  # Distance to itself is zero


# Nombre de villes
n = num_cities
p = 14  # Nombre d'antennes  


#on utilise le solveur par défaut de Pulp, car pas de licence CPLEX
#cplex_solver = pulp.CPLEX_CMD() 

# Définition du problème : minimisation 
problem = pulp.LpProblem("p-centre Problem", pulp.LpMinimize)

# définition des variables de décisions
x = pulp.LpVariable.dicts("x", (range(n), range(n)), cat='Binary')
z = pulp.LpVariable('z', lowBound=0)

# fonction objective
problem += z

# ---Contraintes---
# Contrainte 1
problem += pulp.lpSum(x[i][i] for i in range(n)) <= p
# Contrainte 2
for i in range(n):
    problem += pulp.lpSum(x[i][j] for j in range(n)) == 1
# Contrainte 3
for i in range(n):
    for j in range(n):
        if j != i:
            problem += x[i][j] <= x[j][j]
# Contrainte 4        
for j in range(n):
    problem += pulp.lpSum(distances[i][j] * x[i][j] for i in range(n)) <= z


# Résolution du problème avec le solveur pré défini
# problem.solve()

problem.writeLP("problem.lp")


# dictionnaire contenant les key-value: ville i et son antenna j
dict_antenna = {}
for i in range(n):
    for j in range(n):
        if pulp.value(x[i][j]) == 1:
            dict_antenna[i] = j

# Création du graphe
plt.figure(figsize=(10, 8))

# Ajout des villes sous forme de point bleu
plt.scatter(df['x'], df['y'], color='blue', s=10, zorder=2)

# Ajout des antennes sous forme de ligne rouge reliant l'antenne et les villes couvertes
for i in range(n):
    if i in dict_antenna:
        antenna = dict_antenna[i]
        plt.plot([df.iloc[i]['x'], df.iloc[antenna]['x']], [df.iloc[i]['y'], df.iloc[antenna]['y']], 'r-', zorder=1)

plt.title('City dict_antenna to Antennas')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.show()


print('Optimal value of z:', pulp.value(problem.objective))


# print('Optimal value of z:', pulp.value(problem.objective))
# for i in range(n):
#     for j in range(n):
#         if pulp.value(x[i][j]) == 1:
#             print(f'Point {i} is assigned to antenna {j}')
