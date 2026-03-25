(function() {
    var saved = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    updateIcon(saved);

    window.toggleTheme = function() {
        var current = document.documentElement.getAttribute('data-theme');
        var next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        updateIcon(next);
    };

    function updateIcon(theme) {
        var icons = document.querySelectorAll('.theme-icon');
        icons.forEach(function(el) {
            el.textContent = theme === 'dark' ? '\u2600\uFE0F' : '\uD83C\uDF19';
        });
    }
})();
