import React, { useRef, useEffect, useState } from 'react';

const CreatureData = ({ medianGenome, numSensory, numInternal, numAction }) => {
  const canvasRef = useRef(null);
  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const updateCanvasSize = () => {
      const container = canvasRef.current.parentElement;
      const width = container.clientWidth;
      const height = container.clientHeight;
      setCanvasSize({ width, height });
    };

    updateCanvasSize();
    window.addEventListener('resize', updateCanvasSize);

    return () => window.removeEventListener('resize', updateCanvasSize);
  }, []);

  useEffect(() => {
    if (!medianGenome) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const { width, height } = canvasSize;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Define neuron positions
    const neuronRadius = 24; // 4 times larger than the original 10
    const maxNeuronsPerColumn = 10;
    const neuronSpacing = neuronRadius * 2 + 30;
    const columnSpacing = neuronRadius * 4; // Extra spacing between different types of neurons

    const getRandomOffset = () => (Math.random() - 0.5) * 20; // Random offset between -10 and 10

    const sensoryNeurons = Array(numSensory).fill().map((_, i) => ({
      x: 50 + Math.floor(i / maxNeuronsPerColumn) * neuronSpacing + getRandomOffset(),
      y: 50 + (i % maxNeuronsPerColumn) * neuronSpacing + getRandomOffset()
    }));
    const internalNeurons = Array(numInternal).fill().map((_, i) => ({
      x: width / 2 + Math.floor(i / maxNeuronsPerColumn) * neuronSpacing + getRandomOffset(),
      y: 50 + (i % maxNeuronsPerColumn) * neuronSpacing + getRandomOffset()
    }));
    const actionNeurons = Array(numAction).fill().map((_, i) => ({
      x: width - 50 - Math.floor(i / maxNeuronsPerColumn) * neuronSpacing + getRandomOffset(),
      y: 50 + (i % maxNeuronsPerColumn) * neuronSpacing + getRandomOffset()
    }));

    // Draw connections
    const drawConnection = (source, sink, weight) => {
      if (!source || !sink) return;
      ctx.beginPath();
      ctx.moveTo(source.x, source.y);
      const controlPointX = (source.x + sink.x) / 2 + getRandomOffset();
      const controlPointY = (source.y + sink.y) / 2 + getRandomOffset();
      ctx.quadraticCurveTo(controlPointX, controlPointY, sink.x, sink.y);
      ctx.strokeStyle = weight > 0 ? '#FFD700' : '#FFFFFF';
      // Scale the line width based on the weight, but keep it within a reasonable range
      const scaledWeight = Math.abs(weight) / 32768; // Assuming weight is a 16-bit integer
      ctx.lineWidth = Math.max(2, Math.min(5, scaledWeight * 5));
      ctx.stroke();
    };

    // Check if medianGenome is defined and has elements
    if (medianGenome && medianGenome.length > 0) {
      medianGenome.forEach(gene => {
        const sourceType = gene.source_type;
        const sourceId = gene.source_num;
        const sinkType = gene.sink_type;
        const sinkId = gene.sink_num;
        const weight = gene.weight;

        let source, sink;

        if (sourceType === 1) { // SENSOR
          source = sensoryNeurons[sourceId % numSensory];
        } else { // NEURON
          source = internalNeurons[sourceId % numInternal];
        }

        if (sinkType === 1) { // ACTION
          sink = actionNeurons[sinkId % numAction];
        } else { // NEURON
          sink = internalNeurons[sinkId % numInternal];
        }

        if (source && sink) {
          drawConnection(source, sink, weight);
        }
      });

      // Draw neurons
      const drawNeuron = (x, y, label) => {
        ctx.beginPath();
        ctx.arc(x, y, neuronRadius, 0, 2 * Math.PI); // Use neuronRadius for larger neurons
        ctx.fillStyle = 'white';
        ctx.fill();
        ctx.strokeStyle = 'black';
        ctx.stroke();
        ctx.fillStyle = 'black';
        ctx.font = '18px Press Start 2P';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle'; // Center the text vertically
        ctx.fillText(label, x, y); // Position the label inside the neuron
      };

      sensoryNeurons.forEach((n, i) => drawNeuron(n.x, n.y, `S${i}`));
      internalNeurons.forEach((n, i) => drawNeuron(n.x, n.y, `I${i}`));
      actionNeurons.forEach((n, i) => drawNeuron(n.x, n.y, `A${i}`));
    }

  }, [medianGenome, canvasSize, numSensory, numInternal, numAction]);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '20px',
      margin: '20px 0',
      width: '100%',
      height: '900px', // Ensure this div has a fixed height
      boxSizing: 'border-box'
    }}>
      <div style={{ 
        fontFamily: '"Press Start 2P", cursive',
        fontSize: '24px',
        marginBottom: '20px',
        color: '#FFD700',  // Gold color
        textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
        padding: '10px',
        border: '2px solid #FFD700',
        borderRadius: '5px',
        backgroundColor: 'rgba(0, 0, 0, 0.2)',
        width: '100%',
        height: '100%', // Make this div fill the parent div
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        <h2 style={{ paddingTop: '10px',
      margin: '20px 20px 20px 20px',
      fontSize: '24px',
      display: 'flex',
      alignItems: 'center',
      textAlign: 'left', // Align text to the left
      alignSelf: 'flex-start' // Align the h2 element itself to the start of the parent

    }}>Brain Anatomy</h2>
            
      <canvas 
        ref={canvasRef} 
        width={canvasSize.width}
        height={canvasSize.height}
        style={{ 
            width: '100%',
            height: '100%' // Make the canvas fill the available space
        }} 
      />
        
      </div>
      
    </div>
  );
};

export default CreatureData;
