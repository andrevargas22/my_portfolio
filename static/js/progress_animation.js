function animateProgressBar(element, targetPercentage, progressBarColor) {
    element.classList.add(progressBarColor);
    let width = 0;
    const interval = setInterval(function() {
        if (width >= targetPercentage) {
            clearInterval(interval);
        } else {
            width++;
            element.style.width = width + '%';
            element.setAttribute('aria-valuenow', width);
            element.innerHTML = width + '%';
        }
    }, 10);
}
