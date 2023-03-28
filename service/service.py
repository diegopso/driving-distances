
from flask import Flask, jsonify, request
from dotenv import dotenv_values
from repositories import DrivenDistanceRepository

service = Flask(__name__)

config = dotenv_values('.env')
repository = DrivenDistanceRepository(
    host_name=config['DB_HOST'], 
    db_name=config['DB_DATABASE'], 
    user=config['DB_USERNAME'], 
    password=config['DB_PASSWORD'],
)

@service.route('/', methods=['GET'])
@service.route('/api', methods=['GET'])
def index():
    return jsonify("It Works!")

@service.route('/api/driving-distances', methods=['GET'])
def getDrivingDistances():
    try:
        query = request.args
        vehicleId = query.get("vehicle_id", default=None, type=str)
        startDate = query.get("start_date", default=None, type=str)
        endDate = query.get("end_date", default=None, type=str)

        result = repository.getDrivingDistances(vehicleId, startDate, endDate)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "error": str(e)
        })

if __name__ == '__main__':
    service.run()