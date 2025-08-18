document.addEventListener('DOMContentLoaded', async () => {
  const vehicleList = document.getElementById('vehicle-list');
  const form = document.getElementById('vehicle-form');
  const addedByInput = document.getElementById('added_by');

  // Get Discord ID from localStorage (after login)
  const discordID = localStorage.getItem('userDiscordID');

  // Show logged-in user in header
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
        div.className = 'vehicle';
        div.innerHTML = `
          <h3>${vehicle.name}</h3>
          <p>Miles: ${vehicle.miles}</p>
          <p>Condition: ${vehicle.condition}</p>
          <p>Added by: ${vehicle.added_by}</p>
          ${vehicle.image ? `<img src="${vehicle.image}" alt="${vehicle.name}">` : ''}
          ${discordID && vehicle.added_by === discordID ? `<button class="delete-btn" data-id="${vehicle.id}">Delete</button>` : ''}
        `;
        vehicleList.appendChild(div);
      });

      // Add delete button listeners
      document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
          const id = btn.dataset.id;
          try {
            const res = await fetch(`https://ckrp-backend.onrender.com/vehicles/${id}?discord_id=${discordID}`, { method: 'DELETE' });
            const result = await res.json();
            alert(result.message || 'Deleted');
            loadVehicles();
          } catch (err) {
            console.error('Delete error:', err);
          }
        });
      });

    } catch (err) {
      console.error('Error loading vehicles:', err);
      vehicleList.innerHTML = '<p style="color:red;">Failed to load vehicles.</p>';
    }
  }

  await loadVehicles();

  // Check whitelist via backend
  async function checkWhitelist(id) {
    try {
      const res = await fetch(`https://ckrp-backend.onrender.com/is-whitelisted/${id}`);
      const result = await res.json();
      return result.allowed === true;
    } catch (err) {
      console.error('Whitelist check failed:', err);
      return false;
    }
  }

  // Show form only if whitelisted
  if (discordID) {
    const isAllowed = await checkWhitelist(discordID);
    if (isAllowed) {
      addedByInput.value = discordID;
      form.style.display = 'block';
    } else {
      form.style.display = 'none';
      const msg = document.createElement('p');
      msg.style.color = 'red';
      msg.textContent = 'You are not authorized to add vehicles.';
      form.parentElement.insertBefore(msg, form);
    }
  } else {
    form.style.display = 'none';
    const msg = document.createElement('p');
    msg.style.color = 'red';
    msg.textContent = 'Log in to add vehicles.';
    form.parentElement.insertBefore(msg, form);
  }

  // Submit form
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
        alert('Vehicle added successfully!');
        form.reset();
        loadVehicles(); // reload without refreshing the page
      } else {
        alert(`Error: ${result.detail || 'Failed to add vehicle.'}`);
      }
    } catch (err) {
      console.error('Submission error:', err);
      alert('Failed to submit vehicle. Check console for details.');
    }
  });
});
