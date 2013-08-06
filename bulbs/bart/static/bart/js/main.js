$( setup );

function setup(){
}

function headerScroll(){
	var headerEl = 	$('header#primary').parent(), // .header-container
		adHeight = 	90,
		postBody =	$('.article-body p').first().offset().top - 80, // 80 above start of article body
		topClass = 	'scrolled-up', // Class to add/remove
		top = 		$(window).scrollTop(),
		topWithAd = top + adHeight

	if (topWithAd <= postBody){ headerEl.addClass(topClass) } 
		else { headerEl.removeClass(topClass) }

	if (top > adHeight){ 
		headerEl.css({'position': 'fixed', 'top': '0px'})
	} else {
		headerEl.css({'position': 'absolute', 'top': adHeight + 'px'})
	}
}

$(document).ready(function(){
	headerScroll()
})	

$(window).scroll(function(e){ 
	headerScroll()
})