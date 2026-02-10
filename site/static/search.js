/**
 * Research Agora — Client-side filtering, search, and group-aware navigation
 * No dependencies, vanilla JS.
 */
(function() {
    'use strict';

    const searchInput = document.getElementById('search');
    const content = document.getElementById('skills-content');
    const resultsCount = document.getElementById('results-count');
    const resetBtn = document.getElementById('reset-filters');
    const showInternalCb = document.getElementById('show-internal');
    const internalSection = document.getElementById('internal-section');
    const intentButtons = document.querySelectorAll('.intent-btn');
    const groups = document.querySelectorAll('.skill-group');

    // All public cards (inside groups)
    const publicCards = Array.from(content.querySelectorAll('.skill-group .skill-card'));
    // All internal cards
    const internalCards = Array.from(content.querySelectorAll('.skill-card-internal'));
    // Total public count for display
    const totalPublic = publicCards.length;

    let activeIntent = 'all';

    function getCheckedValues(filterName) {
        const group = document.querySelector('[data-filter="' + filterName + '"]');
        if (!group) return null;
        const checked = Array.from(group.querySelectorAll('input:checked'));
        const all = Array.from(group.querySelectorAll('input'));
        if (checked.length === all.length) return null; // all checked = no filter
        return checked.map(function(cb) { return cb.value; });
    }

    function matchesSearch(card, query) {
        if (!query) return true;
        var name = (card.dataset.name || '').toLowerCase();
        var desc = (card.dataset.description || '').toLowerCase();
        return name.includes(query) || desc.includes(query);
    }

    function matchesFilters(card, pluginFilter, taskTypeFilter, verificationFilter) {
        if (pluginFilter && !pluginFilter.includes(card.dataset.plugin)) return false;
        if (taskTypeFilter && !taskTypeFilter.includes(card.dataset.taskType)) return false;
        if (verificationFilter && !verificationFilter.includes(card.dataset.verification)) return false;
        return true;
    }

    function filterCards() {
        var query = searchInput.value.toLowerCase().trim();
        var pluginFilter = getCheckedValues('plugin');
        var taskTypeFilter = getCheckedValues('task-type');
        var verificationFilter = getCheckedValues('verification');

        var visiblePublic = 0;

        // Determine which groups are visible based on intent
        var intentGroups = null;
        if (activeIntent !== 'all') {
            intentGroups = activeIntent.split(',');
        }

        // Filter public cards within groups
        groups.forEach(function(group) {
            var groupId = group.dataset.group;
            var groupHidden = intentGroups && !intentGroups.includes(groupId);

            if (groupHidden) {
                group.classList.add('hidden');
                return;
            }

            var cards = Array.from(group.querySelectorAll('.skill-card'));
            var groupVisible = 0;

            cards.forEach(function(card) {
                var show = matchesSearch(card, query) && matchesFilters(card, pluginFilter, taskTypeFilter, verificationFilter);
                card.classList.toggle('hidden', !show);
                if (show) {
                    groupVisible++;
                    visiblePublic++;
                }
            });

            // Hide group if no visible cards
            group.classList.toggle('hidden', groupVisible === 0);
        });

        // Filter internal cards if visible
        if (showInternalCb.checked) {
            var visibleInternal = 0;
            internalCards.forEach(function(card) {
                var show = matchesSearch(card, query) && matchesFilters(card, pluginFilter, taskTypeFilter, verificationFilter);
                card.classList.toggle('hidden', !show);
                if (show) visibleInternal++;
            });
            internalSection.classList.toggle('hidden', visibleInternal === 0);
            resultsCount.textContent = 'Showing ' + visiblePublic + ' of ' + totalPublic + ' skills' +
                (visibleInternal > 0 ? ' + ' + visibleInternal + ' internal' : '');
        } else {
            internalSection.classList.add('hidden');
            resultsCount.textContent = 'Showing ' + visiblePublic + ' of ' + totalPublic + ' skills';
        }
    }

    // Intent button handlers
    intentButtons.forEach(function(btn) {
        btn.addEventListener('click', function() {
            intentButtons.forEach(function(b) { b.classList.remove('active'); });
            btn.classList.add('active');
            activeIntent = btn.dataset.groups;
            filterCards();
        });
    });

    // Internal toggle
    showInternalCb.addEventListener('change', filterCards);

    // Search input
    searchInput.addEventListener('input', filterCards);

    // Filter checkboxes
    document.querySelectorAll('.filter-group input').forEach(function(cb) {
        cb.addEventListener('change', filterCards);
    });

    // Description expand/collapse
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.desc-toggle');
        if (!btn) return;
        var desc = btn.closest('.card-description');
        if (!desc) return;
        var short = desc.querySelector('.desc-short');
        var full = desc.querySelector('.desc-full');
        if (short && full) {
            short.classList.toggle('hidden');
            full.classList.toggle('hidden');
        }
    });

    // Reset button
    resetBtn.addEventListener('click', function() {
        searchInput.value = '';
        showInternalCb.checked = false;
        document.querySelectorAll('.filter-group input').forEach(function(cb) {
            cb.checked = true;
        });
        intentButtons.forEach(function(b) { b.classList.remove('active'); });
        document.querySelector('.intent-btn-all').classList.add('active');
        activeIntent = 'all';
        filterCards();
    });
})();
