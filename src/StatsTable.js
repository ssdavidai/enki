import React from 'react';

const statOrder = [
  "step_count",
  "population",
  "generation",
  "total_pheromone",
  "pheromone_locations",
  "total_food",
  "food_locations",
  "avg_creature_age",
  "oldest_creature_age"
];

const statNames = {
  step_count: "Year",
  population: "Population",
  generation: "Generation",
  total_pheromone: "Pheromone",
  pheromone_locations: "Pheromone Spots",
  total_food: "Available Food",
  food_locations: "Food Spots",
  avg_creature_age: "Average Age",
  oldest_creature_age: "Oldest Creature"
};

const StatsTable = ({ stats }) => {
  console.log("StatsTable received stats:", stats);

  if (!stats || Object.keys(stats).length === 0) return null;

  return (
    <div style={{
      border: '2px solid #FFD700',
      borderRadius: '10px',
      padding: '20px',
      margin: '20px 0',
      backgroundColor: 'rgba(0, 0, 0, 0.2)',
      width: '100%',
      height: '100%',
      overflowY: 'auto',
    }}>
      <h2 style={{ 
        fontFamily: '"Press Start 2P", cursive',
        fontSize: '24px',
        marginBottom: '20px',
        color: '#FFD700',  // Gold color
        textShadow: '2px 2px 4px rgba(0,0,0,0.5)'
      }}>
        World Data
      </h2>
      <table style={{
        fontFamily: '"Press Start 2P", cursive',
        fontSize: '12px',
        borderCollapse: 'separate',
        borderSpacing: '0 10px',
        color: '#fff',
        width: '100%',
      }}>
        <tbody>
          {statOrder.map(key => (
            <tr key={key} style={{ marginBottom: '10px' }}>
              <td style={{ 
                textAlign: 'left', 
                paddingRight: '20px', 
                borderRight: '1px solid #FFD700'
              }}>
                {statNames[key] || key}:
              </td>
              <td style={{ paddingLeft: '20px' }}>
                {key in stats ? 
                  (typeof stats[key] === 'number' ? Math.round(stats[key]) : stats[key]) 
                  : 'N/A'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StatsTable;