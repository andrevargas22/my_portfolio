document.addEventListener('DOMContentLoaded', function () {
    var titles = document.querySelectorAll('.article-title');
    titles.forEach(function (title) {
        title.addEventListener('click', function (e) {
            e.preventDefault();
            var contentId = this.getAttribute('data-toggle');
            var content = document.getElementById(contentId);
            if (content.style.display === 'none') {
                content.style.display = 'block';
            } else {
                content.style.display = 'none';
            }
        });
    });
});