$( setup );

function setup(){
	headerScroll()
}

function headerScroll(){
	var header = 	$('header#primary').parent(),
		top = 		$(window).scrollTop(),
		topClass = 	'scrolled-up',
		scrollPt =	15

	$(window).load(function(){
		if (top <= scrollPt){ header.addClass(topClass) } 
	})	

	$(window).scroll(function() {
		var top = $(window).scrollTop()
		if (top <= scrollPt){ header.addClass(topClass) } 
		else { header.removeClass(topClass) }
	})
}