$( setup );

function setup(){
	imageSizer()
	addComments()
}

var imageSizeJS = STATIC_URL + 'images/js/image.js'

function imageSizer(){
	$.getScript(imageSizeJS, function(){
		console.log('test')
	})
}

function addComments(){
	if ($("#comments").length){
		$("#comments").moot({
		   url: "https://moot.it/avclub/prototype-detail",
		   title: "Prototype detail page"
		})
	}
}