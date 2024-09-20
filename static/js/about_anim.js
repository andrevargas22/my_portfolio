document.addEventListener('DOMContentLoaded', () => {
    const tooltip = document.getElementById('tooltip');
    const modal = document.getElementById('modal');
    const modalText = document.getElementById('modal-text');
    const closeModal = document.getElementById('close-modal');
    const icons = document.querySelectorAll('.icon'); // Select all icons

    // Add event listeners to each icon
    icons.forEach(icon => {
        // Show tooltip on mouse enter (desktop only)
        icon.addEventListener('mouseenter', (event) => {
            if (window.innerWidth >= 768) { // Only show tooltips on desktop screens
                const title = event.target.getAttribute('data-title');
                tooltip.textContent = title; // Set the tooltip text
                tooltip.style.opacity = 1; // Make tooltip visible
            }
        });

        // Hide tooltip on mouse leave (desktop only)
        icon.addEventListener('mouseleave', () => {
            if (window.innerWidth >= 768) { // Only hide tooltips on desktop screens
                tooltip.style.opacity = 0; // Hide tooltip
            }
        });

        // Move tooltip with the mouse cursor (desktop only)
        icon.addEventListener('mousemove', (event) => {
            if (window.innerWidth >= 768) { // Only move tooltips on desktop screens
                tooltip.style.left = `${event.pageX + 10}px`; // Position tooltip slightly right of cursor
                tooltip.style.top = `${event.pageY + 10}px`;  // Position tooltip slightly below cursor
            }
        });

        // Show modal with title when clicked (mobile only)
        icon.addEventListener('click', (event) => {
            if (window.innerWidth < 768) { // Only show modals on mobile screens
                const title = event.target.getAttribute('data-title');
                modalText.textContent = title; // Set modal text
                modal.style.display = 'block'; // Show modal
            }
        });
    });

    // Close modal when the close button is clicked
    closeModal.addEventListener('click', () => {
        modal.style.display = 'none'; // Hide modal
    });

    // Close modal when clicking outside of the modal content
    window.addEventListener('click', (event) => {
        if (event.target == modal) { // If the click is outside the modal content
            modal.style.display = 'none'; // Hide modal
        }
    });
});
