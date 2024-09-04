# api.py

from flask import Flask, jsonify, Response, request
from flask_cors import CORS
import json
from .simulation import simulation
import logging
from .utils import setup_logging
import sys

setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/api/start-simulation', methods=['POST'])
def start_simulation():
    try:
        params = request.json if request.json else {}
        simulation.start_simulation(params)
        return jsonify({"message": "Simulation started successfully", "params": simulation.params}), 200
    except Exception as e:
        logger.error(f"Failed to start simulation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/simulation-data')
def simulation_data():
    def generate():
        if simulation.world is None:
            yield f"data: {json.dumps({'error': 'Simulation not started'})}\n\n"
            return
        while True:
            try:
                simulation.run_step()
                data = simulation.get_simulation_data()
                logger.info(f"Sending data: {data}")
                yield f"data: {json.dumps(data)}\n\n"
                
                if data['isSimulationOver']:
                    break
            except Exception as e:
                error_message = f"Error in simulation_data: {str(e)}"
                logger.error(error_message, exc_info=True)
                yield f"data: {json.dumps({'error': error_message})}\n\n"
                break
            sys.stdout.flush()
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({"message": "Backend is working"}), 200

if __name__ == "__main__":
    logger.info("Starting the Flask application")
    app.run(debug=False, threaded=True, port=5000)
