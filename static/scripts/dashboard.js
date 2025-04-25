function toggleDropdown() {
    const dropdown = document.getElementById('user-dropdown');
    dropdown.classList.toggle('hidden');
}

// This closes the dropdown when clicking outside
document.addEventListener('click', function (event) {
    const dropdown = document.getElementById('user-dropdown');
    const userProfile = document.querySelector('.user-profile');
    if (!userProfile.contains(event.target) && !dropdown.contains(event.target)) {
        dropdown.classList.add('hidden');
    }
});

function toggleProfileCard() {
    const profileCard = document.getElementById('profile-card');
    profileCard.classList.toggle('hidden');
}

function closeProfileCard() {
    const profileCard = document.getElementById('profile-card');
    profileCard.classList.add('hidden');
}

// Utility: Hide the add client card
function hideCard() {
    document.getElementById("addClientCard").style.display = "none";
}

// Utility: Show the add client modal
function showAddClientModal() {
    document.getElementById('addClientModal').classList.add('show');
}

// Utility: Show the add program modal
function showAddProgramModal() {
    window.location.href = "/add-program";
}

// Utility: Show search results container
function showSearchResults() {
    document.getElementById('search-results').classList.add('show');
}


// Utility: Close modal by ID
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
}
function searchClients() {
    const query = document.getElementById('client-search-input').value.trim();
    const clientList = document.getElementById('client-list');
    const clientResultSection = document.getElementById('client-result');
    const noClientCard = document.getElementById('no-client-card');
    const searchResults = document.getElementById('search-results');

    clientList.innerHTML = '';
    clientResultSection.classList.add('hidden');
    noClientCard.classList.add('d-none');

    if (query !== "") {
        fetch(`/search/clients?query=${query}`)
            .then(response => response.json())
            .then(data => {
                if (data.clients.length > 0) {
                    let tableHTML = `
                        <thead>
                            <tr><th>ID</th><th>Name</th><th>Email</th><th>National ID</th></tr>
                        </thead>
                        <tbody>
                    `;

                    tableHTML += data.clients.map(client => `
                        <tr class="clickable-row" onclick="window.location.href='/client/${client.id}'">
                            <td>${client.id}</td>
                            <td>${client.first_name} ${client.last_name}</td>
                            <td>${client.email}</td>
                            <td>${client.national_id}</td>
                        </tr>
                    `).join('');

                    tableHTML += '</tbody>';
                    clientList.innerHTML = tableHTML;

                    clientResultSection.classList.remove('hidden');
                    searchResults.classList.remove('hidden');
                } else {
                    noClientCard.classList.remove('d-none');
                    clientResultSection.classList.remove('hidden');
                    searchResults.classList.remove('hidden');
                }
            })
            .catch(error => console.error('Error fetching clients:', error));
    } else {
        searchResults.classList.add('hidden');
    }
}

function searchPrograms() {
    const query = document.getElementById('program-search-input').value.trim();
    const programList = document.getElementById('program-list');
    const programResultSection = document.getElementById('program-result');
    const noProgramCard = document.getElementById('no-program-card');
    const searchResults = document.getElementById('search-results');

    programList.innerHTML = '';
    programResultSection.classList.add('hidden');
    noProgramCard.classList.add('d-none');

    if (query !== "") {
        fetch(`/search/programs?query=${query}`)
            .then(response => response.json())
            .then(data => {
                if (data.programs.length > 0) {
                    let tableHTML = `
                        <thead>
                            <tr><th>ID</th><th>Name</th><th>Description</th></tr>
                        </thead>
                        <tbody>
                    `;

                    tableHTML += data.programs.map(program => `
                        <tr class="clickable-row" onclick="window.location.href='/program/${program.id}'">
                            <td>${program.id}</td>
                            <td>${program.name}</td>
                            <td>${program.description}</td>
                        </tr>
                    `).join('');

                    tableHTML += '</tbody>';
                    programList.innerHTML = tableHTML;

                    programResultSection.classList.remove('hidden');
                    searchResults.classList.remove('hidden');
                } else {
                    noProgramCard.classList.remove('d-none');
                    programResultSection.classList.remove('hidden');
                    searchResults.classList.remove('hidden');
                }
            })
            .catch(error => console.error('Error fetching programs:', error));
    } else {
        searchResults.classList.add('hidden');
    }
}


// Navigation and modal handling
document.addEventListener('DOMContentLoaded', function () {
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    const sections = document.querySelectorAll('.content-section');
    navLinks.forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            sections.forEach(section => section.classList.add('hidden'));
            document.getElementById(targetId).classList.remove('hidden');
            navLinks.forEach(navLink => navLink.parentElement.classList.remove('active'));
            link.parentElement.classList.add('active');
        });
    });

    const modals = document.querySelectorAll('.modal');
    const closeButtons = document.querySelectorAll('.close-modal');
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            button.closest('.modal').classList.remove('show');
        });
    });
    modals.forEach(modal => {
        modal.addEventListener('click', e => {
            if (e.target === modal) modal.classList.remove('show');
        });
    });

    const userProfile = document.querySelector('.user-profile');
    if (userProfile) {
        userProfile.addEventListener('click', () => console.log('Toggle user menu'));
    }

    const notificationsButton = document.querySelector('.notifications');
    if (notificationsButton) {
        notificationsButton.addEventListener('click', () => console.log('Toggle notifications'));
    }
});

// Client info fetch on National ID input
document.getElementById('national_id').addEventListener('input', function () {
    const nationalId = this.value;
    if (nationalId) {
        getClientInfo(nationalId);
    } else {
        document.getElementById('client-info-card').style.display = 'none';
    }
});

function getClientInfo(nationalId) {
    console.log("Fetching client info...");
    fetch(`/client_info/${nationalId}`)
        .then(response => response.json())
        .then(data => {
            if (data.client) {
                const { first_name, last_name, date_of_birth, gender, email, phoneNumber } = data.client;
                document.getElementById('client-name').innerText = `${first_name} ${last_name}`;
                document.getElementById('client-dob').innerHTML = `<strong>Date of Birth:</strong> ${date_of_birth}`;
                document.getElementById('client-gender').innerHTML = `<strong>Gender:</strong> ${gender}`;
                document.getElementById('client-email').innerHTML = `<strong>Email:</strong> ${email}`;
                document.getElementById('client-phone').innerHTML = `<strong>Contact:</strong> ${phoneNumber}`;
                const card = document.getElementById('client-info-card');
                card.style.display = 'block';
                card.classList.add('fadeIn');
            } else {
                document.getElementById('client-info-card').style.display = 'none';
                alert('Client not found.');
            }
        })
        .catch(() => alert('Error fetching client info.'));
}


function editProgram(programId) {
    console.log('Editing program:', programId);
    alert(`Editing program: ${programId}`);
}
