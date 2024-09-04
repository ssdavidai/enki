const express = require('express');
const app = express();
const port = 3000;

let clients = [];

app.use(express.json());

app.post('/api/start-simulation', (req, res) => {
  // Start your simulation logic here
  res.json({ message: 'Simulation started' });
  startSimulation();
});

app.get('/api/simulation-data', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();

  clients.push(res);

  req.on('close', () => {
    clients = clients.filter(client => client !== res);
  });
});

function startSimulation() {
  let step = 0;
  const interval = setInterval(() => {
    step++;
    const data = {
      step,
      stats: {
        step_count: step,
        population: Math.floor(Math.random() * 100),
        generation: Math.floor(step / 10),
        total_pheromone: Math.random() * 1000,
        pheromone_locations: Math.floor(Math.random() * 50),
        total_food: Math.random() * 500,
        food_locations: Math.floor(Math.random() * 30),
        avg_creature_age: Math.random() * 100,
        oldest_creature_age: Math.random() * 200
      },
      world_state: {
        creatures: [
          { id: 1, x: Math.random() * 100, y: Math.random() * 100, energy: Math.random() * 100 },
          { id: 2, x: Math.random() * 100, y: Math.random() * 100, energy: Math.random() * 100 }
        ],
        food_sources: [
          { id: 1, x: Math.random() * 100, y: Math.random() * 100, amount: Math.random() * 100 },
          { id: 2, x: Math.random() * 100, y: Math.random() * 100, amount: Math.random() * 100 }
        ]
      },
      median_genome: [
        { source_type: 1, source_num: 0, sink_type: 2, sink_num: 1, weight: Math.random() * 2 - 1 },
        { source_type: 2, source_num: 1, sink_type: 1, sink_num: 0, weight: Math.random() * 2 - 1 }
      ],
      isSimulationOver: step >= 1000 // Example condition to end simulation
    };

    clients.forEach(client => client.write(`data: ${JSON.stringify(data)}\n\n`));

    if (data.isSimulationOver) {
      clearInterval(interval);
      clients.forEach(client => client.end());
    }
  }, 1000); // Adjust the interval as needed
}

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
