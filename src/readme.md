# Enki World Simulator

## Overview

The Enki World Simulator is a virtual ecosystem where creatures live and evolve. This project has been refactored to separate different responsibilities into specific modules.

## Directory Structure

- `creature.py`: Defines the Creature class and neural network.
- `world.py`: Manages the simulation world, including creatures, food, and pheromones.
- `simulation.py`: Controls the simulation flow.
- `api.py`: Provides API endpoints for starting and interacting with the simulation.
- `config.py`: Contains configuration variables.
- `utils.py`: Provides utility functions and logging setup.
- `tests/`: Contains unit tests for the simulation.

## How to Run

1. Install dependencies: `pip install -r requirements.txt`
2. Start the API server: `python -m enki_simulator.api`
3. Interact with the simulation through the provided API endpoints.

## Running Tests

Run the unit tests with:

```bash
python -m unittest discover tests/
