jQuery(document).ready(function() {
	jQuery('.dropdown-menu a.dropdown-toggle').on('click', function(e) {
		$this = jQuery(this);
	  if (!$this.next().hasClass('show')) {
		$this.parents('.dropdown-menu').first().find('.show').removeClass('show');
	  }
	  var $subMenu = $this.next('.dropdown-menu');
	  $subMenu.toggleClass('show');
	  //highlight link in use
	  $this.parents('.dropdown-menu').first().find('.active').removeClass('active');
	  	 $this.addClass('active');


	  $this.parents('li.nav-item.dropdown.show').on('hidden.bs.dropdown', function(e) {
		jQuery('.dropdown-submenu .show').removeClass('show');
		$this.removeClass('active');
	  });


	  return false;
	});

    $('[data-toggle="tooltip"]').tooltip()
});
