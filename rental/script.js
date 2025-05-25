// Search functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('input[type="text"]');
    const searchButton = document.querySelector('button i.fa-search').parentElement;
    const browseEquipmentButton = document.getElementById('browseEquipment');

    // Browse Equipment button functionality
    if (browseEquipmentButton) {
        browseEquipmentButton.addEventListener('click', function() {
            // Scroll to categories section
            document.getElementById('categories').scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        });
    }

    searchButton.addEventListener('click', function() {
        performSearch(searchInput.value);
    });

    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch(searchInput.value);
        }
    });

    function performSearch(query) {
        // Remove any previous 'no results' message
        document.querySelectorAll('.no-results-message').forEach(el => el.remove());

        if (!query.trim()) {
            // If search is cleared, show all equipment sections and cards
            document.querySelectorAll('.equipment-section').forEach(section => {
                section.classList.add('hidden');
            });
            // Optionally, show categories section or reset UI
            return;
        }

        query = query.toLowerCase();

        const categoryMap = {
            'heavy': 'heavy-section',
            'heavy machinery': 'heavy-section',
            'light': 'light-section',
            'light machinery': 'light-section',
            'tools': 'tools-section',
            'tools & accessories': 'tools-section',
            'vehicles': 'vehicles-section',
            'vehicle': 'vehicles-section'
        };

        let foundItems = [];
        let foundCategories = new Set();
        let categoryMatched = false;

        // Check if the query matches a category
        for (const [keyword, sectionId] of Object.entries(categoryMap)) {
            if (query === keyword || query.includes(keyword)) {
                const section = document.getElementById(sectionId);
                if (section) {
                    const cards = section.querySelectorAll('.bg-white.rounded-lg.shadow-md');
                    cards.forEach(card => foundItems.push(card));
                    foundCategories.add(sectionId.replace('-section', ''));
                    categoryMatched = true;
                }
            }
        }

        // If not a category match, search through each equipment card
        if (!categoryMatched) {
            const equipmentCards = document.querySelectorAll('.equipment-section .bg-white.rounded-lg.shadow-md');
            equipmentCards.forEach(card => {
                const title = card.querySelector('h3').textContent.toLowerCase();
                const description = card.querySelector('p').textContent.toLowerCase();
                const category = card.closest('.equipment-section').id.replace('-section', '');
                if (title.includes(query) || description.includes(query)) {
                    foundItems.push(card);
                    foundCategories.add(category);
                }
            });
        }

        // Hide all equipment sections first
        document.querySelectorAll('.equipment-section').forEach(section => {
            section.classList.add('hidden');
        });

        // Hide all cards first
        document.querySelectorAll('.equipment-section .bg-white.rounded-lg.shadow-md').forEach(card => {
            card.style.display = 'none';
        });

        if (foundItems.length > 0) {
            // Show only the relevant section(s) and cards
            foundCategories.forEach(category => {
                const section = document.getElementById(`${category}-section`);
                if (section) {
                    section.classList.remove('hidden');
                }
            });
            foundItems.forEach(card => {
                card.style.display = '';
                card.style.backgroundColor = '#f0fdf4';
                card.style.border = '2px solid #22c55e';
                setTimeout(() => {
                    card.style.backgroundColor = '';
                    card.style.border = '';
                }, 2000);
            });
        } else {
            // Show the first section and display a no results message
            const firstSection = document.querySelector('.equipment-section');
            if (firstSection) {
                firstSection.classList.remove('hidden');
                const noResults = document.createElement('div');
                noResults.className = 'no-results-message text-center text-gray-500 py-8';
                noResults.textContent = 'No equipment found matching your search.';
                firstSection.querySelector('.grid')?.appendChild(noResults);
            }
        }
    }

    // Navigation and section handling
    function showSection(sectionId) {
        // Hide all sections first
        document.querySelectorAll('.equipment-section').forEach(section => {
            section.classList.add('hidden');
        });

        // Show the selected section
        const selectedSection = document.getElementById(sectionId);
        if (selectedSection) {
            selectedSection.classList.remove('hidden');
            
            // Smooth scroll to the section
            selectedSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });

            // Update active state of category cards
            document.querySelectorAll('.category-card').forEach(card => {
                card.classList.remove('bg-green-50', 'border-2', 'border-green-600');
                if (card.getAttribute('data-category') === sectionId.replace('-section', '')) {
                    card.classList.add('bg-green-50', 'border-2', 'border-green-600');
                }
            });
        }
    }

    // Handle navigation links
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            
            if (targetId === 'categories') {
                // Scroll to categories section
                document.getElementById('categories').scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            } else if (targetId === 'about' || targetId === 'contact') {
                // Scroll to about or contact section
                document.getElementById(targetId).scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            } else if (targetId.endsWith('-section')) {
                // Show the selected equipment section
                showSection(targetId);
            }
        });
    });

    // Handle contact form submission
    const contactForm = document.querySelector('#contact form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const formObject = {};
            formData.forEach((value, key) => {
                formObject[key] = value;
            });

            // Here you would typically send the form data to a server
            console.log('Form submitted:', formObject);
            
            // Show success message
            alert('Thank you for your message! We will get back to you soon.');
            
            // Reset form
            this.reset();
        });
    }

    // Category click functionality
    const categoryCards = document.querySelectorAll('.category-card');
    categoryCards.forEach(card => {
        card.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            showSection(`${category}-section`);
        });
    });

    // Add hover effects to equipment cards
    const equipmentCards = document.querySelectorAll('.bg-white.rounded-lg.shadow-md');
    equipmentCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.3s ease';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add click handlers for "Rent Now" buttons
    const rentButtons = document.querySelectorAll('button:contains("Rent Now")');
    rentButtons.forEach(button => {
        button.addEventListener('click', function() {
            const equipmentName = this.closest('.bg-white').querySelector('h3').textContent;
            alert(`You clicked to rent: ${equipmentName}`);
            // Here you would typically redirect to a rental form or open a modal
        });
    });

    // Add animation to category icons
    const categoryIcons = document.querySelectorAll('.fas.text-4xl.text-green-600');
    categoryIcons.forEach(icon => {
        icon.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.2)';
            this.style.transition = 'transform 0.3s ease';
        });

        icon.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // Handle URL hash on page load
    if (window.location.hash) {
        const targetId = window.location.hash.substring(1);
        if (targetId.endsWith('-section')) {
            showSection(targetId);
        } else if (targetId === 'about' || targetId === 'contact') {
            document.getElementById(targetId).scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
}); 