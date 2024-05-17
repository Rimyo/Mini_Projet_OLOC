using Random

function generate_random_binary_vector(n, p)
    # Create a vector of size n with at most p ones
    vec = vcat(ones(Int, min(n, p)), zeros(Int, max(0, n - p)))
    return shuffle(vec)
end

# Exemple d'utilisation pour un vecteur de taille 10
n = 10
random_vector = generate_random_binary_vector(n)
println(random_vector)
