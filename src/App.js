import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import './arcadeButton.css';
import StatsTable from './StatsTable';
import WorldMap from './WorldMap';
import CreatureData from './CreatureData';

const NUM_SENSORY_NEURONS = 21;
const NUM_INTERNAL_NEURONS = 4;
const NUM_ACTION_NEURONS = 16;

function App() {
  const [simulationStarted, setSimulationStarted] = useState(false);
  const [simulationData, setSimulationData] = useState({ stats: {}, median_genome: [], world_state: [] });
  const [error, setError] = useState(null);
  const [simulationStatus, setSimulationStatus] = useState('idle');
  const [simulationParams, setSimulationParams] = useState({
    min_reproduction_energy: 300,
    max_age: 500,
    energy_gain_from_killing: 50,
    reproduction_energy_cost: 100,
    move_energy_cost: 1,
    idle_energy_cost: 0.1,
    pheromone_energy_cost: 5,
    long_probe_energy_cost: 2,
    num_genes: 4,
    steps_per_generation: 100,
  });
  const eventSourceRef = useRef(null);

  const handleParamChange = (e) => {
    setSimulationParams({
      ...simulationParams,
      [e.target.name]: parseFloat(e.target.value),
    });
  };

  const startSimulation = () => {
    fetch('/api/start-simulation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(simulationParams),
    })
    .then(response => response.json())
    .then(data => {
      console.log('Simulation started:', data);
      setSimulationStatus('running');
      setSimulationStarted(true);
      startEventSource();
    })
    .catch((error) => {
      console.error('Error:', error);
      setError('Failed to start simulation. Please try again.');
    });
  };

  const startEventSource = () => {
    eventSourceRef.current = new EventSource('/api/simulation-data');
    eventSourceRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("Received data in App.js:", data);
        setSimulationData(data);
        if (data.isSimulationOver) {
          setSimulationStatus('over');
          eventSourceRef.current.close();
        }
      } catch (error) {
        console.error("Error parsing data:", error);
        setError(`Error parsing simulation data: ${error.message}`);
      }
    };
    eventSourceRef.current.onerror = () => {
      setError('Connection to simulation lost. Please refresh the page and try again.');
      eventSourceRef.current.close();
    };
  };

  const resetSimulation = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    setSimulationStarted(false);
    setSimulationData({ stats: {}, median_genome: [], world_state: [] });
    setError(null);
    setSimulationStatus('idle');
  };

  const endSimulation = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    setSimulationStatus('over');
  };

  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1 style={{ fontFamily: '"Press Start 2P", cursive' }}>Welcome to Enki!</h1>
        {!simulationStarted ? (
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            width: '100%'
          }}>
            <form onSubmit={(e) => { e.preventDefault(); startSimulation(); }}>
              <table style={{ 
                fontFamily: '"Press Start 2P", cursive',
                fontSize: '14px',
                borderCollapse: 'separate',
                borderSpacing: '0 20px'
              }}>
                <tbody>
                  {Object.entries(simulationParams).map(([key, value]) => (
                    <tr key={key}>
                      <td style={{paddingRight: '10px' }}>
                        {key.replace(/_/g, ' ').charAt(0).toUpperCase() + key.replace(/_/g, ' ').slice(1)}:
                      </td>
                      <td>
                        <input
                          type="number"
                          name={key}
                          value={value}
                          onChange={handleParamChange}
                          step={key.includes('energy') ? 0.1 : 1}
                          style={{
                            fontFamily: '"Press Start 2P", cursive',
                            fontSize: '12px',
                            backgroundColor: 'transparent',
                            color: 'white',
                            border: '1px solid white',
                            padding: '5px',
                            width: '100px'
                          }}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
                <button 
                  className="arcade-button" 
                  type="submit"
                  style={{ 
                    fontFamily: '"Press Start 2P", cursive',
                    fontSize: '16px'
                  }}
                >
                  Start Simulation
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', maxWidth: '800px', margin: '0 auto' }}>
            <WorldMap worldState={simulationData.world_state} />
            {simulationStatus === 'over' && (
              <div style={{
                color: 'red',
                fontFamily: '"Press Start 2P", cursive',
                fontSize: '18px',
                textAlign: 'center',
                margin: '10px 0',
                lineHeight: '1.5', 
                backgroundColor: 'white'
              }}>
                Everyone died. <br />The world of Enki is now a barren land.
              </div>
            )}
            <StatsTable stats={simulationData.stats} />
            <CreatureData 
              medianGenome={simulationData.median_genome}
              numSensory={NUM_SENSORY_NEURONS}
              numInternal={NUM_INTERNAL_NEURONS}
              numAction={NUM_ACTION_NEURONS}
            />
            <div style={{ display: 'flex', justifyContent: 'center', gap: '30px', margin: '20px 20px 10% 20px' }}>
              <button className="arcade-button" onClick={resetSimulation}>Reset</button>
              <button className="arcade-button" onClick={endSimulation}>End</button>
            </div>
          </div>
        )}
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </header>
    </div>
  );
}

export default App;