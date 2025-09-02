document.addEventListener('DOMContentLoaded', async () => {
    const entryList = document.getElementById('vehicle-list');
    const form = document.getElementById('vehicle-form');
    const usernameInput = document.getElementById('added_by');
    const reasonInput = document.getElementById('reason');
    const BASE_URL = 'https://ckrp.example.com/vehicles'; // Replace with your actual backend URL
    const discordID = localStorage.getItem('userDiscordID') || '';

    // Populate the "added_by" field automatically
    usernameInput.value = discordID;

    // Helper: create a vehicle list item
    function createVehicleItem(vehicle) {
        const li = document.createElement('li');
        li.dataset.id = vehicle.id;
        li.textContent = `ID: ${vehicle.id} | Model: ${vehicle.model} | Added by: ${vehicle.username} | Reason: ${vehicle.reason}`;

        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.style.marginLeft = '10px';
        deleteBtn.addEventListener('click', async () => {
            try {
                const res = await fetch(`${BASE_URL}/${vehicle.id}`, { method: 'DELETE' });
                if (res.ok) {
                    li.remove();
                } else {
                    alert('Failed to delete vehicle');
                }
            } catch (err) {
                console.error(err);
                alert('Error deleting vehicle');
            }
        });

        li.appendChild(deleteBtn);
        return li;
    }

    // Fetch and display vehicles
    async function loadVehicles() {
        entryList.innerHTML = '';
        try {
            const res = await fetch(BASE_URL);
            if (!res.ok) throw new Error('Failed to fetch vehicles');
            const vehicles = await res.json();
            vehicles.forEach(vehicle => {
                entryList.appendChild(createVehicleItem(vehicle));
            });
        } catch (err) {
            console.error(err);
            entryList.textContent = 'Error loading vehicles.';
        }
    }

    await loadVehicles();

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            username: usernameInput.value.trim(),
            reason: reasonInput.value.trim(),
            model: form.model.value.trim()
        };

        if (!data.username || !data.model || !data.reason) {
            alert('Please fill all fields.');
            return;
        }

        try {
            const res = await fetch(BASE_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!res.ok) throw new Error('Failed to add vehicle');

            const newVehicle = await res.json();
            entryList.appendChild(createVehicleItem(newVehicle));
            form.reset();
            usernameInput.value = discordID; // Keep the discordID filled
        } catch (err) {
            console.error(err);
            alert('Error adding vehicle.');
        }
    });
});
