
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
from models import db, Plant, User
from werkzeug.exceptions import NotFound, HTTPException
from external_apis import get_plant_image, get_weather
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__) #initalise flask app

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///plants.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", default=None)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", default=None) #uses envoirment variables for secret keys

#initalise 
db.init_app(app) #db
bcrypt = Bcrypt(app)#password hashing
jwt = JWTManager(app)#jwt 

with app.app_context(): #create db id it doesnt exist
    db.create_all()

CORS(app, resources={r"*": {"origins": "*"}}, supports_credentials=True, expose_headers=["Authorization"])

@app.after_request
def secure_headers(response): # secuirty headeder sent after every request
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains' # forces https

    response.headers['Content-Security-Policy'] = ("default-src 'self'; " "frame-ancestors 'none'; " "form-action 'self'; ")
    # only load resources from server, prevent embedding url on site and can only send form to site
    response.headers['X-Content-Type-Options'] = 'nosniff' # preveent content sniffing as that would let a user see the format of data
    response.headers['X-Frame-Options'] = 'SAMEORIGIN' # prevents malicous useing hiding links on page
    response.headers['X-XSS-Protection'] = '1; mode=block' #XSS filter
    return response


@app.route('/get_user', methods=['GET']) #get user endpoint for testing
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    # if not username or not email or not password:
    #     return {'message': 'Missing required fields'}, 400

    if user:
        return {'message': 'Sucess', 'name': user.username}, 200
    else:
        return {'message': 'Failed'}, 404



@app.route('/register', methods=['POST'])# endpoint to register a new user
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password') #get info from the form

    if not username or not email or not password:
        return {'message': 'Missing required fields'}, 400

    if "@" not in email:
        return {"message":"please enter a valid email"},400
    
    if User.query.filter_by(email=email).first():
        return {"message":"one email per account"},400

    if User.query.filter_by(username=username).first():
        return {"message":"username already exists"},400

    if len(password) < 8:
        return {"message":"Password must be at least 8 long."},400
    if not any(c.isupper() for c in password):
        return {"message":"password must have at least one uppercase letter."},400
    if not any(c.islower() for c in password):
        return {"message":"password must have at least one lowercase letter."},400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8') #hash password before storing 
    user = User(username=username, email=email, password=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return {'message':'User registered'}, 201


@app.route('/login', methods=['POST']) #user login path 
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return {'message': 'Missing required fields'}, 400

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password): #if user and password create JWT
        token = create_access_token(identity=str(user.id)) 
        return {'token': token}, 200

    return {'message': 'Invalid credentials'}, 401


class PlantResource(Resource): #plant resource for CRUD

    @jwt_required()
    def get(self, plant_id=None): #gets plants
        if plant_id:
            plant = Plant.query.get(plant_id)
            if plant is None:
                return{'message': f'Plant with id {plant_id} not found'}, 404

            image_url = None
            image_url = get_plant_image(plant.name) #get image from external API

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
                return{'plants':[], 'message': 'no plants found'} #returns if no plants
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


    @jwt_required()
    def post(self): #add plants
        data = request.get_json()

        if not data.get('name'):
            return{'message': 'please enter a plant name'}, 400

        if not data.get('location'):
            return{'message':'please enter a location'}, 400

        if not data.get('date_planted'):
            return{'message': 'please enter a date'}, 400
            #checks all feilds

        height = None #checks height
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
            watered=bool(data.get('watered', False)),
            notes=data.get('notes')
        )
        db.session.add(new_plant) #add to DB
        db.session.commit()
        return {'message': 'plant added successfully'}, 201


    @jwt_required()
    def put(self, plant_id): #edit plant info
        data = request.get_json()
        plant = Plant.query.get(plant_id) 
        if not plant: 
            return {'message': f'Plant with id {plant_id} not found'}, 404

        if 'name' in data:
            plant.name = data['name']

        if 'location' in data:
            plant.location = data['location']

        if 'date_planted' in data:
            plant.date_planted = data['date_planted']
            #update feild if change occured


        height = plant.height #validates height
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
        db.session.commit()
        return {'message': 'plant updated successfully'}, 200


    @jwt_required()
    def delete(self, plant_id):
        plant = Plant.query.get(plant_id) 
        if not plant: 
            return {'message': f'Plant with id {plant_id} not found'}, 404
        db.session.delete(plant)
        db.session.commit()
        return {'message': 'plant deleted successfully'}, 200


@app.route("/weather/<string:city>", methods=["GET"]) #reoute to check weathrt 
def weather(city):
    if app.config.get("TESTING"):
        if city.lower() == "dublin":    
            return {"temp":16, "condition":"sunny"},200 #return mock datatype
        else:
            return {"message":"city not found"},404
     
    weather_info = get_weather(city)
    if "error" in weather_info:
        return weather_info, 404
    return weather_info, 200

@app.route("/image/<string:plant>", methods=["GET"])
def image_test_fucntion(plant):
    if app.config.get("TESTING"):
        if plant.lower() =="rose":
            return {"image":"some image"},200
        else:
            return{"message":"error no image"},404




# Routes
api = Api(app)
api.add_resource(PlantResource, '/plants', '/plants/<int:plant_id>')

@app.route('/')
def home():
    return {'message': 'Welcome'}


# @app.errorhandler(HTTPException)
# def handle_http_exception(e):
#     return {'message': e.description}, e.code

# @app.errorhandler(Exception)
# def handle_exception(e):
#     return {'message': 'An unexpected error occurred'}, 400



if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=3000)


# cmd for venv
#  source ./venv/bin/activate

# ./runProgram.sh