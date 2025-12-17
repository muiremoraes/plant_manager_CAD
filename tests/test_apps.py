
import pytest 
from app import app, db, bcrypt
from models import Plant, User
from flask_jwt_extended import create_access_token





@pytest.fixture
def client():
    """sets up pytest DB"""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:" # DB in memory

    app.config["SECRET_KEY"]="test-secret"
    app.config["JWT_SECRET_KEY"]="test-jwt-secret"

    with app.test_client() as client: # create a temp client for requests
        with app.app_context(): 
            db.create_all() # create DB with all tables
            yield client # run using this client
            db.drop_all()



def auth(client):
    with app.app_context():
        hashed_pw=bcrypt.generate_password_hash("Password123").decode("utf-8") #generate hashed pass
        user = User(username="testuser", email="test@test.com", password=hashed_pw) #user obejct 
        db.session.add(user) #add user to database
        db.session.commit()

        token = create_access_token(identity=str(user.id)) #generate JWT access token for new user 
        return {
            "Authorization": f"Bearer {token}" #return header for testing
        }




def test_create_plant(client):
    """tests POST request for adding new plant"""
    headers=auth(client)
    response = client.post("/plants", json={ 
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    }, headers=headers) #pass jwt header
    assert response.status_code == 201 
    data = response.get_json() 
    assert data["message"] == "plant added successfully"


def test_create_plant_with_missing_name(client):
    """test POST request for adding plant with name missing"""
    headers=auth(client)
    response = client.post("/plants", json={
        "location": "Dublin",
        "date_planted": "09-11-2025",
    }, headers=headers)
    assert response.status_code == 400
    
    

def test_create_plant_with_missing_location(client):
    """test POST request for adding plant with location missing"""
    headers=auth(client)
    response = client.post("/plants", json={
        "name": "Lily",
        "date_planted": "09-11-2025"
    }, headers=headers)
    assert response.status_code == 400
    
    
    

def test_create_plant_with_missing_date(client):
    """test POST request for adding plant with date missing"""
    headers=auth(client)
    response = client.post("/plants", json={
        "name": "Lily",
        "location": "Kildare"
    }, headers=headers)
    assert response.status_code == 400
    


def test_create_plant_minus_for_height(client):
    "test POST for adding plant with minus height number"
    headers=auth(client)
    response = client.post("/plants", json={
        "name": "Lily",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": -10.5,
        "watered": True,
        "notes": "looks pretty"
    }, headers=headers)
    assert response.status_code == 400
    


def test_create_plant_string_for_height(client):
    "test POST for adding plant with string for height"
    headers=auth(client)
    response = client.post("/plants", json={
        "name": "Lily",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": "tall",
        "watered": True,
        "notes": "looks pretty"
    }, headers=headers)
    assert response.status_code == 400
    
    

def test_get_all_plants(client):
    """test to get all plants"""
    headers=auth(client)
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    }, headers=headers)
    response = client.get("/plants",headers=headers)
    assert response.status_code == 200
   
    


def test_get_all_plants_with_empty(client):
    """test to get all plants but no plant posted"""
    headers=auth(client)
    response = client.get("/plants", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["plants"] == []


def test_get_plant_by_id(client):
    """test to get a plant by id"""
    headers=auth(client)
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    },headers=headers)

    response = client.get("/plants/1",headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Rose"



def test_get_plant_by_id_that_doesnt_exist(client):
    """test to get a plant by id"""
    headers = auth(client)
    response = client.get("/plants/900",headers=headers)
    assert response.status_code == 404
   

def test_update_plant(client):
    """test update plant"""
    headers = auth(client)
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    },headers=headers)

    response = client.put("/plants/1", json={
        "name": "Pink Rose",
        "location": "Kildare",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    },headers=headers)
    assert response.status_code == 200
   



def test_update_plant_that_doesnt_exist(client):
    """test update plant that doesnt exist"""
    headers = auth(client)
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    })

    response = client.put("/plants/100", json={
        "name": "Pink Rose",
        "location": "Kildare",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    },headers=headers)
    assert response.status_code == 404
    



def test_update_plant_with_missing_field(client):
    """test update plant with missing field"""
    headers = auth(client)
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    }, headers=headers)

    response = client.put("/plants/1", json={
        "location": "Kildare",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    },headers=headers)
    assert response.status_code == 200
    


