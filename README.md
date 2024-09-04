# Enki World Simulator

## Overview

The Enki World Simulator is a virtual ecosystem where creatures live, evolve, and interact with their environment. This project is designed to simulate a world with various creatures that have neural networks controlling their behavior. The simulation includes features such as reproduction, mutation, and environmental interactions.

## Directory Structure

- `src/creature.py`: Defines the `Creature` class and its neural network.
- `src/world.py`: Manages the simulation world, including creatures, food, and pheromones.
- `src/simulation.py`: Controls the simulation flow.
- `src/api.py`: Provides API endpoints for starting and interacting with the simulation.
- `src/config.py`: Contains configuration variables.
- `src/utils.py`: Provides utility functions and logging setup.
- `src/tests/`: Contains unit tests for the simulation.
- `public/`: Contains static files for the frontend.
- `src/index.js`: Entry point for the React frontend.
- `src/App.js`: Main React component for the frontend.
- `src/WorldMap.js`: React component for displaying the world map.
- `src/StatsTable.js`: React component for displaying simulation statistics.
- `src/CreatureData.js`: React component for displaying creature data.
- `src/server.js`: Express server for handling API requests.
- `src/reportWebVitals.js`: Utility for reporting web vitals.
- `src/setupTests.js`: Setup for Jest testing.

## How to Run

1. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    npm install
    ```

2. **Start the backend server**:
    ```bash
    python -m enki_simulator.api
    ```

3. **Start the frontend development server**:
    ```bash
    npm start
    ```

4. **Interact with the simulation**:
    - Access the frontend at `http://localhost:3000`.
    - Use the provided API endpoints to interact with the simulation.

## API Endpoints

- **Start Simulation**: `POST /api/start-simulation`
    - Starts the simulation with optional parameters.
    - Example request body:
        ```json
        {
            "width": 128,
            "height": 128,
            "initial_population": 1000
        }
        ```

- **Get Simulation Data**: `GET /api/simulation-data`
    - Streams real-time simulation data.

- **Test Endpoint**: `GET /api/test`
    - Returns a simple message to verify the backend is working.

## Configuration

Configuration variables are defined in `src/config.py`. Key settings include:

- `WORLD_WIDTH`: Width of the simulation world.
- `WORLD_HEIGHT`: Height of the simulation world.
- `INITIAL_POPULATION`: Initial number of creatures.
- `DEFAULT_MIN_REPRODUCTION_ENERGY`: Minimum energy required for reproduction.
- `DEFAULT_MAX_AGE`: Maximum age of creatures.
- `DEFAULT_ENERGY_GAIN_FROM_KILLING`: Energy gained from killing another creature.
- `DEFAULT_REPRODUCTION_ENERGY_COST`: Energy cost of reproduction.
- `DEFAULT_MOVE_ENERGY_COST`: Energy cost of movement.
- `DEFAULT_IDLE_ENERGY_COST`: Energy cost of idling.
- `DEFAULT_PHEROMONE_ENERGY_COST`: Energy cost of emitting pheromones.
- `DEFAULT_LONG_PROBE_ENERGY_COST`: Energy cost of long-range probing.
- `MUTATION_RATE`: Rate of mutation during reproduction.
- `NUM_SENSORY_NEURONS`: Number of sensory neurons in the neural network.
- `NUM_INTERNAL_NEURONS`: Number of internal neurons in the neural network.
- `NUM_ACTION_NEURONS`: Number of action neurons in the neural network.
- `DEFAULT_NUM_GENES`: Default number of genes in a creature's genome.

## Frontend

The frontend is built with React and includes the following components:

- `App.js`: Main component that manages the simulation state and user interactions.
- `WorldMap.js`: Displays the world map with creatures and food.
- `StatsTable.js`: Displays statistics about the simulation.
- `CreatureData.js`: Displays detailed data about the creatures' neural networks.

## Backend

The backend is built with Flask and Express, providing the following functionalities:

- **Flask API** (`src/api.py`):
    - Handles simulation control and data streaming.
    - Provides endpoints for starting the simulation and retrieving data.

- **Express Server** (`src/server.js`):
    - Manages client connections and streams simulation data to the frontend.

## Simulation Logic

The core simulation logic is implemented in the following modules:

- **Creature** (`src/creature.py`):
    - Defines the `Creature` class, including its neural network and behavior.
    - Handles reproduction, mutation, and action prediction.

- **World** (`src/world.py`):
    - Manages the simulation world, including creatures, food, and pheromones.
    - Updates the state of the world and processes creature actions.

- **Simulation** (`src/simulation.py`):
    - Controls the overall simulation flow.
    - Initializes the world and runs simulation steps.

## Testing

Unit tests are located in the `src/tests/` directory. To run the tests, use:
