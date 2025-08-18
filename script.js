// ✅ Whitelisted Discord IDs
const allowedIDs = [
  "329997541523587073", // Replace with real Discord IDs
  "1287198545539104780"
];

// ✅ Load vehicles from localStorage
function loadVehicles() {
  const vehicles = JSON.parse(localStorage.getItem('vehicles') || '[]');
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
        ${v.image ? `<img src="${v.image}">` : ''}
      </div>
    `;
  });
}

// ✅ Handle form submission
document.getElementById('vehicle-form').addEventListener('submit', (e) => {
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

  const vehicles = JSON.parse(localStorage.getItem('vehicles') || '[]');
  vehicles.push(vehicle);
  localStorage.setItem('vehicles', JSON.stringify(vehicles));
  loadVehicles();
  e.target.reset();
});

loadVehicles();