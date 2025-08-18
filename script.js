document.addEventListener('DOMContentLoaded', async () => {
  const vehicleList = document.getElementById('vehicle-list');
  const form = document.getElementById('vehicle-form');
  const addedByInput = document.getElementById('added_by');
  const discordID = localStorage.getItem('userDiscordID');

  // ✅ Show logged-in user
  const header = document.querySelector('h1');
  if (discordID) {
    header.innerHTML += ` <span style="font-size:0.6em;color:#888;">(Logged in as ${discordID})</span>`;
  }

  // ✅ Load vehicles for everyone
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
          ${vehicle.image ? `<img src="${vehicle.image}" alt="${vehicle.name}" style="max-width:200px;">` : ''}
        `;
        vehicleList.appendChild(div);
      });
    } catch (err) {
      console.error('Error loading vehicles:', err);
      vehicleList.innerHTML = '<p style="color:red;">Failed to load vehicles.</p>';
    }
  }

  await loadVehicles();

  // ✅ Check whitelist via backend
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

  // ✅ Form visibility logic
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

  // ✅ Submit form
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const vehicle = {
      name: document.getElementById('name').value.trim(),
      miles: parseInt(document.getElementById('miles').value),
      condition: document.getElementById('condition').value.trim(),
      image: document.getElementById('image').value.trim(),
      added_by: discordID
    };

    console.log('Submitting vehicle:', vehicle);

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
        await loadVehicles(); // Reload without full page refresh
      } else {
        alert(`Error: ${result.detail || 'Failed to add vehicle.'}`);
      }
    } catch (err) {
      console.error('Submission error:', err);
      alert('Failed to submit vehicle. Check console for details.');
    }
  });
});