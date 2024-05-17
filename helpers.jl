using Random

function generate_random_binary_vector(n)
    # Créer un vecteur de taille n avec des 0 et 1 au hasard
    return rand(Bool, n) .|> Int
end

# Exemple d'utilisation pour un vecteur de taille 10
n = 10
random_vector = generate_random_binary_vector(n)
println(random_vector)
