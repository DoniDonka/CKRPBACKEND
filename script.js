document.addEventListener('DOMContentLoaded', async () => {
  const vehicleList = document.getElementById('vehicle-list');
  const form = document.getElementById('vehicle-form');
  const discordID = localStorage.getItem('userDiscordID'); // Will be replaced with OAuth2 later
  const messageBox = document.createElement('p');
  form.parentElement.insertBefore(messageBox, form);

  // Show logged-in user
  const header = document.querySelector('h1');
  if (discordID) {
    header.innerHTML += ` <span style="font-size:0.6em;color:#888;">(Logged in as ${discordID})</span>`;
  }

  // Load vehicles
  async function loadVehicles() {
    try {
      const res = await fetch('https://ckrp-backend.onrender.com/vehicles');
      const data = await res.json();
      vehicleList.innerHTML = '';

      if (data.length === 0) {
        vehicleList.innerHTML = '<p>No vehicles listed yet.</p>';
        return;
      }

      data.forEach(vehicle => {
        const div = document.createElement('div');
        div.className = 'vehicle-card';
        div.innerHTML = `
          <div>
            <strong>${vehicle.name}</strong><br>
            Miles: ${vehicle.miles}<br>
            Condition: ${vehicle.condition}<br>
            Added by: ${vehicle.added_by}<br>
            ${vehicle.image ? `<img src="${vehicle.image}" alt="${vehicle.name}" style="max-width:200px;margin-top:5px;">` : ''}
          </div>
          ${discordID ? `<button class="delete-btn" data-id="${vehicle.id}">Delete</button>` : ''}
        `;
        vehicleList.appendChild(div);
      });

      // Add delete button listeners
      document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
          const id = btn.dataset.id;
          try {
            const res = await fetch(`https://ckrp-backend.onrender.com/vehicles/${id}?discord_id=${discordID}`, {
              method: 'DELETE'
            });
            const result = await res.json();
            messageBox.style.color = 'green';
            messageBox.textContent = result.message || 'Vehicle deleted!';
            await loadVehicles();
          } catch (err) {
            console.error('Delete error:', err);
            messageBox.style.color = 'red';
            messageBox.textContent = 'Failed to delete vehicle.';
          }
        });
      });

    } catch (err) {
      console.error('Error loading vehicles:', err);
      vehicleList.innerHTML = '<p style="color:red;">Failed to load vehicles.</p>';
    }
  }

  await loadVehicles();

  // Check whitelist
  async function checkWhitelist(id) {
    if (!id) return false;
    try {
      const res = await fetch(`https://ckrp-backend.onrender.com/is-whitelisted/${id}`);
      const result = await res.json();
      return result.allowed === true;
    } catch {
      return false;
    }
  }

  // Show form only for admins
  if (discordID && await checkWhitelist(discordID)) {
    form.style.display = 'block';
  } else {
    form.style.display = 'none';
    messageBox.style.color = 'red';
    messageBox.textContent = discordID ? 'You are not authorized to add vehicles.' : 'Log in to add vehicles.';
  }

  // Submit new vehicle
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const vehicle = {
      name: document.getElementById('name').value.trim(),
      miles: parseInt(document.getElementById('miles').value),
      condition: document.getElementById('condition').value.trim(),
      image: document.getElementById('image').value.trim(),
      added_by: discordID
    };

    try {
      const res = await fetch('https://ckrp-backend.onrender.com/vehicles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(vehicle)
      });
      const result = await res.json();
      if (res.ok) {
        messageBox.style.color = 'green';
        messageBox.textContent = 'Vehicle added successfully!';
        form.reset();
        await loadVehicles();
      } else {
        messageBox.style.color = 'red';
        messageBox.textContent = result.detail || 'Failed to add vehicle.';
      }
    } catch (err) {
      console.error('Submit error:', err);
      messageBox.style.color = 'red';
      messageBox.textContent = 'Failed to submit vehicle.';
    }
  });
});
