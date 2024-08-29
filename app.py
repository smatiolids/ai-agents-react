from dotenv import load_dotenv
from flask import Flask, jsonify, request
from astra_conn import AstraDBConnection
from sample_data_load import load_flight_tickets
load_dotenv()

from flight_agent import TheFlightAgent


app = Flask(__name__)

flight_agent = TheFlightAgent() 
astra_db = AstraDBConnection().get_session()

@app.route('/get-collections', methods=['GET'])
def get_data():
    collections = astra_db.list_collection_names()
    return jsonify(collections), 200

@app.route('/load-sample-data', methods=['POST'])
def load_data():
    res = load_flight_tickets(False)
    return jsonify(res), 200

@app.route('/react-agent', methods=['POST'])
def invoke_flight_assistant():
    try:
        data = request.json
        message = data.get('message')
        
        if not message:
            return jsonify({'error': 'Message attribute is required'}), 400

        result = flight_agent.invoke(message)

        return jsonify({'message': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':

    app.run(debug=True, use_reloader=True)
