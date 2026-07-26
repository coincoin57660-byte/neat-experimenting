#  NEAT -> NeuroEvolution of Augmenting Topologies

# remplacer Neurones par nodes

import random, math
from collections import defaultdict, deque




def random_weight() -> float:
    value = random.uniform(-1, 1)
    return value


def ReLU(value: float) -> float:
    return max(0.0, value)






class Model:
    def __init__(self, population_size: int) -> None:

        self.population_size = population_size
        self.population = [
            Genome(
                parent = None
            )
            for _ in range(population_size)
        ]
        self.génération = 0


    def evaluate_population(self, steps: int, pendulum: object, débug: bool = False) -> None:

        for genome in self.population:

            save_log = False

            if self.génération == 100:

                save_log = True

            genome.reset_value()
            pendulum.reset(
                log = save_log
            )
            fitness = 0

            for t in range(steps):

                state = pendulum.get_state()
                action = genome.forward(input_values = state)

                state, reward, done = pendulum.step(
                    action = action,
                    t = t
                )
                fitness += reward

                if done:
                    break

                if débug and t == steps - 1:
                    print(f'\nforce = {action[0]:.2f}')
                    print(f't = {t * pendulum.dt:.2f}s,  theta = {state[2]:.2f},  x = {state[0]:.2f}')
                    print(f'fitness = {fitness:.2f}')

            genome.max_angle = pendulum.max_angle_inv_pour
            genome.moyen_angle = pendulum.total_angle_inv_pour / steps

            genome.fitness = fitness

            # limitation de la complexité
            genome.fitness -= 0.01 * genome.nbr_Connections + 0.02 * genome.nbr_Neurones

            genome.fitness = max(
                0.0,
                genome.fitness
            )

            if save_log:
                pendulum.save_logs()
                raise Exception('Only 1 log')


    def sort_population(self, ordre_croissant: bool = False) -> None:

        ordre_croissant = not ordre_croissant
        self.population.sort(key = lambda g: g.fitness, reverse = ordre_croissant)


    def selection_population(self, débug: bool = False) -> None:

        nbr_survivors = int(self.population_size * 0.3)

        if débug:
            print(f'\nnbr survivors : {nbr_survivors}')

        self.survivors = self.population[:nbr_survivors]


    def reproduction_population(self, débug: bool = False) -> None:

        if débug:
            print()

        new_population = self.survivors.copy()

        if débug:
            print(f'len new population : {len(new_population)}')

        while len(new_population) < self.population_size:

            parent = random.choice(self.survivors)

            child = Genome(
                parent = parent
            )
            child.mutate()

            new_population.append(child)

            if débug:
                print(f'len new population : {len(new_population)}')

        self.population = new_population






