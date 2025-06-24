// Multi-level dropdown functionality
$(document).ready(function() {
    // Handle dropdown submenu hover
    $('.dropdown-submenu > a').on('mouseenter', function() {
        $(this).next('.dropdown-menu').show();
    });
    
    $('.dropdown-submenu').on('mouseleave', function() {
        $(this).find('.dropdown-menu').hide();
    });
    
    // Handle dropdown toggle clicks
    $('.dropdown-toggle').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        var $dropdown = $(this).next('.dropdown-menu');
        var $parent = $(this).closest('.dropdown-submenu');
        
        // Hide all other dropdowns at the same level
        $parent.siblings().find('.dropdown-menu').hide();
        
        // Toggle current dropdown
        $dropdown.toggle();
    });
    
    // Close dropdowns when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.dropdown').length) {
            $('.dropdown-menu').hide();
        }
    });
}); 