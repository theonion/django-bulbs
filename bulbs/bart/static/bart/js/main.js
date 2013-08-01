$( setup );

function setup(){
	headerScroll()
}

function headerScroll(){
	var header = 	$('header#primary').parent(), // .header-container
		postBody =	$('.article-text p').first().offset().top - 80, // 80 above start of article body
		top = 		$(window).scrollTop(), // Top of window (duh)
		topClass = 	'scrolled-up' // Class to add/remove

	$(window).load(function(){
		if (top <= postBody){ header.addClass(topClass) } 
	})	

	$(window).scroll(function() {
		var top = $(window).scrollTop()
		if (top <= postBody){ header.addClass(topClass) } 
		else { header.removeClass(topClass) }
	})
}