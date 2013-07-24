
(function( w ){

    /* We can request an image at every possible width, but let's limit it to a reasonalbe number 
       We can set these so they are correspond to our more common sizes.
    */
    var breakpoints = [0,50, 150, 200, 300, 400, 500, 600, 800];

    w.picturefill = function() {
        //don't need to do them all at once. can decide to do lazy load if needed
        var ps = w.document.getElementsByTagName( "div" ); 
        // Loop the pictures
        function tmpl(text, dict) {
            for (k in dict) {
                text = text.replace("{{" + k + "}}", dict[k]);
            }
            return text
        }


        for( var i = 0, il = ps.length; i < il; i++ ){
            if( ps[ i ].getAttribute( "data-picture" ) !== null ){

                var div = ps[ i ].getElementsByTagName( "div" )[0];

                if( ps[ i ].getAttribute( "data-image-id" ) !== null ){
                    var id = ps[ i ].getAttribute( "data-image-id" ),
                        crop = ps[ i ].getAttribute( "data-crop" );
                    var _w = div.offsetWidth,
                        _h = div.offsetHeight;

                    if (!crop) {
                        var aspectRatio = Math.ceil(_w/_h * 10);
                        //smooth out rounding issues.
                        switch (aspectRatio) {
                            case 14:
                                crop = "4x3";
                                break;
                            case 18:
                                crop = "16x9";
                                break;
                            case 8:
                                crop = "3x4";
                                break;
                            case 10:
                                crop = "1x1";
                                break;
                            default:
                                crop = "original";
                        }
                    }
                    var width = 50;
                    for (var j = 0; j < breakpoints.length; j++) {
                        if (_w <= breakpoints[j]) {
                            width = breakpoints[j];
                            break;
                        }
                    }   
                    // TODO: do something for retina
                    if (w.devicePixelRatio) {
                        if (w.devicePixelRatio > 1) {

                        }
                    }

                    // Find any existing img element in the picture element
                    var picImg = div.getElementsByTagName( "img" )[ 0 ];

                    if( !picImg ){
                        picImg = w.document.createElement( "img" );
                        picImg.alt = ps[ i ].getAttribute( "data-alt" );
                        div.appendChild( picImg );
                    }
                    picImg.src = tmpl(IMAGE_URL, {id: id, crop: crop, width: width});
                }
            }
        }
    };
    // Run on resize and domready (w.load as a fallback)
    if( w.addEventListener ){
        w.addEventListener( "resize", w.picturefill, false );
        w.addEventListener( "DOMContentLoaded", function(){
            w.picturefill();
            // Run once only
            w.removeEventListener( "load", w.picturefill, false );
        }, false );
        w.addEventListener( "load", w.picturefill, false );
    }
    else if( w.attachEvent ){
        w.attachEvent( "onload", w.picturefill );
    }
    
}( this ));