from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import json, os, uuid, httpx

# ----------------------------
# CONFIGURATION
# ----------------------------
CLIENT_ID = "1407023428699033721"          # Replace with your Discord app ID
CLIENT_SECRET = "YDPcE6cX9XcqvXs6EQ6zAJTbMhva3WjU"  # Replace with your Discord app secret
REDIRECT_URI = "https://ckrp-backend.onrender.com/oauth/callback"
SCOPES = "identify"
WHITELIST = [
    "329997541523587073",
    "1287198545539104780"
]
DATA_FILE = "vehicles.json"
COOKIE_NAME = "discord_user"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# ----------------------------
# MODELS
# ----------------------------
class Vehicle(BaseModel):
    name: str
    miles: int
    condition: str
    in_stock: bool = True
    image: str = ""

# ----------------------------
# HELPERS
# ----------------------------
def load_vehicles():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_vehicles(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_discord_id(request: Request):
    discord_id = request.cookies.get(COOKIE_NAME)
    if not discord_id:
        raise HTTPException(status_code=401, detail="Not logged in")
    return discord_id

# ----------------------------
# OAUTH2 LOGIN
# ----------------------------
@app.get("/login")
def login():
    url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        f"&response_type=code&scope={SCOPES}"
    )
    return RedirectResponse(url)

@app.get("/oauth/callback")
async def oauth_callback(code: str):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient() as client:
        token_res = await client.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
        token_json = token_res.json()
        access_token = token_json.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="OAuth2 token failed")
        
        user_res = await client.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        discord_id = user_res.json().get("id")

    response = RedirectResponse("/marketplace")
    response.set_cookie(key=COOKIE_NAME, value=discord_id, httponly=True, samesite="lax")
    return response

# ----------------------------
# VEHICLE ENDPOINTS
# ----------------------------
@app.get("/vehicles")
def get_vehicles(in_stock: bool = None):
    data = load_vehicles()
    if in_stock is not None:
        data = [v for v in data if v.get("in_stock") == in_stock]
    return data

@app.post("/vehicles")
def add_vehicle(vehicle: Vehicle, discord_id: str = Depends(get_discord_id)):
    if discord_id not in WHITELIST:
        raise HTTPException(status_code=403, detail="Not authorized")
    data = load_vehicles()
    vehicle_dict = vehicle.dict()
    vehicle_dict["id"] = str(uuid.uuid4())
    vehicle_dict["added_by"] = discord_id
    data.append(vehicle_dict)
    save_vehicles(data)
    return {"message": "Vehicle added", "id": vehicle_dict["id"]}

@app.delete("/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: str, discord_id: str = Depends(get_discord_id)):
    if discord_id not in WHITELIST:
        raise HTTPException(status_code=403, detail="Not authorized")
    data = load_vehicles()
    updated = [v for v in data if v.get("id") != vehicle_id]
    save_vehicles(updated)
    return {"message": "Vehicle deleted"}

@app.get("/is-whitelisted")
def is_whitelisted(discord_id: str = Depends(get_discord_id)):
    return {"allowed": discord_id in WHITELIST}

# ----------------------------
# FRONTEND
# ----------------------------
@app.get("/marketplace", response_class=HTMLResponse)
def marketplace():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CK:RP Vehicle Marketplace</title>
<style>
body { font-family: Arial, sans-serif; background: #121212; color: #fff; margin: 0; padding: 20px; }
.container { max-width: 900px; margin: auto; }
.vehicle-card { background: #1e1e1e; padding: 15px; margin: 10px 0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
.vehicle-card img { max-width: 200px; margin-left: 10px; border-radius: 4px; }
button { background: #007bff; color: #fff; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; }
button:hover { background: #0056b3; }
form { display: flex; flex-direction: column; gap: 10px; background: #1e1e1e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
input, select { padding: 8px; border-radius: 4px; border: none; }
.message-box { margin-bottom: 10px; font-weight: bold; }
#loginBtn { background: #7289da; margin-bottom: 20px; }
#loginBtn:hover { background: #5b6eae; }
</style>
</head>
<body>
<div class="container">
  <h1>CK:RP Vehicle Marketplace</h1>
  <button id="loginBtn">Login with Discord</button>
  <p class="message-box" id="messageBox"></p>

  <div id="adminFormContainer" style="display:none;">
    <h2>Add Vehicle</h2>
    <form id="vehicleForm">
      <input type="text" id="name" placeholder="Vehicle Name" required>
      <input type="number" id="miles" placeholder="Miles" required>
      <select id="condition">
        <option value="New">New</option>
        <option value="Like New">Like New</option>
        <option value="Used">Used</option>
      </select>
      <input type="text" id="image" placeholder="Image URL">
      <button type="submit">Add Vehicle</button>
    </form>
  </div>

  <h2>Vehicles</h2>
  <div id="vehicleList"></div>
</div>

<script>
document.addEventListener('DOMContentLoaded', async () => {
  const vehicleList = document.getElementById('vehicleList');
  const form = document.getElementById('vehicleForm');
  const adminFormContainer = document.getElementById('adminFormContainer');
  const messageBox = document.getElementById('messageBox');
  const loginBtn = document.getElementById('loginBtn');

  // Check if user is admin
  async function checkAdmin() {
    try {
      const res = await fetch('/is-whitelisted');
      const result = await res.json();
      return result.allowed;
    } catch { return false; }
  }

  const isAdmin = await checkAdmin();
  if (isAdmin) {
    loginBtn.style.display = 'none';
    messageBox.textContent = "Logged in as authorized admin";
    adminFormContainer.style.display = 'block';
  } else {
    loginBtn.style.display = 'block';
    messageBox.textContent = "Log in to add vehicles";
  }

  loginBtn.addEventListener('click', () => window.location.href = '/login');

  // Load vehicles
  async function loadVehicles() {
    const res = await fetch('/vehicles');
    const vehicles = await res.json();
    vehicleList.innerHTML = '';
    vehicles.forEach(v => {
      const div = document.createElement('div');
      div.className = 'vehicle-card';
      div.innerHTML = `
        <div>
          <strong>${v.name}</strong><br>
          Miles: ${v.miles}<br>
          Condition: ${v.condition}<br>
          Added by: ${v.added_by}
        </div>
        ${v.image ? `<img src="${v.image}" alt="${v.name}">` : ''}
        ${isAdmin ? `<button class="delete-btn" data-id="${v.id}">Delete</button>` : ''}
      `;
      vehicleList.appendChild(div);
    });

    document.querySelectorAll('.delete-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.id;
        const res = await fetch(`/vehicles/${id}`, { method: 'DELETE' });
        const result = await res.json();
        messageBox.textContent = result.message || 'Deleted';
        await loadVehicles();
      });
    });
  }

  await loadVehicles();

  // Submit vehicle
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const vehicle = {
      name: document.getElementById('name').value.trim(),
      miles: parseInt(document.getElementById('miles').value),
      condition: document.getElementById('condition').value.trim(),
      image: document.getElementById('image').value.trim()
    };
    const res = await fetch('/vehicles', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(vehicle)
    });
    const result = await res.json();
    messageBox.textContent = result.message || 'Added';
    form.reset();
    await loadVehicles();
  });
});
</script>
</body>
</html>
"""
