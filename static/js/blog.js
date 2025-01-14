/**
 * Blog Content Handler
 * 
 * Manages the interactive elements of the blog section:
 * - Article expansion/collapse
 * - URL hash navigation
 * - Content visibility toggling
 * 
 * Features:
 * - Deep linking support
 * - Smooth content transitions
 * - Automatic content handling based on URL
 */

document.addEventListener('DOMContentLoaded', function () {
    var titles = document.querySelectorAll('.article-title');
    var hash = window.location.hash;

    titles.forEach(function (title) {
        title.addEventListener('click', function (e) {
            e.preventDefault();
            var contentId = this.getAttribute('data-toggle');
            var content = document.getElementById(contentId);
            window.location.hash = contentId;

            if (content.style.display === 'none') {
                content.style.display = 'block';
            } else {
                content.style.display = 'none';
            }
        });
    });

    // Check if there's a hash in the URL and open the corresponding article
    if (hash) {
        var content = document.querySelector(hash);
        if (content) {
            content.style.display = 'block';
        }
    }
});
