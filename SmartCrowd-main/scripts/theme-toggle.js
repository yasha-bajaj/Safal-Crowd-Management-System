document.addEventListener('DOMContentLoaded', () => {
    console.log('JavaScript loaded'); // Add this line to verify JS is running
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeLink = document.getElementById('theme-link');

    themeToggleBtn.addEventListener('click', () => {
        if (themeLink.getAttribute('href') === 'styles/light-theme.css') {
            themeLink.setAttribute('href', 'styles/dark-theme.css');
        } else {
            themeLink.setAttribute('href', 'styles/light-theme.css');
        }
    });
});