def test_update_plant_with_negative_height_value(client):
    """test update plant with negative height value"""
    headers = auth(client)
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    },headers=headers)

    response = client.put("/plants/1", json={
        "name": "Pink Rose",
        "location": "Kildare",
        "date_planted": "09-11-2025",
        "height": -10.5,
        "watered": True,
        "notes": "looks pretty"
    },headers=headers)
    assert response.status_code == 400
    


def test_update_plant_with_string_value_for_height(client):
    """test update plant with string height value"""
    headers = auth(client)
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    },headers=headers)

    response = client.put("/plants/1", json={
        "name": "Pink Rose",
        "location": "Kildare",
        "date_planted": "09-11-2025",
        "height": "tall",
        "watered": True,
        "notes": "looks pretty"
    },headers=headers)
    assert response.status_code == 400
    



def test_delete_plant(client):
    """test delete plant"""
    headers = auth(client)
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    },headers=headers)

    response = client.delete("/plants/1",headers=headers)
    assert response.status_code == 200
 


def test_delete_plant_that_doesnt_exist(client):
    """test delete plant that doesnt exist"""
    headers = auth(client)
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    },headers=headers)

    response = client.delete("/plants/100",headers=headers)
    assert response.status_code == 404


def test_delete_plant_using_string_value(client):
    """test delete plant using string value"""
    headers = auth(client)
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    },headers=headers)

    response = client.delete("/plants/abc",headers=headers)
    assert response.status_code in (400, 404)
    

def test_get_weather(client):
    response = client.get("/weather/Dublin")
    assert response.status_code == 200


def test_get_weather_with_no_correct_city(client):
    response = client.get("/weather/blah")
    assert response.status_code == 404


def test_get_weather_with_blank(client):
    response = client.get("/weather/")
    assert response.status_code == 404


def test_get_weather_with_a_number(client):
    response = client.get("/weather/123")
    assert response.status_code == 404


def test_get_image(client):
    response = client.get("/image/rose")
    assert response.status_code == 200


def test_get_image_with_image_doesnt_exist(client):
    response = client.get("/image/fancy flower")
    assert response.status_code == 404


def test_get_image_with_number(client):
    response = client.get("/image/1234")
    assert response.status_code == 404


def test_register(client):
    response = client.post("/register", json={
        "username":"123user",
        "email":"user@person.com",
        "password":"SuperPass123"
    })
    assert response.status_code == 201



def test_register_weak_pass_less_than_8_char(client):
    response = client.post("/register", json={
        "username":"123user",
        "email":"user@person.com",
        "password":"pass"
    })
    assert response.status_code == 400


def test_register_weak_pass_no_upper_c(client):
    response = client.post("/register", json={
        "username":"123user",
        "email":"user@person.com",
        "password":"password123"
    })
    assert response.status_code == 400

def test_register_weak_pass_no_lower_c(client):
    response = client.post("/register", json={
        "username":"123user",
        "email":"user@person.com",
        "password":"PASSWORD123"
    })
    assert response.status_code == 400

def test_register_no_a_in_email(client):
    response = client.post("/register", json={
        "username":"123user",
        "email":"userperson.com",
        "password":"Password123"
    })
    assert response.status_code == 400



def test_register_no_a_in_email(client):
    client.post("/register", json={
        "username":"123user",
        "email":"userperson.com",
        "password":"Password123"
    })
    response = client.post("/register", json={
        "username":"1234user",
        "email":"userperson.com",
        "password":"Password1234"
    })
    assert response.status_code == 400



def test_login(client):
    client.post("/register", json={
        "username":"123user",
        "email":"user@person.com",
        "password":"Password123"
    })
    response = client.post("/login", json={
        "username":"123user",
        "password":"Password123"
    })
    assert response.status_code == 200


def test_login_with_no_password(client):
    client.post("/register", json={
        "username":"123user",
        "email":"user@person.com",
        "password":"Password123"
    })
    response = client.post("/login", json={
        "username":"123user",
        "password":""
    })
    assert response.status_code == 400



def test_login_with_incorrect_password(client):
    client.post("/register", json={
        "username":"123user",
        "email":"user@person.com",
        "password":"Password123"
    })
    response = client.post("/login", json={
        "username":"123user",
        "password":"abcPassword123"
    })
    assert response.status_code == 401










# cmd to run test
# PYTHONPATH=. pytest -v -k "test"





