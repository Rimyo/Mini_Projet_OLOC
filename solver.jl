using CPLEX
using JuMP
using LinearAlgebra
using Plots
using DataFrames

# File path
file_path = "inst_300000.flp"
p = 2
# Read the data from the file
num_cities = 0
ids = Int[]
code_postal = Int[]
x_coords = Float64[]
y_coords = Float64[]
f= Float64[]

function Lit_fichier_UFLP(nom_fichier, tabX, tabY, f)

    n=0
    println("Lecture du fichier: ", nom_fichier)
    open(nom_fichier) do fic

        for (i,line) in enumerate(eachline(fic)) 
                lg = split(line," ")      # découpe la ligne suivant les espaces et crée un tableau 
                if (i<=1) 
                    n= parse(Int,lg[1])
                end
                if (i>=2) && (i<=n+1) 
                    push!(tabX,parse(Float64,lg[3]))
                    push!(tabY,parse(Float64,lg[4]))	
                    push!(f,parse(Float64,lg[5]))               
                end              
        end    
    end
    return n
end

num_cities= Lit_fichier_UFLP(file_path, x_coords, y_coords, f)

println("Le fichier contient ",num_cities, " villes")

# Print a sample of the data
println("Sample data:")
for i in 1:5
    println("City $i: x=$(x_coords[i]), y=$(y_coords[i])")
end

# Compute the distance matrix
distances = zeros(Float64, num_cities, num_cities)
for i in 1:num_cities
    for j in 1:num_cities
        if i != j
            distances[i, j] = sqrt((x_coords[i] - x_coords[j])^2 + (y_coords[i] - y_coords[j])^2)
        end
    end
end

function exact_resolution(model)
# Define the optimization model
	model = Model(CPLEX.Optimizer)

	# Decision variables
	@variable(model, x[1:num_cities, 1:num_cities], Bin)
	@variable(model, z >= 0)

	# Objective function
	@objective(model, Min, z)

	# Constraints
	@constraint(model, sum(x[i, i] for i in 1:num_cities) <= p)
	for i in 1:num_cities
	    @constraint(model, sum(x[i, j] for j in 1:num_cities) == 1)
	end
	for i in 1:num_cities, j in 1:num_cities
	    if i != j
		@constraint(model, x[i, j] <= x[j, j])
	    end
	end
	for i in 1:num_cities
	    @constraint(model, sum(distances[i, j] * x[i, j] for j in 1:num_cities) <= z)
	end

	return model
end



# Solve the model
model = exact_resolution(model)
#optimize!(model)

# Extract results
optimal_z = objective_value(model)
println("Optimal value of z: ", optimal_z)
println("yooooo")

# Plot the results
scatter(x_coords, y_coords, color = :blue, label = "Cities", legend = false)
for i in 1:num_cities
    for j in 1:num_cities
        if value(x[i, j]) == 1
            plot!([x_coords[i], x_coords[j]], [y_coords[i], y_coords[j]], color = :red)
        end
    end
end
title!("City Assignments to Antennas")
xlabel!("Longitude")
ylabel!("Latitude")
display(plot!())