class Genome:
    def __init__(self, parent: object = None) -> None:

        if parent is None:
            self.init_base()

        else:
            self.init_copy(
                parent = parent
            )

        self.max_angle = None
        self.moyen_angle = None



    def init_base(self) -> None:

        self.Neurones = {
            0: Neurone(id = 0, type = 'input'),
            1: Neurone(id = 1, type = 'input'),
            2: Neurone(id = 2, type = 'input'),
            3: Neurone(id = 3, type = 'input'),
            4: Neurone(id = 4, type = 'output')
        }

        self.connections = [
            Connection(from_id = 0, to_id = 4, weight = random_weight(), enabled = True, innovation = 1),
            Connection(from_id = 1, to_id = 4, weight = random_weight(), enabled = True, innovation = 2),
            Connection(from_id = 2, to_id = 4, weight = random_weight(), enabled = True, innovation = 3),
            Connection(from_id = 3, to_id = 4, weight = random_weight(), enabled = True, innovation = 4)
        ]

        self.nbr_Neurones = 5
        self.nbr_Connections = 4



    def init_copy(self, parent: object) -> None:

        self.Neurones = {
            nid: Neurone(
                id = neurone.id,
                type = neurone.type
            )
            for nid, neurone in parent.Neurones.items()
        }

        self.connections = [
            Connection(
                from_id = connection.from_id,
                to_id = connection.to_id,
                weight = connection.weight,
                enabled = connection.enabled,
                innovation = connection.innovation
            )
            for connection in parent.connections
        ]

        self.nbr_Neurones = parent.nbr_Neurones
        self.nbr_Connections = parent.nbr_Connections


    def reset_value(self) -> None:

        for index in range(self.nbr_Neurones):

            self.Neurones[index].value = None




    def forward(self, input_values: list) -> list:

        # Assigner valeurs aux Neuronees d'entrée
        for index, val in enumerate(input_values):

            self.Neurones[index].value = val

        # Calculer les autres Neuronees dans l'ordre topologique
        order = topological_sort(self.Neurones, self.connections)

        for nid in order:

            Neurone = self.Neurones[nid]

            if Neurone.type == 'input':
                continue # Valeur déja assignée

            # Somme pondérée de toutes les connexions actives
            incoming = [
                connection
                for connection in self.connections
                if connection.to_id == nid and connection.enabled
            ]
            Neurone.value = sum(
                self.Neurones[connection.from_id].value * connection.weight
                for connection in incoming
            )
            Neurone.value = self.activation(
                value = Neurone.value
            )

        # Retourne les outputs
        return [
            self.Neurones[nid].value
            for nid in self.Neurones
            if self.Neurones[nid].type == 'output'
        ]



    def activation(self, value: float) -> float:

        # new_value = ReLU(value)
        new_value = math.tanh(value)
        return new_value



    def mutate(self) -> None:

        proba = random.random()

        proba_weight = 0.80
        proba_new_neurone = 0.05
        proba_new_connection = 0.10
        proba_act_connection = 0.05


        # mutation poids
        if proba <= proba_weight:

            self.weight_mutation()


        # nouveau Neuronee
        elif proba <= proba_weight + proba_new_neurone:

            self.add_neurone()


        # nouvelle connexion
        elif proba <= proba_weight + proba_new_neurone + proba_new_connection:

            self.add_connection()


        # réactiver une connection
        elif proba <= proba_weight + proba_new_neurone + proba_new_connection + proba_act_connection:

            self.reactivate_connection()





    def weight_mutation(self):

        variation = 0.05
        proba_plus = 0.1
        proba_encore = 0.25

        connection = random.choice(self.connections)

        if random.random() < 1 - proba_plus:
            connection.weight += random.uniform(-variation, variation)
        else:
            connection.weight += random.uniform(-variation * 2, variation * 2)

        # 25 % de chance de modifier un deuxième, troisième etc.. poids
        while random.random() > 1 - proba_encore:
            connection = random.choice(self.connections)

            if random.random() < 1 - proba_plus:
                connection.weight += random.uniform(-variation, variation)
            else:
                connection.weight += random.uniform(variation * 2, variation * 2)



    def add_neurone(self) -> None:

        connection = random.choice(self.connections)

        if connection.enabled:

            connection.enabled = False
            new_id = self.nbr_Neurones

            self.Neurones[new_id] = Neurone(
                id = new_id,
                type = "hidden"
            )
            self.nbr_Neurones += 1

            self.connections.append(
                Connection(
                    from_id = connection.from_id,
                    to_id = new_id,
                    weight = 1.0,
                    enabled = True,
                    innovation = 0
                )
            )

            self.connections.append(
                Connection(
                    from_id = new_id,
                    to_id = connection.to_id,
                    weight = connection.weight,
                    enabled = True,
                    innovation = 0
                )
            )


    def add_connection(self) -> None:

        for _ in range(10):

            from_id = random.choice(list(self.Neurones.keys()))
            to_id = random.choice(list(self.Neurones.keys()))

            if from_id == to_id:
                continue

            if self.Neurones[to_id].type == 'input':
                continue

            for connection in self.connections:
                if connection.from_id == from_id and connection.to_id == to_id:
                    continue

            new_connection = Connection(
                from_id = from_id,
                to_id = to_id,
                weight = random_weight(),
                enabled = True,
                innovation = 0
            )

            self.connections.append(
                new_connection
            )

            try:
                topological_sort(
                    Neurones = self.Neurones,
                    connections = self.connections
                )

                self.nbr_Connections += 1
                return

            except:
                self.connections.pop()


    def reactivate_connection(self):

        disabled = [
            connection
            for connection in self.connections
            if not connection.enabled
        ]

        if disabled:

            random.choice(disabled).enabled = True








class Neurone:
    def __init__(self, id: int, type: str) -> None:

        self.id = id
        self.type = type
        self.value = 0.0


class Connection:
    def __init__(self,
            from_id: int, to_id: int, weight: float,
            enabled: bool = True, innovation: int = 0
        ) -> None:

        self.from_id = from_id
        self.to_id = to_id
        self.weight = weight
        self.enabled = enabled
        self.innovation = innovation






def topological_sort(Neurones, connections) -> list:

    # Graph : Neuronee -> Neuronees dépendants
    graph = defaultdict(list)
    in_degree = {
        nid: 0
        for nid in Neurones
    }

    for connection in connections:

        if connection.enabled:

            graph[connection.from_id].append(connection.to_id)
            in_degree[connection.to_id] += 1

    # Tri topologique
    queue = deque(
        [
            nid
            for nid in Neurones
            if in_degree[nid] == 0
        ]
    )

    order = []

    while queue:

        nid = queue.popleft()

        order.append(nid)

        for neighbor in graph[nid]:

            in_degree[neighbor] -= 1

            if in_degree[neighbor] == 0:

                queue.append(neighbor)

    if len(order) != len(Neurones):

        raise Exception('Cycle detected !')

    return order