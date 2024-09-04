# creature.py

import numpy as np
import logging
from .utils import generate_id
from .config import DEFAULT_MAX_AGE

class Gene:
    def __init__(self, gene_value=None):
        if gene_value is None:
            self.source_type = np.random.choice([0, 1])
            self.source_num = np.random.randint(0, 128)  # 7 bits
            self.sink_type = np.random.choice([0, 1])
            self.sink_num = np.random.randint(0, 128)  # 7 bits
            self.weight = np.random.randint(-32768, 32767)  # 16-bit signed integer
            self.gene_value = self.encode_gene()
        else:
            self.gene_value = gene_value
            self.decode_gene()

    def encode_gene(self):
        gene = 0
        gene |= (self.source_type & 0x1) << 31
        gene |= (self.source_num & 0x7F) << 24
        gene |= (self.sink_type & 0x1) << 23
        gene |= (self.sink_num & 0x7F) << 16
        gene |= (self.weight & 0xFFFF)
        return gene

    def decode_gene(self):
        self.source_type = (self.gene_value >> 31) & 0x1
        self.source_num = (self.gene_value >> 24) & 0x7F
        self.sink_type = (self.gene_value >> 23) & 0x1
        self.sink_num = (self.gene_value >> 16) & 0x7F
        self.weight = self.gene_value & 0xFFFF
        if self.weight >= 32768:  # Convert to signed 16-bit integer
            self.weight -= 65536

    def weight_as_float(self):
        return np.power(self.weight / 8000.0, 3) / 64.0

    @staticmethod
    def make_random_weight():
        return np.random.randint(-32768, 32767)

class NeuralNet:
    def __init__(self):
        self.connections = []
        self.neurons = []

    class Neuron:
        def __init__(self):
            self.output = 0.5  # Initial neuron output
            self.driven = False

    def add_connection(self, gene):
        self.connections.append(gene)

    def add_neuron(self):
        self.neurons.append(self.Neuron())

