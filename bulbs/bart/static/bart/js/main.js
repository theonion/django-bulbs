$( setup );

function setup(){
	headerScroll()
}

function headerScroll(){
	var header = 	$('header#primary').parent(), // .header-container
		postBody =	$('.article-body p').first().offset().top - 80, // 80 above start of article body
		top = 		$(window).scrollTop() + 90, // Top of window plus 90 for the banner
		topClass = 	'scrolled-up' // Class to add/remove

	$(window).load(function(){
		if (top <= postBody){ header.addClass(topClass) } 
		positionTheHeader()
	})	

	$(window).scroll(function(e){ 
		var top = $(window).scrollTop()
		if (top <= postBody){ header.addClass(topClass) } 
		else { header.removeClass(topClass) }
		positionTheHeader()
	});

	function positionTheHeader() {
		$el = $('header#primary').parent(); 
		if ($(this).scrollTop() > 90 && $el.css('position') != 'fixed'){ 
			$el.css({'position': 'fixed', 'top': '0px'})
		} else if ($(this).scrollTop() < 90 && $el.css('position') == 'fixed'){
			$el.css({'position': 'absolute', 'top': '90px'})
		}
	}
}