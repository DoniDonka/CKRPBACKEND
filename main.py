from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from uuid import uuid4

app = FastAPI()

# CORS so your GitHub Pages frontend can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["https://donidonka.github.io"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Blacklist entry model
class BlacklistEntry(BaseModel):
    id: str
    target: str       # Player being blacklisted
    username: str     # Who added them
    reason: str       # Why they were blacklisted

# In-memory "database"
blacklist_db: List[BlacklistEntry] = []

# GET all blacklist entries
@app.get("/blacklist", response_model=List[BlacklistEntry])
async def get_blacklist():
    return blacklist_db

# POST a new blacklist entry
class BlacklistEntryCreate(BaseModel):
    target: str
    username: str
    reason: str

@app.post("/blacklist", response_model=BlacklistEntry)
async def add_blacklist(entry: BlacklistEntryCreate):
    if not entry.target or not entry.username or not entry.reason:
        raise HTTPException(status_code=400, detail="All fields are required.")

    new_entry = BlacklistEntry(
        id=str(uuid4()),
        target=entry.target,
        username=entry.username,
        reason=entry.reason
    )
    blacklist_db.append(new_entry)
    return new_entry

# DELETE a blacklist entry by ID
@app.delete("/blacklist/{entry_id}")
async def delete_blacklist(entry_id: str):
    global blacklist_db
    for e in blacklist_db:
        if e.id == entry_id:
            blacklist_db = [entry for entry in blacklist_db if entry.id != entry_id]
            return {"success": True}
    raise HTTPException(status_code=404, detail="Entry not found")
