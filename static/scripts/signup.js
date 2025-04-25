
async function loadTerms() {
    try {
        const response = await fetch('/static/terms.json');
        const terms = await response.json();
        const container = document.getElementById('termsBody');
        container.innerHTML = ''; // Clear existing content

        terms.forEach(section => {
            const title = document.createElement('h6');
            title.classList.add('mb-3', 'mt-4');
            title.textContent = section.title;
            container.appendChild(title);

            const paragraph = document.createElement('p');
            paragraph.textContent = section.content;
            container.appendChild(paragraph);

            if (section.list) {
                const ul = document.createElement('ul');
                section.list.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = item;
                    ul.appendChild(li);
                });
                container.appendChild(ul);
            }
        });
    } catch (error) {
        console.error('Failed to load terms:', error);
    }
}

// Load terms when modal is shown
document.getElementById('termsModal').addEventListener('show.bs.modal', loadTerms);
