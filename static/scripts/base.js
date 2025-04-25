// JavaScript to manage sidebar item clicks
document.addEventListener("DOMContentLoaded", function () {
    const sidebarLinks = document.querySelectorAll(".sidebar-nav a");
    const sections = document.querySelectorAll(".content-section");

    sidebarLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault();

            // Hide all sections
            sections.forEach(section => section.classList.add("hidden"));

            // Remove active class from all sidebar links
            sidebarLinks.forEach(link => link.parentElement.classList.remove("active"));

            // Show the clicked section
            const targetSection = document.querySelector(link.getAttribute("href"));
            targetSection.classList.remove("hidden");

            // Add active class to the clicked sidebar link
            link.parentElement.classList.add("active");
        });
    });
});
