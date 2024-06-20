document.addEventListener('DOMContentLoaded', () => {
    const tooltip = document.getElementById('tooltip');
    const modal = document.getElementById('modal');
    const modalText = document.getElementById('modal-text');
    const closeModal = document.getElementById('close-modal');
    const icons = document.querySelectorAll('.icon');

    icons.forEach(icon => {
        icon.addEventListener('mouseenter', (event) => {
            if (window.innerWidth >= 768) { // Desktop
                const title = event.target.getAttribute('data-title');
                tooltip.textContent = title;
                tooltip.style.opacity = 1;
            }
        });

        icon.addEventListener('mouseleave', () => {
            if (window.innerWidth >= 768) { // Desktop
                tooltip.style.opacity = 0;
            }
        });

        icon.addEventListener('mousemove', (event) => {
            if (window.innerWidth >= 768) { // Desktop
                tooltip.style.left = `${event.pageX + 10}px`;
                tooltip.style.top = `${event.pageY + 10}px`;
            }
        });

        icon.addEventListener('click', (event) => {
            if (window.innerWidth < 768) { // Mobile
                const title = event.target.getAttribute('data-title');
                modalText.textContent = title;
                modal.style.display = 'block';
            }
        });
    });

    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });
});
