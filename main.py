from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uuid

app = FastAPI()

# In-memory vehicle store
vehicles = []

# Vehicle model
class Vehicle(BaseModel):
    model: str
    owner_id: str  # Discord ID or user identifier

@app.get("/api/ping")
def ping():
    return {"status": "awake"}

@app.get("/api/vehicles", response_model=List[Vehicle])
def get_vehicles():
    return vehicles

@app.post("/api/vehicles")
def add_vehicle(vehicle: Vehicle):
    vehicle_entry = vehicle.dict()
    vehicle_entry["id"] = str(uuid.uuid4())
    vehicles.append(vehicle_entry)
    return {"message": "Vehicle added", "vehicle": vehicle_entry}

@app.delete("/api/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: str):
    global vehicles
    for v in vehicles:
        if v.get("id") == vehicle_id:
            vehicles = [veh for veh in vehicles if veh.get("id") != vehicle_id]
            return {"message": "Vehicle deleted"}
    raise HTTPException(status_code=404, detail="Vehicle not found")