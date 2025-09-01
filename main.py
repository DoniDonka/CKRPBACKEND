from fastapi import FastAPI, Request, HTTPException
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
DATA_FILE = "blacklist.json"
WHITELIST = [
    "329997541523587073",  # Doni
    "1287198545539104780",  # Second person
    "1094486136283467847",  # Added
    "898599688918405181"   # Added
]

# ✅ Blacklist entry model (same form fields, renamed)
class BlacklistEntry(BaseModel):
    name: str               # Username
    miles: int              # Danger level
    condition: str          # Reason
    in_stock: bool = True   # Optional flag (can be ignored)
    image: str = ""         # Player image URL
    added_by: str           # Submitter Discord ID

# ✅ Load blacklist from file
def load_blacklist():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# ✅ Save blacklist to file
def save_blacklist(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ✅ Get all blacklist entries
@app.get("/blacklist")
def get_blacklist():
    return load_blacklist()

# ✅ Add a blacklist entry (only if whitelisted)
@app.post("/blacklist")
def add_blacklist_entry(entry: BlacklistEntry):
    if entry.added_by not in WHITELIST:
        return {"error": "Unauthorized Discord ID"}
    data = load_blacklist()
    data.append(entry.dict())
    save_blacklist(data)
    return {"message": "Player blacklisted successfully"}

# ✅ Check if Discord ID is whitelisted
@app.get("/is-whitelisted/{discord_id}")
def is_whitelisted(discord_id: str):
    return { "allowed": discord_id in WHITELIST }

# ✅ Delete blacklist entry by index (admin only)
@app.delete("/blacklist/{index}")
def delete_blacklist_entry(index: int, request: Request):
    discord_id = request.query_params.get("discord_id")
    if discord_id not in WHITELIST:
        raise HTTPException(status_code=403, detail="Unauthorized")

    data = load_blacklist()
    if index < 0 or index >= len(data):
        raise HTTPException(status_code=404, detail="Entry not found")

    deleted = data.pop(index)
    save_blacklist(data)
    return {"message": "Blacklist entry deleted", "deleted": deleted}

