/**
 * Research Agora — Client-side filtering and search
 * No dependencies, vanilla JS.
 */
(function() {
    'use strict';

    const searchInput = document.getElementById('search');
    const grid = document.getElementById('skills-grid');
    const cards = Array.from(grid.querySelectorAll('.skill-card'));
    const resultsCount = document.getElementById('results-count');
    const resetBtn = document.getElementById('reset-filters');

    function getCheckedValues(filterName) {
        const group = document.querySelector(`[data-filter="${filterName}"]`);
        if (!group) return null;
        const checked = Array.from(group.querySelectorAll('input:checked'));
        const all = Array.from(group.querySelectorAll('input'));
        if (checked.length === all.length) return null; // all checked = no filter
        return checked.map(cb => cb.value);
    }

    function filterCards() {
        const query = searchInput.value.toLowerCase().trim();
        const pluginFilter = getCheckedValues('plugin');
        const typeFilter = getCheckedValues('type');
        const taskTypeFilter = getCheckedValues('task-type');
        const phaseFilter = getCheckedValues('phase');
        const verificationFilter = getCheckedValues('verification');

        let visible = 0;

        cards.forEach(card => {
            let show = true;

            // Text search
            if (query) {
                const name = (card.dataset.name || '').toLowerCase();
                const desc = (card.dataset.description || '').toLowerCase();
                if (!name.includes(query) && !desc.includes(query)) {
                    show = false;
                }
            }

            // Filter checks
            if (show && pluginFilter && !pluginFilter.includes(card.dataset.plugin)) show = false;
            if (show && typeFilter && !typeFilter.includes(card.dataset.type)) show = false;
            if (show && taskTypeFilter && !taskTypeFilter.includes(card.dataset.taskType)) show = false;
            if (show && phaseFilter && !phaseFilter.includes(card.dataset.phase)) show = false;
            if (show && verificationFilter && !verificationFilter.includes(card.dataset.verification)) show = false;

            card.classList.toggle('hidden', !show);
            if (show) visible++;
        });

        resultsCount.textContent = `Showing ${visible} of ${cards.length} skills`;
    }

    // Bind events
    searchInput.addEventListener('input', filterCards);

    document.querySelectorAll('.filter-group input').forEach(cb => {
        cb.addEventListener('change', filterCards);
    });

    resetBtn.addEventListener('click', function() {
        searchInput.value = '';
        document.querySelectorAll('.filter-group input').forEach(cb => {
            cb.checked = true;
        });
        filterCards();
    });
})();
