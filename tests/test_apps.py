
import pytest 
from app import app, db
from models import Plant





@pytest.fixture
def client():
    """sets up pytest DB"""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:" # DB in memory

    with app.test_client() as client: # create a temp client for requests
        with app.app_context(): 
            db.create_all() # create DB with all tables
            yield client # run using this client
            db.drop_all()


def test_create_plant(client):
    """tests POST request for adding new plant"""
    response = client.post("/plants", json={ 
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    })
    assert response.status_code == 201 
    data = response.get_json() 
    assert data["message"] == "plant added successfully"


def test_create_plant_with_missing_name(client):
    """test POST request for adding plant with name missing"""
    response = client.post("/plants", json={
        "location": "Dublin",
        "date_planted": "09-11-2025",
    })
    assert response.status_code == 400
    data= response.get_json()
    

def test_create_plant_with_missing_location(client):
    """test POST request for adding plant with location missing"""
    response = client.post("/plants", json={
        "name": "Lily",
        "date_planted": "09-11-2025"
    })
    assert response.status_code == 400
    data= response.get_json()
    
    

def test_create_plant_with_missing_date(client):
    """test POST request for adding plant with date missing"""
    response = client.post("/plants", json={
        "name": "Lily",
        "location": "Kildare"
    })
    assert response.status_code == 400
    data= response.get_json()


def test_create_plant_minus_for_height(client):
    "test POST for adding plant with minus height number"
    response = client.post("/plants", json={
        "name": "Lily",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": -10.5,
        "watered": True,
        "notes": "looks pretty"
    })
    assert response.status_code == 400
    data = response.get_json


def test_create_plant_string_for_height(client):
    "test POST for adding plant with string for height"
    response = client.post("/plants", json={
        "name": "Lily",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": "tall",
        "watered": True,
        "notes": "looks pretty"
    })
    assert response.status_code == 400
    data = response.get_json
    

def test_get_all_plants(client):
    """test to get all plants"""
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    })
    response = client.get("/plants")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] in data[0]


def test_get_all_plants(client):
    """test to get all plants but no plant posted"""
    response = client.get("/plants")
    assert response.status_code == 200
    data = response.get_json()
    assert data["plants"] == []


def test_get_plant_by_id(client):
    """test to get a plant by id"""
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    })

    response = client.get("/plants/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Rose"



def test_get_plant_by_id_that_doesnt_exist(client):
    """test to get a plant by id"""
    response = client.get("/plants/900")
    assert response.status_code == 404
    data = response.get_json()
    

def test_update_plant(client):
    """test update plant"""
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    })

    response = client.put("/plants/1", json={
        "name": "Pink Rose",
        "location": "Kildare",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    })
    assert response.status_code == 200
    data = response.get_json()



def test_update_plant_that_doesnt_exist(client):
    """test update plant that doesnt exist"""
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
    })
    assert response.status_code == 404
    data = response.get_json()



def test_update_plant_with_missing_field(client):
    """test update plant with missing field"""
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    })

    response = client.put("/plants/1", json={
        "location": "Kildare",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    })
    assert response.status_code == 200
    data = response.get_json()


def test_update_plant_with_negative_height_value(client):
    """test update plant with negative height value"""
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    })

    response = client.put("/plants/1", json={
        "name": "Pink Rose",
        "location": "Kildare",
        "date_planted": "09-11-2025",
        "height": -10.5,
        "watered": True,
        "notes": "looks pretty"
    })
    assert response.status_code == 400
    data = response.get_json()


def test_update_plant_with_string_value_for_height(client):
    """test update plant with string height value"""
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    })

    response = client.put("/plants/1", json={
        "name": "Pink Rose",
        "location": "Kildare",
        "date_planted": "09-11-2025",
        "height": "tall",
        "watered": True,
        "notes": "looks pretty"
    })
    assert response.status_code == 400
    data = response.get_json()



def test_delete_plant(client):
    """test delete plant"""
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    })

    response = client.delete("/plants/1")
    assert response.status_code == 200
    data = response.get_json()


def test_delete_plant_that_doesnt_exist(client):
    """test delete plant that doesnt exist"""
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    })

    response = client.delete("/plants/100")
    assert response.status_code == 404
    data = response.get_json()


def test_delete_plant_using_string_value(client):
    """test delete plant using string value"""
    client.post("/plants", json={
        "name": "Rose",
        "location": "Dublin",
        "date_planted": "09-11-2025",
        "height": 10.5,
        "watered": True,
        "notes": "looks pretty"
    })

    response = client.delete("/plants/abc")
    assert response.status_code == 400 or 404
    data = response.get_json()



# def test_get_weather(client):
#    """test get weather"""
#    response = client.get("/weather/Dublin")
#    assert response.status_code == 200
#    data = response.get_json()


# def test_get_weather_of_a_place_that_doesnt_exist(client):
#    """test get weather of a place that doesnt exist"""
#    response = client.get("/weather/abc")
#    assert response.status_code == 404
#    data = response.get_json()



# cmd to run test
# PYTHONPATH=. pytest -v -k "test"

# TODO Test for login, register

# def test_register(client):
#     """tests POST request for adding new plant"""
#     response = client.post("/register", json={ 
#         "username": "Testuser123",


#     })
#     assert response.status_code == 201 
#     data = response.get_json() 
#     assert data["message"] == "plant added successfully"



