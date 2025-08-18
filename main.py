from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "vehicles.json"
WHITELIST = ["329997541523587073", "1287198545539104780"]  # Replace with real Discord IDs

class Vehicle(BaseModel):
    name: str
    miles: int
    condition: str
    in_stock: bool = True
    image: str = ""
    added_by: str

def load_vehicles():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_vehicles(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.get("/vehicles")
def get_vehicles():
    return load_vehicles()

@app.post("/vehicles")
def add_vehicle(vehicle: Vehicle):
    if vehicle.added_by not in WHITELIST:
        return {"error": "Unauthorized Discord ID"}
    data = load_vehicles()
    data.append(vehicle.dict())
    save_vehicles(data)
    return {"message": "Vehicle added successfully"}