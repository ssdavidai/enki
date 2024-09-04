# config.py

# World settings
WORLD_WIDTH = 128
WORLD_HEIGHT = 128
INITIAL_POPULATION = 1000

# Default creature settings
DEFAULT_MIN_REPRODUCTION_ENERGY = 300
DEFAULT_MAX_AGE = 500  # 0 means indefinite lifespan
DEFAULT_ENERGY_GAIN_FROM_KILLING = 50
DEFAULT_REPRODUCTION_ENERGY_COST = 100
DEFAULT_MOVE_ENERGY_COST = 1
DEFAULT_IDLE_ENERGY_COST = 0.1
DEFAULT_PHEROMONE_ENERGY_COST = 5
DEFAULT_LONG_PROBE_ENERGY_COST = 2

# Simulation settings
MUTATION_RATE = 0.01

# Neural network settings
NUM_SENSORY_NEURONS = 21  # Update this to match the number of active sensors
NUM_INTERNAL_NEURONS = 4  # This can be adjusted as needed
NUM_ACTION_NEURONS = 16   # Update this to match the number of active actions
DEFAULT_NUM_GENES = 50    # Increase this to allow for more complex networks