class Creature:
    MAX_AGE = DEFAULT_MAX_AGE
    MAX_ENERGY = 1000  # Adjust this value as needed

    SENSORY_NEURONS = [
        'LOC_X', 'LOC_Y', 'BOUNDARY_DIST_X', 'BOUNDARY_DIST', 'BOUNDARY_DIST_Y',
        'GENETIC_SIM_FWD', 'LAST_MOVE_DIR_X', 'LAST_MOVE_DIR_Y', 'LONGPROBE_POP_FWD',
        'LONGPROBE_BAR_FWD', 'POPULATION', 'POPULATION_FWD', 'POPULATION_LR',
        'OSC1', 'AGE', 'BARRIER_FWD', 'BARRIER_LR', 'RANDOM', 'SIGNAL0',
        'SIGNAL0_FWD', 'SIGNAL0_LR'
    ]
    ACTION_NEURONS = [
        'MOVE_X', 'MOVE_Y', 'MOVE_FORWARD', 'MOVE_RL', 'MOVE_RANDOM',
        'SET_OSCILLATOR_PERIOD', 'SET_LONGPROBE_DIST', 'SET_RESPONSIVENESS',
        'EMIT_SIGNAL0', 'MOVE_EAST', 'MOVE_WEST', 'MOVE_NORTH', 'MOVE_SOUTH',
        'MOVE_LEFT', 'MOVE_RIGHT', 'MOVE_REVERSE'
    ]

    def __init__(self, x, y, generation, num_genes):
        self.id = generate_id()
        self.x = int(x)
        self.y = int(y)
        self.energy = float(min(200, self.MAX_ENERGY))
        self.age = 0
        self.generation = generation
        self.num_genes = num_genes
        self.genome = [Gene() for _ in range(num_genes)]
        self.brain = self.create_brain()
        self.direction = np.random.randint(0, 8)
        self.fitness = 0.0
        logging.info(f"Birth: Creature {self.id} born at ({self.x}, {self.y}) in generation {self.generation}")
        self.last_move_x = 0
        self.last_move_y = 0
        self.long_probe_distance = 1  # Initialize with a default value
        self.oscillator_period = 1  # Initialize with a default value
        self.responsiveness = 0.5  # Initialize with a default value

    def create_brain(self):
        brain = NeuralNet()
        for gene in self.genome:
            brain.add_connection(gene)
        # Add neurons based on unique sink and source numbers
        unique_neurons = set()
        for gene in self.genome:
            if gene.source_type == 0:
                unique_neurons.add(gene.source_num)
            if gene.sink_type == 0:
                unique_neurons.add(gene.sink_num)
        for _ in range(len(unique_neurons)):
            brain.add_neuron()
        return brain

    def mutate(self, mutation_rate):
        for gene in self.genome:
            if np.random.random() < mutation_rate:
                gene.weight = Gene.make_random_weight()

    def crossover(self, other):
        new_genome = []
        for gene1, gene2 in zip(self.genome, other.genome):
            new_gene = Gene()
            if np.random.random() < 0.5:
                new_gene.source_type = gene1.source_type
                new_gene.source_num = gene1.source_num
                new_gene.sink_type = gene1.sink_type
                new_gene.sink_num = gene1.sink_num
                new_gene.weight = gene1.weight
            else:
                new_gene.source_type = gene2.source_type
                new_gene.source_num = gene2.source_num
                new_gene.sink_type = gene2.sink_type
                new_gene.sink_num = gene2.sink_num
                new_gene.weight = gene2.weight
            new_genome.append(new_gene)
        return new_genome

    def predict(self, inputs):
        if len(inputs) != len(self.SENSORY_NEURONS):
            raise ValueError(f"Expected {len(self.SENSORY_NEURONS)} inputs, got {len(inputs)}")
        
        # Reset neuron outputs
        for neuron in self.brain.neurons:
            neuron.output = 0.5
            neuron.driven = False

        # Process each connection
        for gene in self.brain.connections:
            if gene.source_type == 1:
                if gene.source_num >= len(inputs):
                    continue  # Skip this connection if the source_num is out of range
                source_value = inputs[gene.source_num]
            else:
                if gene.source_num >= len(self.brain.neurons):
                    continue  # Skip this connection if the source_num is out of range
                source_value = self.brain.neurons[gene.source_num].output
            
            weight = gene.weight_as_float()
            if gene.sink_type == 0:
                if gene.sink_num < len(self.brain.neurons):
                    self.brain.neurons[gene.sink_num].output += source_value * weight
                    self.brain.neurons[gene.sink_num].driven = True
            else:  # ACTION
                # Here you would update the action neurons directly
                pass

        # Apply activation function to driven neurons
        for neuron in self.brain.neurons:
            if neuron.driven:
                neuron.output = np.tanh(neuron.output)

        # Collect action neuron outputs
        action_outputs = [0.0] * len(self.ACTION_NEURONS)
        for gene in self.brain.connections:
            if gene.sink_type == 1 and gene.sink_num < len(action_outputs):
                if gene.source_type == 1 and gene.source_num < len(inputs):
                    source_value = inputs[gene.source_num]
                elif gene.source_type == 0 and gene.source_num < len(self.brain.neurons):
                    source_value = self.brain.neurons[gene.source_num].output
                else:
                    continue
                action_outputs[gene.sink_num] += source_value * gene.weight_as_float()

        # Apply activation function to action outputs
        action_outputs = np.tanh(action_outputs)

        # Update creature attributes based on action outputs
        self.long_probe_distance = int(np.clip(action_outputs[self.ACTION_NEURONS.index('SET_LONGPROBE_DIST')] * 10, 1, 10))
        self.oscillator_period = int(np.clip(action_outputs[self.ACTION_NEURONS.index('SET_OSCILLATOR_PERIOD')] * 10, 1, 10))
        self.responsiveness = np.clip(action_outputs[self.ACTION_NEURONS.index('SET_RESPONSIVENESS')], 0, 1)

        return action_outputs

    def get_average_reproduction_chance(self):
        return np.mean([gene.weight_as_float() for gene in self.genome[:len(self.genome)//2]]) * 0.5 + 0.5

    def get_average_energy_efficiency(self):
        return np.mean([gene.weight_as_float() for gene in self.genome[len(self.genome)//2:]]) * 0.5 + 0.5

    def update_direction(self, rotate):
        self.direction = (self.direction + rotate) % 8
