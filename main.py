from Simulation import simulation
import neat_main


model = neat_main.Model(
    population_size = 250
)

pendulum = simulation.Pendulum(
    dt = 0.016,
    g = 9.81,
    m = 1.0,  # masse pendule
    M = 5.0,  # masse chariot
    l = 2.0   # longeur pendule
)

while True:
    model.evaluate_population(
        steps = int(120 / pendulum.dt),  # sur 10 secondes de simulation
        pendulum = pendulum,
        débug = False
    )


    print(f'\n\nGénération : {model.génération}\n')
    model.sort_population(
        ordre_croissant = True
    )
    for i in range(model.population_size):
        print(
            f'fitness : {model.population[i].fitness:<22}      angle max en %: {model.population[i].max_angle:>22} %       angle moyen en %: {model.population[i].moyen_angle:>22} %       nbr neurones : {model.population[i].nbr_Neurones:<5}       nbr connections : {model.population[i].nbr_Connections:<5}'
        )


    model.sort_population(
        ordre_croissant = False
    )

    model.selection_population(
        débug = False
    )

    model.reproduction_population(
        débug = False
    )

    model.génération += 1

    # input()


"""
generation loop
-> évaluer tous les genomes
-> sélection des meilleurs
-> crossover
-> mutations
-> nouvelle génération
"""