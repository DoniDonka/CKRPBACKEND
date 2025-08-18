// ✅ Whitelisted Discord IDs
const allowedIDs = [
  "329997541523587073", // Replace with real Discord IDs
  "1287198545539104780"
];

// ✅ Backend API base (Render)
const API_BASE = 'https://ckrp-backend.onrender.com';

// ✅ Load vehicles from backend
async function loadVehicles() {
  try {
    const res = await fetch(`${API_BASE}/vehicles`);
    const vehicles = await res.json();
    const list = document.getElementById('vehicle-list');
    list.innerHTML = '';

    if (vehicles.length === 0) {
      list.innerHTML = '<p>No vehicles yet.</p>';
      return;
    }

    vehicles.forEach(v => {
      list.innerHTML += `
        <div class="vehicle">
          <strong>${v.name}</strong><br>
          Miles: ${v.miles}<br>
          Condition: ${v.condition}<br>
          Added by: ${v.added_by}<br>
          ${v.image ? `<img src="${v.image}" alt="Vehicle Image">` : ''}
        </div>
      `;
    });
  } catch (err) {
    console.error('Failed to load vehicles:', err);
    document.getElementById('vehicle-list').innerHTML = '<p>Error loading vehicles.</p>';
  }
}

// ✅ Handle form submission
document.getElementById('vehicle-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const discordID = document.getElementById('added_by').value.trim();
  if (!allowedIDs.includes(discordID)) {
    alert("You are not authorized to add vehicles.");
    return;
  }

  const vehicle = {
    name: document.getElementById('name').value,
    miles: parseInt(document.getElementById('miles').value),
    condition: document.getElementById('condition').value,
    image: document.getElementById('image').value,
    added_by: discordID
  };

  try {
    const res = await fetch(`${API_BASE}/vehicles`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(vehicle)
    });

    if (!res.ok) {
      throw new Error('Failed to add vehicle');
    }

    await loadVehicles();
    e.target.reset();
  } catch (err) {
    console.error('Error adding vehicle:', err);
    alert('Failed to add vehicle. Please try again.');
  }
});

// ✅ Initial load
loadVehicles();