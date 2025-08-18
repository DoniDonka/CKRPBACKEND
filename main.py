from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import uuid

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

# ✅ Get all vehicles (optional filter)
@app.get("/vehicles")
def get_vehicles(in_stock: bool = None):
    data = load_vehicles()
    if in_stock is not None:
        data = [v for v in data if v.get("in_stock") == in_stock]
    return data

# ✅ Add a vehicle (only if whitelisted)
@app.post("/vehicles")
def add_vehicle(vehicle: Vehicle):
    if vehicle.added_by not in WHITELIST:
        return {"error": "Unauthorized Discord ID"}
    data = load_vehicles()
    vehicle_dict = vehicle.dict()
    vehicle_dict["id"] = str(uuid.uuid4())
    data.append(vehicle_dict)
    save_vehicles(data)
    return {"message": "Vehicle added", "id": vehicle_dict["id"]}

# ✅ Delete a vehicle (admin-only)
@app.delete("/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: str, request: Request):
    discord_id = request.query_params.get("discord_id")
    if discord_id not in WHITELIST:
        return {"error": "Unauthorized"}
    data = load_vehicles()
    updated = [v for v in data if v.get("id") != vehicle_id]
    save_vehicles(updated)
    return {"message": "Vehicle deleted"}

# ✅ Check if Discord ID is whitelisted
@app.get("/is-whitelisted/{discord_id}")
def is_whitelisted(discord_id: str):
    return { "allowed": discord_id in WHITELIST }