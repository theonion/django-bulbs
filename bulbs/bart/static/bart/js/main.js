$( setup );

function setup(){
	headerScroll()
}

function headerScroll(){
	var header = 	$('header#primary').parent(),
		postBody =	$('.article-text').offset().top - 80,
		top = 		$(window).scrollTop(),
		topClass = 	'scrolled-up',
		scrollPt =	postBody

	console.log(postBody);

	$(window).load(function(){
		if (top <= scrollPt){ header.addClass(topClass) } 
	})	

	$(window).scroll(function() {
		var top = $(window).scrollTop()
		if (top <= scrollPt){ header.addClass(topClass) } 
		else { header.removeClass(topClass) }
	})
}