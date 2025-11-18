
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from models import db, Plant, User
from werkzeug.exceptions import NotFound, HTTPException
from external_apis import get_plant_image, get_weather
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///plants.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'strong_secret_key' # TODO: dont have secret displayed like this 
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()





@app.route('/get_user', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    # if not username or not email or not password:
    #     return jsonify({'message': 'Missing required fields'}), 400

    if user:
        return jsonify({'message': 'Sucess', 'name': user.username}), 200
    else:
        return jsonify({'message': 'Failed'}), 404



@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Missing required fields'}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, email=email, password=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message':'User registered'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        token = create_access_token(identity=str(user.id)) # TODO: add timeout refresh token endpoint and generate new access token 
        return jsonify({'token': token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401


class PlantResource(Resource):

    def get(self, plant_id=None):
        if plant_id:
            plant = Plant.query.get(plant_id)
            if plant is None:
                return jsonify({'message': f'Plant with id {plant_id} not found'}), 404

            image_url = None
            image_url = get_plant_image(plant.name)       

            return {
                'id': plant.id,
                'name': plant.name,
                'location': plant.location,
                'date_planted': plant.date_planted,
                'height': plant.height,
                'watered': plant.watered,
                'notes': plant.notes,
                'image_url': image_url
            }
        else:
            plants = Plant.query.all()
            if not plants:
                return{'plants':[], 'message': 'no plants found'}
            return [
                {
                    'id': plant.id,
                    'name': plant.name,
                    'location': plant.location,
                    'date_planted': plant.date_planted,
                    'height': plant.height,
                    'watered': plant.watered,
                    'notes': plant.notes,
                    'image_url': get_plant_image(plant.name)
                }
                for plant in plants
            ]


    def post(self):
        data = request.get_json()

        if not data.get('name'):
            return{'message': 'please enter a plant name'}, 400

        if not data.get('location'):
            return{'message':'please enter a location'}, 400

        if not data.get('date_planted'):
            return{'message': 'please enter a date'}, 400

        height = None
        if data.get('height') is not None:
            try: 
                height = float(data.get('height'))
                if height < 0:
                    return{'message': 'height cant be negative'}, 400
            except ValueError:
                return{'message': 'height must be a number'}, 400


        new_plant = Plant(
            name=data['name'],
            location=data.get('location'),
            date_planted=data.get('date_planted'),
            height=height,
            watered=data.get('watered', False),
            notes=data.get('notes')
        )
        db.session.add(new_plant)
        db.session.commit()
        return {'message': 'plant added successfully'}, 201


    def put(self, plant_id):
        data = request.get_json()
        plant = Plant.query.get(plant_id) 
        if not plant: 
            return jsonify({'message': f'Plant with id {plant_id} not found'}), 404

        if 'name' in data:
            plant.name = data['name']

        if 'location' in data:
            plant.location = data['location']

        if 'date_planted' in data:
            plant.date_planted = data['date_planted']


        height = plant.height
        if data.get('height') is not None:
            try: 
                height = float(data.get('height'))
                if height < 0:
                    return{'message': 'height cant be negative'}, 400
            except ValueError:
                return{'message': 'height must be a number'}, 400

        plant.name = data.get('name', plant.name)
        plant.location = data.get('location', plant.location)
        plant.date_planted = data.get('date_planted', plant.date_planted)
        plant.height = height
        plant.watered = data.get('watered', plant.watered)
        plant.notes = data.get('notes', plant.notes)
        db.session.commit()
        return {'message': 'plant updated successfully'}, 200


    def delete(self, plant_id):
        plant = Plant.query.get(plant_id) 
        if not plant: 
            return jsonify({'message': f'Plant with id {plant_id} not found'}), 404
        db.session.delete(plant)
        db.session.commit()
        return {'message': 'plant deleted successfully'}, 200



@app.route("/weather/<string:city>", methods=["GET"])
def weather(city):
    weather_info = get_weather(city)
    if "error" in weather_info:
        return jsonify(weather_info), 404
    return jsonify(weather_info), 200



# Routes
api = Api(app)
api.add_resource(PlantResource, '/plants', '/plants/<int:plant_id>')

@app.route('/')
def home():
    return {'message': 'Welcome'}


# @app.errorhandler(HTTPException)
# def handle_http_exception(e):
#     return jsonify({'message': e.description}), e.code

# @app.errorhandler(Exception)
# def handle_exception(e):
#     return jsonify({'message': 'An unexpected error occurred'}), 400



if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=3000)


# cmd for venv
#  source ./venv/bin/activate

# ./runProgram.sh