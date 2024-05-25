document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const brFlag = document.getElementById('br-flag');
    const enFlag = document.getElementById('en-flag');
    
    // Adjust the path to switch languages
    if (currentPath.startsWith('/br')) {
        brFlag.href = currentPath; // Already on PT-BR, no change
        enFlag.href = currentPath.replace('/br', '') || '/';
    } else {
        brFlag.href = '/br' + (currentPath === '/' ? '' : currentPath);
        enFlag.href = currentPath;
    }
});