# world.py

import numpy as np
import logging
from .creature import Creature, Gene
from .utils import handle_index_error, logging_decorator
from PIL import Image
import io
import base64
from .config import (
    WORLD_WIDTH, WORLD_HEIGHT, INITIAL_POPULATION,
    DEFAULT_MIN_REPRODUCTION_ENERGY, DEFAULT_MAX_AGE,
    DEFAULT_ENERGY_GAIN_FROM_KILLING, DEFAULT_REPRODUCTION_ENERGY_COST,
    DEFAULT_MOVE_ENERGY_COST, DEFAULT_IDLE_ENERGY_COST,
    DEFAULT_PHEROMONE_ENERGY_COST, DEFAULT_LONG_PROBE_ENERGY_COST,
    MUTATION_RATE, NUM_SENSORY_NEURONS, NUM_INTERNAL_NEURONS,
    NUM_ACTION_NEURONS, DEFAULT_NUM_GENES
)
from .creature import Gene

class World:
    def __init__(self, width, height, initial_population, params):
        self.width = max(1, width)
        self.height = max(1, height)
        self.params = {
            'max_age': params.get('max_age', DEFAULT_MAX_AGE),
            'min_reproduction_energy': params.get('min_reproduction_energy', DEFAULT_MIN_REPRODUCTION_ENERGY),
            'energy_gain_from_killing': params.get('energy_gain_from_killing', DEFAULT_ENERGY_GAIN_FROM_KILLING),
            'reproduction_energy_cost': params.get('reproduction_energy_cost', DEFAULT_REPRODUCTION_ENERGY_COST),
            'move_energy_cost': params.get('move_energy_cost', DEFAULT_MOVE_ENERGY_COST),
            'idle_energy_cost': params.get('idle_energy_cost', DEFAULT_IDLE_ENERGY_COST),
            'pheromone_energy_cost': params.get('pheromone_energy_cost', DEFAULT_PHEROMONE_ENERGY_COST),
            'long_probe_energy_cost': params.get('long_probe_energy_cost', DEFAULT_LONG_PROBE_ENERGY_COST),
            'num_genes': int(params.get('num_genes', DEFAULT_NUM_GENES)),
        }
        self.creatures = []
        self.pheromones = np.zeros((width, height))
        self.food = np.zeros((width, height))
        self.step_count = 0
        self.generation = 0
        self.logger = logging.getLogger(__name__)
        self.initialize_population(initial_population)

    def initialize_population(self, initial_population):
        for _ in range(initial_population):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            creature = Creature(x, y, 0, self.params['num_genes'])
            self.creatures.append(creature)
        self.respawn_food()  # Ensure food is generated at the start

    @logging_decorator
    def update_creatures(self):
        if not self.creatures:
            self.logger.warning("No creatures to update")
            return

        try:
            for creature in self.creatures:
                inputs = self.get_creature_inputs(creature)
                outputs = creature.predict(inputs)
                self.process_creature_actions(creature, outputs)

            # Remove creatures with no energy
            self.creatures = [c for c in self.creatures if c.energy > 0]

        except Exception as e:
            self.logger.error(f"Error in update_creatures: {str(e)}", exc_info=True)
            raise

    def get_creature_inputs(self, creature):
        inputs = [
            creature.x / self.width,  # LOC_X
            creature.y / self.height,  # LOC_Y
            self.get_border_distance_x(creature),  # BOUNDARY_DIST_X
            self.get_nearest_border_distance(creature),  # BOUNDARY_DIST
            self.get_border_distance_y(creature),  # BOUNDARY_DIST_Y
            self.get_genetic_similarity_fd(creature),  # GENETIC_SIM_FWD
            creature.last_move_x,  # LAST_MOVE_DIR_X
            creature.last_move_y,  # LAST_MOVE_DIR_Y
            self.get_long_range_population_fd(creature),  # LONGPROBE_POP_FWD
            self.get_long_range_blockage_fd(creature),  # LONGPROBE_BAR_FWD
            self.get_population_density(creature),  # POPULATION
            self.get_population_gradient_fd(creature),  # POPULATION_FWD
            self.get_population_gradient_lr(creature),  # POPULATION_LR
            self.get_oscillator_value(creature),  # OSC1
            creature.age / Creature.MAX_AGE,  # AGE
            self.is_blocked_fd(creature),  # BARRIER_FWD
            self.is_blocked_lr(creature),  # BARRIER_LR
            np.random.random(),  # RANDOM
            self.get_pheromone_density(creature),  # SIGNAL0
            self.get_pheromone_gradient_fd(creature),  # SIGNAL0_FWD
            self.get_pheromone_gradient_lr(creature),  # SIGNAL0_LR
        ]
        assert len(inputs) == 21, f"Expected 21 inputs, got {len(inputs)}"
        return inputs

    def process_creature_actions(self, creature, outputs):
        try:
            # SET_LONGPROBE_DIST
            creature.long_probe_distance = int(np.clip(outputs[Creature.ACTION_NEURONS.index('SET_LONGPROBE_DIST')] * 5, 1, 5))

            # SET_OSCILLATOR_PERIOD
            creature.oscillator_period = int(np.clip(outputs[Creature.ACTION_NEURONS.index('SET_OSCILLATOR_PERIOD')] * 10, 1, 10))
            
            # Check for reproduction
            if outputs[Creature.ACTION_NEURONS.index('SET_OSCILLATOR_PERIOD')] > 0.5:
                self.attempt_reproduction(creature)

            # EMIT_SIGNAL0
            if outputs[Creature.ACTION_NEURONS.index('EMIT_SIGNAL0')] > 0.5:
                self.pheromones[creature.x, creature.y] = 1.0
                creature.energy -= self.params['pheromone_energy_cost']
                self.log_event("Pheromone", f"Creature {creature.id} spawned pheromone at ({creature.x}, {creature.y})")

            # Movement
            move_x = outputs[Creature.ACTION_NEURONS.index('MOVE_X')]
            move_y = outputs[Creature.ACTION_NEURONS.index('MOVE_Y')]
            move_forward = outputs[Creature.ACTION_NEURONS.index('MOVE_FORWARD')] > 0.5
            move_rl = outputs[Creature.ACTION_NEURONS.index('MOVE_RL')]
            move_random = outputs[Creature.ACTION_NEURONS.index('MOVE_RANDOM')] > 0.5

            old_x, old_y = creature.x, creature.y

            if move_forward:
                creature.x, creature.y = self.get_forward_position(creature)
            elif move_random:
                creature.x, creature.y = self.get_random_neighbor(creature)
            else:
                dx = int(np.clip(move_x * 3, -1, 1))
                dy = int(np.clip(move_y * 3, -1, 1))
                creature.x = (creature.x + dx) % self.width
                creature.y = (creature.y + dy) % self.height

            if move_rl != 0:
                creature.direction = (creature.direction + (1 if move_rl > 0 else -1)) % 8

            if (creature.x, creature.y) != (old_x, old_y):
                creature.energy -= self.params['move_energy_cost']
                self.log_event("Move", f"Creature {creature.id} moved from ({old_x}, {old_y}) to ({creature.x}, {creature.y})")
            else:
                creature.energy -= self.params['idle_energy_cost']

            creature.last_move_x = creature.x - old_x
            creature.last_move_y = creature.y - old_y

            # SET_RESPONSIVENESS
            creature.responsiveness = np.clip(outputs[Creature.ACTION_NEURONS.index('SET_RESPONSIVENESS')], 0, 1)

            # Aging and energy cap
            creature.age += 1
            creature.energy = min(creature.energy, Creature.MAX_ENERGY)

        except Exception as e:
            self.logger.error(f"Error processing creature {creature.id}: {str(e)}", exc_info=True)
            raise

    def attempt_reproduction(self, creature):
        for partner in self.creatures:
            if partner != creature and self.distance(creature, partner) <= 10:
                if partner.oscillator_period > 0.5:
                    child = self.create_child(creature, partner)
                    if child:
                        self.creatures.append(child)
                        creature.energy -= self.params['reproduction_energy_cost']
                        partner.energy -= self.params['reproduction_energy_cost']
                        self.log_event("Reproduction", f"Creature {creature.id} and {partner.id} reproduced, creating creature {child.id}")
                    break

    def distance(self, creature1, creature2):
        return np.sqrt((creature1.x - creature2.x) ** 2 + (creature1.y - creature2.y) ** 2)

    def update(self):
        try:
            self.perform_step()
            self.step_count += 1
            
            if self.step_count % self.params.get('steps_per_generation', 100) == 0:
                self.end_generation()
        except Exception as e:
            self.logger.error(f"Error updating world: {str(e)}", exc_info=True)
            raise

    def update_pheromones(self):
        self.pheromones *= 0.99

    def perform_step(self):
        self.step_count += 1
        if self.step_count % 50 == 0:
            self.generation += 1
            self.logger.info(f"New generation marker: {self.generation}")

        self.update_creatures()
        self.update_pheromones()
        self.update_food()

        self.logger.debug(f"Step {self.step_count} completed. Population: {len(self.creatures)}")

    def end_generation(self):
        self.generation += 1
        self.logger.info(f"Generation {self.generation} completed")
        
        self.evaluate_creatures()
        self.reproduce()
        self.remove_unfit_creatures()

    def evaluate_creatures(self):
        for creature in self.creatures:
            creature.fitness = creature.energy  # Simple fitness function based on energy

    def remove_unfit_creatures(self):
        self.creatures.sort(key=lambda c: c.fitness, reverse=True)
        self.creatures = self.creatures[:len(self.creatures)//2]  # Keep top 50%

    def reproduce(self):
        new_creatures = []
        for creature in self.creatures:
            reproduction_chance = creature.get_average_reproduction_chance()
            if (creature.energy > self.params['min_reproduction_energy'] and
                np.random.random() < reproduction_chance):
                partner = self.find_partner(creature)
                if partner:
                    child = self.create_child(creature, partner)
                    new_creatures.append(child)
                    creature.energy -= self.params['reproduction_energy_cost']
                    partner.energy -= self.params['reproduction_energy_cost']
                    self.log_event("Reproduction", f"Creature {creature.id} and {partner.id} reproduced, creating creature {child.id}")
        self.creatures.extend(new_creatures)

    def find_partner(self, creature):
        potential_partners = [c for c in self.creatures if c != creature and
                              abs(c.x - creature.x) <= 1 and abs(c.y - creature.y) <= 1 and
                              c.energy > 30 and c.age < 100]
        return np.random.choice(potential_partners) if potential_partners else None

    def create_child(self, parent1, parent2):
        try:
            child_x, child_y = (parent1.x + parent2.x) // 2, (parent1.y + parent2.y) // 2
            child = Creature(child_x, child_y, max(parent1.generation, parent2.generation) + 1, num_genes=self.params['num_genes'])
            
            # Crossover
            child.genome = parent1.crossover(parent2)
            
            # Mutation
            mutation_rate = MUTATION_RATE / (1 + 0.01 * self.generation)            
            child.mutate(mutation_rate)
            
            child.brain = child.create_brain()
            return child
        except Exception as e:
            self.logger.error(f"Error creating child: {str(e)}", exc_info=True)
            raise

    def update_food(self):
        if self.step_count % 1 == 0:
            self.respawn_food()

    def respawn_food(self):
        if np.random.random() < 0.7:
            x, y = np.random.randint(0, self.width), np.random.randint(0, self.height)
            self.food[x, y] = np.random.uniform(75, 150)
            logging.info(f"New food spawned at ({x}, {y}) with energy {self.food[x, y]:.2f}")

    # Helper methods for get_creature_inputs
    def get_pheromone_gradient_lr(self, creature):
        left = self.pheromones[max(0, creature.x - 1), creature.y]
        right = self.pheromones[min(self.width - 1, creature.x + 1), creature.y]
        return (right - left + 1) / 2  # Normalize to 0-1 range

    def get_pheromone_gradient_fd(self, creature):
        back = self.pheromones[creature.x, creature.y]
        forward = self.pheromones[creature.x, min(self.height - 1, creature.y + 1)]
        return (forward - back + 1) / 2  # Normalize to 0-1 range

    def get_pheromone_density(self, creature):
        neighborhood = self.pheromones[max(0, creature.x-1):min(self.width, creature.x+2),
                                       max(0, creature.y-1):min(self.height, creature.y+2)]
        return np.mean(neighborhood)

    def is_blocked_lr(self, creature):
        left_blocked = creature.x == 0 or any(c.x == creature.x - 1 and c.y == creature.y for c in self.creatures)
        right_blocked = creature.x == self.width - 1 or any(c.x == creature.x + 1 and c.y == creature.y for c in self.creatures)
        return (left_blocked + right_blocked) / 2  # Average of left and right blockage

    def is_blocked_fd(self, creature):
        forward_pos = self.get_forward_position(creature)
        return 1.0 if self.get_creature_at(forward_pos) else 0.0

    def get_oscillator_value(self, creature):
        return np.sin(2 * np.pi * self.step_count / creature.oscillator_period)

    def get_population_gradient_lr(self, creature):
        left_count = sum(1 for c in self.creatures if c.x == creature.x - 1 and abs(c.y - creature.y) <= 1)
        right_count = sum(1 for c in self.creatures if c.x == creature.x + 1 and abs(c.y - creature.y) <= 1)
        return (right_count - left_count + 3) / 6  # Normalize to 0-1 range

    def get_population_density(self, creature):
        neighborhood = [(x, y) for x in range(creature.x-1, creature.x+2) for y in range(creature.y-1, creature.y+2)]
        count = sum(1 for c in self.creatures if (c.x, c.y) in neighborhood)
        return count / 9  # Normalize by the size of the neighborhood

    def get_population_gradient_fd(self, creature):
        forward_pos = self.get_forward_position(creature)
        backward_pos = self.get_reverse_position(creature)
        forward_count = sum(1 for c in self.creatures if (c.x, c.y) == forward_pos)
        backward_count = sum(1 for c in self.creatures if (c.x, c.y) == backward_pos)
        return (forward_count - backward_count + 1) / 2  # Normalize to 0-1 range

    def get_long_range_population_fd(self, creature):
        forward_pos = self.get_forward_position(creature)
        count = 0
        for i in range(1, creature.long_probe_distance + 1):
            x = (forward_pos[0] + i * (forward_pos[0] - creature.x)) % self.width
            y = (forward_pos[1] + i * (forward_pos[1] - creature.y)) % self.height
            count += sum(1 for c in self.creatures if c.x == x and c.y == y)
        return count / (creature.long_probe_distance * 5)  # Normalize

    def get_long_range_blockage_fd(self, creature):
        forward_pos = self.get_forward_position(creature)
        for i in range(1, creature.long_probe_distance + 1):
            x = (forward_pos[0] + i * (forward_pos[0] - creature.x)) % self.width
            y = (forward_pos[1] + i * (forward_pos[1] - creature.y)) % self.height
            if any(c.x == x and c.y == y for c in self.creatures):
                return i / creature.long_probe_distance
        return 1.0

    def get_border_distance_x(self, creature):
        return min(creature.x, self.width - 1 - creature.x) / (self.width / 2)

    def get_border_distance_y(self, creature):
        return min(creature.y, self.height - 1 - creature.y) / (self.height / 2)

    def get_nearest_border_distance(self, creature):
        return min(self.get_border_distance_x(creature), self.get_border_distance_y(creature))

    def get_genetic_similarity_fd(self, creature):
        forward_pos = self.get_forward_position(creature)
        forward_creature = self.get_creature_at(forward_pos)
        if forward_creature:
            return self.calculate_genetic_similarity(creature, forward_creature)
        return 0.0

    def calculate_genetic_similarity(self, creature1, creature2):
        similar_genes = sum(1 for g1, g2 in zip(creature1.genome, creature2.genome)
                            if g1.source_type == g2.source_type and g1.source_num == g2.source_num
                            and g1.sink_type == g2.sink_type and g1.sink_num == g2.sink_num)
        return similar_genes / len(creature1.genome)

    def get_world_state(self):
        state = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Set food (green)
        state[:, :, 1] = np.minimum(self.food, 255).astype(np.uint8)
        
        # Set pheromones (blue)
        state[:, :, 2] = np.minimum(self.pheromones * 255, 255).astype(np.uint8)
        
        # Set creatures (red)
        for creature in self.creatures:
            state[creature.y, creature.x, 0] = 255
        
        return state.tolist()

    def simulation_data(self):
        stats = {
            'step_count': self.step_count,
            'population': len(self.creatures),
            'generation': self.generation,
            'total_pheromone': np.sum(self.pheromones),
            'pheromone_locations': np.count_nonzero(self.pheromones),
            'total_food': np.sum(self.food),
            'food_locations': np.count_nonzero(self.food),
            'avg_creature_age': np.mean([c.age for c in self.creatures]) if self.creatures else 0,
            'oldest_creature_age': max([c.age for c in self.creatures]) if self.creatures else 0
        }
        
        return {
            'stats': stats,
            'world_state': self.get_world_state(),
            'median_genome': self.get_median_genome(),
            'isSimulationOver': self.is_simulation_over()
        }

    def is_simulation_over(self):
        return len(self.creatures) == 0

    def log_event(self, event_type, details):
        logging.info(f"{event_type}: {details}")

    def get_reverse_position(self, creature):
        dx, dy = self.get_direction_vector(creature.direction)
        new_x = (creature.x - dx) % self.width
        new_y = (creature.y - dy) % self.height
        return new_x, new_y

    def get_direction_vector(self, direction):
        directions = [
            (0, 1),   # North
            (1, 1),   # Northeast
            (1, 0),   # East
            (1, -1),  # Southeast
            (0, -1),  # South
            (-1, -1), # Southwest
            (-1, 0),  # West
            (-1, 1)   # Northwest
        ]
        return directions[direction]

    def get_forward_position(self, creature):
        dx, dy = self.get_direction_vector(creature.direction)
        new_x = (creature.x + dx) % self.width
        new_y = (creature.y + dy) % self.height
        return new_x, new_y

    def get_random_neighbor(self, creature):
        dx = np.random.randint(-1, 2)
        dy = np.random.randint(-1, 2)
        new_x = (creature.x + dx) % self.width
        new_y = (creature.y + dy) % self.height
        return new_x, new_y

    def get_creature_at(self, position):
        x, y = position
        for creature in self.creatures:
            if creature.x == x and creature.y == y:
                return creature
        return None
    
    def get_median_genome(self):
        if not self.creatures:
            return []
        all_genomes = [c.genome for c in self.creatures]
        median_genome = []
        for gene_index in range(len(all_genomes[0])):
            median_gene = Gene()
            median_gene.source_type = int(np.median([genome[gene_index].source_type for genome in all_genomes]))
            median_gene.source_num = int(np.median([genome[gene_index].source_num for genome in all_genomes]))
            median_gene.sink_type = int(np.median([genome[gene_index].sink_type for genome in all_genomes]))
            median_gene.sink_num = int(np.median([genome[gene_index].sink_num for genome in all_genomes]))
            median_gene.weight = int(np.median([genome[gene_index].weight for genome in all_genomes]))
            median_genome.append(median_gene)
        return [gene.__dict__ for gene in median_genome]


