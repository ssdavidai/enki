# simulation.py

from .world import World
from .config import WORLD_WIDTH, WORLD_HEIGHT, INITIAL_POPULATION, DEFAULT_MIN_REPRODUCTION_ENERGY, DEFAULT_MAX_AGE, DEFAULT_ENERGY_GAIN_FROM_KILLING, DEFAULT_REPRODUCTION_ENERGY_COST, DEFAULT_MOVE_ENERGY_COST, DEFAULT_IDLE_ENERGY_COST, DEFAULT_PHEROMONE_ENERGY_COST, DEFAULT_LONG_PROBE_ENERGY_COST, DEFAULT_NUM_GENES
from .utils import logging_decorator

class Simulation:
    def __init__(self):
        self.world = None
        self.params = {}

    def start_simulation(self, params):
        self.params = params
        width = params.get('width', WORLD_WIDTH)
        height = params.get('height', WORLD_HEIGHT)
        initial_population = params.get('initial_population', INITIAL_POPULATION)
        self.world = World(width, height, initial_population, params)

    def run_step(self):
        if self.world is None:
            raise ValueError("Simulation not started. Call start_simulation first.")
        self.world.update()

    def get_simulation_data(self):
        if self.world is None:
            raise ValueError("Simulation not started. Call start_simulation first.")
        return self.world.simulation_data()

simulation = Simulation()
