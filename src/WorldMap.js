import React, { useRef, useEffect } from 'react';

const WorldMap = ({ worldState }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!worldState || !Array.isArray(worldState) || worldState.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const imageData = ctx.createImageData(128, 128);

    for (let y = 0; y < 128; y++) {
      for (let x = 0; x < 128; x++) {
        const i = (y * 128 + x) * 4;
        if (worldState[y] && worldState[y][x]) {
          imageData.data[i] = worldState[y][x][0];     // Red
          imageData.data[i + 1] = worldState[y][x][1]; // Green
          imageData.data[i + 2] = worldState[y][x][2]; // Blue
          imageData.data[i + 3] = 255;                 // Alpha
        } else {
          imageData.data[i] = 0;     // Red
          imageData.data[i + 1] = 0; // Green
          imageData.data[i + 2] = 0; // Blue
          imageData.data[i + 3] = 255; // Alpha
        }
      }
    }

    ctx.putImageData(imageData, 0, 0);
  }, [worldState]);

  return (
    <div style={{
      border: '2px solid #FFD700',
      borderRadius: '10px',
      padding: '10px',
      margin: '20px 0',
      backgroundColor: 'rgba(0, 0, 0, 0.2)',
      width: '100%',
      height: '100%',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
    }}>
        <div style={{ 
        fontFamily: '"Press Start 2P", cursive',
        fontSize: '24px',
        marginBottom: '20px',
        color: '#FFD700',  // Gold color
        textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
        padding: '10px',
        backgroundColor: 'rgba(0, 0, 0, 0.2)',
        width:'100%',
        height:'100%'
      }}>
        <h2 style={{ padding: '10px',
      margin: '20px 0',
      fontSize: '24px',
      display: 'flex',
      alignItems: 'center', }}>World Map</h2>
      
      <canvas 
        ref={canvasRef} 
        width={128} 
        height={128} 
        style={{ 
          width: '100%', 
          height: '100%', 
          imageRendering: 'pixelated',
        }} 
      />
      </div>
    </div>
  );
};

export default WorldMap;
