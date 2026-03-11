// Simplified dropdown menu handling
$(document).ready(function() {
    console.log('Simple dropdown script loaded');
    
    // Handle main menu dropdowns
    $(document).on('mouseenter', '.nav-item.dropdown', function() {
        var $dropdown = $(this);
        console.log('Mouse enter on main menu:', $dropdown.find('.dropdown-toggle').text());
        
        // Hide other main menus
        $('.nav-item.dropdown').not($dropdown).removeClass('show');
        $('.dropdown-menu').removeClass('show');
        
        // Show current menu
        $dropdown.addClass('show');
        $dropdown.find('> .dropdown-menu').addClass('show');
    });
    
    $(document).on('mouseleave', '.nav-item.dropdown', function() {
        var $dropdown = $(this);
        setTimeout(function() {
            if (!$dropdown.is(':hover')) {
                $dropdown.removeClass('show');
                $dropdown.find('.dropdown-menu').removeClass('show');
            }
        }, 300);
    });
    
    // Handle dropdown menu hover to keep them open
    $(document).on('mouseenter', '.dropdown-menu', function() {
        // Keep menu open when hovering over it
    });
    
    $(document).on('mouseleave', '.dropdown-menu', function() {
        var $menu = $(this);
        var $dropdown = $menu.parent('.dropdown');
        
        setTimeout(function() {
            if (!$dropdown.is(':hover') && !$menu.is(':hover')) {
                $dropdown.removeClass('show');
                $menu.removeClass('show');
            }
        }, 300);
    });
    
    // Close dropdowns when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.dropdown').length) {
            $('.dropdown').removeClass('show');
            $('.dropdown-menu').removeClass('show');
        }
    });
    
    // Close dropdowns with ESC key
    $(document).on('keydown', function(e) {
        if (e.keyCode === 27) {
            $('.dropdown').removeClass('show');
            $('.dropdown-menu').removeClass('show');
        }
    });
    
    // Search functionality
    const SEARCH_PAGE_SIZE = 5;
    let searchResults = [];
    let currentPage = 1;
    let searchIndex = [];
    let searchablePages = new Set();

    function getRelativePrefix() {
        const currentPath = window.location.pathname;
        let pathParts = currentPath.split('/').filter(Boolean);

        console.log('Current path:', currentPath);

        const srcIndex = pathParts.lastIndexOf('src');
        if (srcIndex !== -1) {
            pathParts = pathParts.slice(srcIndex + 1);
        }

        if (pathParts.length > 0 && pathParts[pathParts.length - 1].includes('.')) {
            pathParts = pathParts.slice(0, -1);
        }

        const prefix = '../'.repeat(pathParts.length);
        console.log('Calculated relative prefix:', prefix || './');
        return prefix;
    }

    function getSearchIndexPath() {
        return `${getRelativePrefix()}searchIndex.json`;
    }

    function normalizeInternalPath(url) {
        if (!url || url.startsWith('http') || url.startsWith('#') || url.startsWith('mailto:')) {
            return null;
        }

        return url.replace(/^(\.\.\/)+/, '').replace(/^\.\//, '').replace(/^\//, '');
    }

    function refreshSearchablePages() {
        searchablePages = new Set();

        $('#navbar-include a').each(function() {
            const href = $(this).attr('href');
            const normalizedHref = normalizeInternalPath(href);

            if (normalizedHref && normalizedHref.endsWith('.html')) {
                searchablePages.add(normalizedHref);
            }
        });

        console.log('Searchable navbar pages:', Array.from(searchablePages));
    }

    $.getJSON(getSearchIndexPath(), function(data) {
        searchIndex = data;
        console.log('Search index loaded successfully, found', data.length, 'pages');
    }).fail(function(jqXHR, textStatus, errorThrown) {
        console.error('Failed to load searchIndex.json:', textStatus, errorThrown);
        console.log('Attempted path:', getSearchIndexPath());
        console.log('Current URL:', window.location.href);
    });

    function showSearchModal(results) {
        searchResults = results;
        currentPage = 1;
        updateSearchResults();
        $('#searchModal').modal('show');
    }

    function updateSearchResults() {
        const start = (currentPage - 1) * SEARCH_PAGE_SIZE;
        const end = start + SEARCH_PAGE_SIZE;
        const pageResults = searchResults.slice(start, end);
        const relativePrefix = getRelativePrefix();
        let html = '';

        pageResults.forEach(item => {
            let correctUrl = item.url;

            console.log('Original URL:', item.url);

            if (!item.url.startsWith('http') && !item.url.startsWith('/')) {
                correctUrl = `${relativePrefix}${item.url}`;
                console.log('Corrected URL:', correctUrl);
            }
            
            html += `<div class="search-result-item mb-3">
                <a href="${correctUrl}" class="h5 text-primary">${item.title}</a>
                <div class="text-muted small">${item.snippet}</div>
            </div>`;
        });
        if (html === '') {
            html = '<div class="text-center text-muted">No results found.</div>';
        }
        $('#searchResultsList').html(html);
        // Update pagination
        const totalPages = Math.ceil(searchResults.length / SEARCH_PAGE_SIZE);
        $('#pageInfo').text(`Page ${currentPage} of ${totalPages}`);
        $('#prevPage').prop('disabled', currentPage === 1);
        $('#nextPage').prop('disabled', currentPage === totalPages || totalPages === 0);
    }

    // Pagination button events
    $(document).on('click', '#prevPage', function() {
        if (currentPage > 1) {
            currentPage--;
            updateSearchResults();
        }
    });

    $(document).on('click', '#nextPage', function() {
        const totalPages = Math.ceil(searchResults.length / SEARCH_PAGE_SIZE);
        if (currentPage < totalPages) {
            currentPage++;
            updateSearchResults();
        }
    });

    // Search form submit event
    $(document).on('submit', '#searchForm', function(e) {
        e.preventDefault();
        const keyword = $('#searchInput').val().trim().toLowerCase();
        if (!keyword) {
            alert('Please enter a search term');
            return;
        }
        
        if (searchIndex.length === 0) {
            alert('Search index not loaded yet. Please try again.');
            return;
        }
        
        const results = searchIndex.filter(item =>
            searchablePages.has(normalizeInternalPath(item.url)) &&
            (
                (item.title && item.title.toLowerCase().includes(keyword)) ||
                (item.snippet && item.snippet.toLowerCase().includes(keyword)) ||
                (item.content && item.content.toLowerCase().includes(keyword))
            )
        );
        showSearchModal(results);
    });

    // Clear search input when modal is closed
    $('#searchModal').on('hidden.bs.modal', function() {
        $('#searchInput').val('');
    });

    $(document).ajaxComplete(function(event, xhr, settings) {
        if (settings && settings.url && settings.url.includes('navbar.html')) {
            refreshSearchablePages();
        }
    });
}); 