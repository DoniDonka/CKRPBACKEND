from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os

app = FastAPI()

# ✅ Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Data file and whitelist
DATA_FILE = "vehicles.json"
WHITELIST = [
    "329997541523587073",  # Doni
    "1287198545539104780"  # Second person
]

# ✅ Vehicle model
class Vehicle(BaseModel):
    name: str
    miles: int
    condition: str
    in_stock: bool = True
    image: str = ""
    added_by: str

# ✅ Load vehicles from file
def load_vehicles():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# ✅ Save vehicles to file
def save_vehicles(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ✅ Get all vehicles
@app.get("/vehicles")
def get_vehicles():
    return load_vehicles()

# ✅ Add a vehicle (only if whitelisted)
@app.post("/vehicles")
def add_vehicle(vehicle: Vehicle):
    if vehicle.added_by not in WHITELIST:
        return {"error": "Unauthorized Discord ID"}
    data = load_vehicles()
    data.append(vehicle.dict())
    save_vehicles(data)
    return {"message": "Vehicle added successfully"}

# ✅ Check if Discord ID is whitelisted
@app.get("/is-whitelisted/{discord_id}")
def is_whitelisted(discord_id: str):
    return { "allowed": discord_id in WHITELIST }