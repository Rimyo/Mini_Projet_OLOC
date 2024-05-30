using CPLEX
using JuMP
using Plots
using DataFrames

# File path
file_path = "inst_0.flp"
p = 97

# Read the data from the file
num_cities = 0
x_coords = Float64[]
y_coords = Float64[]
f = Float64[]

function Lit_fichier_UFLP(nom_fichier, tabX, tabY, f)
    n = 0
    println("Lecture du fichier: ", nom_fichier)
    open(nom_fichier) do fic
        for (i, line) in enumerate(eachline(fic))
            lg = split(line, " ")  # découpe la ligne suivant les espaces et crée un tableau 
            if (i == 1) 
                n = parse(Int, lg[1])
            end
            if (i >= 2) && (i <= n + 1)
                push!(tabX, parse(Float64, lg[3]))
                push!(tabY, parse(Float64, lg[4]))	
                push!(f, parse(Float64, lg[5]))               
            end              
        end    
    end
    return n
end

num_cities = Lit_fichier_UFLP(file_path, x_coords, y_coords, f)
println("Le fichier contient ", num_cities, " villes")

# Calculer la matrice distance entre ville i et ville j
distances = zeros(Float64, num_cities, num_cities)
for i in 1:num_cities
    for j in 1:num_cities
        if i != j
            distances[i, j] = sqrt((x_coords[i] - x_coords[j])^2 + (y_coords[i] - y_coords[j])^2)
        end
    end
end

# Glouton basé sur la distance
function greedy_placement(x_coords, y_coords, distances, p)
    num_cities = length(x_coords)
    selected_antenna = Int[]
    assignments = Dict{Int, Int}()

    push!(selected_antenna, 1)  # On prend une ville au hasard, ici c'est la ville 1

    while length(selected_antenna) < p
        max_distance = -1.0
        farthest_city = -1

        for i in 1:num_cities
            if i in selected_antenna
                continue
            end

            min_distance_to_antenna = minimum([distances[i, j] for j in selected_antenna])
            if min_distance_to_antenna > max_distance
                max_distance = min_distance_to_antenna
                farthest_city = i
            end
        end

        push!(selected_antenna, farthest_city)
    end

    for i in 1:num_cities
        closest_antenna = argmin([distances[i, j] for j in selected_antenna])
        assignments[i] = selected_antenna[closest_antenna]
    end



    return assignments, selected_antenna
end

# Do greedy placement
assignments, selected_antenna = greedy_placement(x_coords, y_coords, distances, p)

# Print results
println("Selected antenna: ", selected_antenna)
for (city, antenna) in assignments
    println("City $city is assigned to antenna $antenna")
end

# Plot the results
scatter(x_coords, y_coords, color = :blue, label = "Cities", legend = false)
for (city, antenna) in assignments
    plot!([x_coords[city], x_coords[antenna]], [y_coords[city], y_coords[antenna]], color = :red)
end
title!("City Assignments to Antennas (Greedy Placement)")
xlabel!("Longitude")
ylabel!("Latitude")
display(plot!())
