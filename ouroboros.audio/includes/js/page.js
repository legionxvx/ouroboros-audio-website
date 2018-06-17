$(function() {
	

	// Vars.
		var	$window = $(window),
			$body = $('body'),
			$projects = $('#projects');
			$container = $('#container');

	// Breakpoints.
		skel.breakpoints({
			xlarge:	'(max-width: 1680px)',
			large:	'(max-width: 1280px)',
			medium:	'(max-width: 980px)',
			small:	'(max-width: 736px)',
			xsmall:	'(max-width: 480px)'
		});

	// Disable animations/transitions until everything's loaded.
		$body.addClass('loading');

		$window.on('load', function() {
			$body.removeClass('loading');
		});
		

	// Poptrox.
		$window.on('load', function() {
			$projects.poptrox({
				onPopupClose: function() { $container.removeClass('covered'); },
				onPopupOpen: function() { $container.addClass('covered'); },
				baseZIndex: 10001,
				useBodyOverflow: false,
				usePopupEasyClose: true,
				overlayColor: '#000000',
				overlayOpacity: 0.75,
				popupLoaderText: '',
				fadeSpeed: 500,
				usePopupDefaultStyling: false,
				windowMargin: (skel.breakpoint('small').active ? 5 : 50)
			});

		});

});