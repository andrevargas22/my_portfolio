/*
 * About page - expandable timeline.
 * Toggles .mt-card.open when a card header is clicked or activated by keyboard.
 */
(function () {
    function init() {
        const heads = document.querySelectorAll('.mtimeline .mt-head');
        function toggle(head) {
            const card = head.closest('.mt-card');
            const open = card.classList.toggle('open');
            head.setAttribute('aria-expanded', open ? 'true' : 'false');
        }
        heads.forEach(function (head) {
            head.addEventListener('click', function () { toggle(head); });
            head.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggle(head);
                }
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
