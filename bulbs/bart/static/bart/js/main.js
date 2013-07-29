$( setup );

function setup(){
	addComments()
}

function addComments(){
	if ($("#comments").length){
		$("#comments").moot({
		   url: "https://moot.it/avclub/prototype-detail",
		   title: "Prototype detail page"
		})
	}
}