window.o = window.o || {};

o.markdownEditor = (function(){
    var exports = {};
    
    $(function(){
        $('[data-widget="markdown-editor"]').each( buildEditor );
    });
	
	function buildEditor(){
        var textarea = $('textarea', this );
		var toolbar = $('.toolbar', this );
		var boldBtn = $('.bold', toolbar );
		var italicBtn = $('.italic', toolbar );
		var linkBtn = $('.link', toolbar );
		var imageBtn = $('.image', toolbar );
		var videoBtn = $('.video', toolbar );
		var h2Btn = $('.h2', toolbar );
		var h3Btn = $('.h3', toolbar );

        var editor = CodeMirror.fromTextArea( textarea[0], {
          mode: 'markdown',
		  lineWrapping: true,
          tabMode: 'indent',
		  extraKeys: {
			  'Cmd-B': toggleBold,
			  'Cmd-I': toggleItalic
		  }
        });
			
		// Formatting buttons
		boldBtn.click( toggleBold );
		italicBtn.click( toggleItalic );
			
		// Insertion buttons
		linkBtn.click( insertLink );
		imageBtn.click( insertImage );
		videoBtn.click( insertVideo );
		h2Btn.click( insertH2 );
		h3Btn.click( insertH3 );
			
		function toggleBold(){
			var cursor = editor.getCursor( true );
			var selection = editor.getSelection() || '';
				
			if( 0 === selection.length ){
				editor.replaceRange('****', cursor, cursor );
				editor.setSelection({ line: cursor.line, ch: cursor.ch + 2 }, { line: cursor.line, ch: cursor.ch + 2 });
			}
			else if( /^\*\*.*\*\*$/m.test(selection) ){
				editor.replaceSelection( selection.replace(/^\*\*/m, '').replace(/\*\*$/m, '') );
			}
			else {
				editor.replaceSelection( selection.replace(/^\**([^*]+)\**$/m, '**$1**') );					
			}
			editor.focus();
		}
			
		function toggleItalic(){
			var cursor = editor.getCursor( true );
			var selection = editor.getSelection() || '';
				
			if( 0 === selection.length ){
				editor.replaceRange('**', cursor, cursor );
				editor.setSelection({ line: cursor.line, ch: cursor.ch + 1 }, { line: cursor.line, ch: cursor.ch + 1 });
			}
			else if( /^\*.*\*$/m.test(selection) ){
				editor.replaceSelection( selection.replace(/^\*/m, '').replace(/\*$/m, '') );
			}
			else {
				editor.replaceSelection( selection.replace(/^\**([^*]+)\**$/m, '*$1*') );					
			}
			editor.focus();
		}
			
		function insertLink(){
			var selection = editor.getSelection() || '';
			var cursor = editor.getCursor( true );
			var text = selection ? selection : 'link text';
			var dummyUrl = 'http://url.com';
			
			getLink(function( err, url, title ){
				if( err ) return editor.focus();
					
				text = title || text;
				url = url || dummyUrl;
				
				editor.replaceRange('[' + text + '](' + url + ')', cursor, { line: cursor.line, ch: cursor.ch + selection.length });
				editor.setSelection({ line: cursor.line, ch: cursor.ch + 1 }, { line: cursor.line, ch: cursor.ch + 1 + text.length })
				editor.focus();
			});
		}
			
		function insertImage(){
			var selection = editor.getSelection() || '';
			var cursor = editor.getCursor( false );
			
			getImage(function( err, img ){
				var path = '/path/to.image';	
				editor.replaceRange('<img src="' + path + '">', cursor, cursor );
				editor.setSelection({ line: cursor.line, ch: cursor.ch + 10 }, { line: cursor.line, ch: cursor.ch + 10 + path.length })
				editor.focus();
			});
		}
		
		function insertVideo(){
			var selection = editor.getSelection() || '';
			var cursor = editor.getCursor( false );
			
			getVideo(function( err, img ){
				var path = '/path/to.image';	
				editor.replaceRange('<img src="' + path + '">', cursor, cursor );
				editor.setSelection({ line: cursor.line, ch: cursor.ch + 10 }, { line: cursor.line, ch: cursor.ch + 10 + path.length })
				editor.focus();
			});
		}
		
			
		function insertH2(){
			return insertHeader( 2 );
		}
			
		function insertH3(){
			return insertHeader( 3 );
		}
			
		function insertHeader( depth ){
			depth = depth || 2;
			var hashes = new Array( depth + 1 ).join('#'); // build string of #s with length of `depth` 
				
			var selection = editor.getSelection() || '';
			var cursor = editor.getCursor( true );
			var text = selection ? selection : 'Heading';
				
			editor.replaceRange('\n' + hashes + ' ' + text + '\n', cursor, { line: cursor.line, ch: cursor.ch + text.length });
			editor.setSelection({ line: cursor.line + 1, ch: depth + 1 }, { line: cursor.line + 1, ch: depth + 1 + text.length })
			editor.focus();
				
		}
			
        exports.editors = exports.editors || [];
        exports.editors.push( editor );
    }
	
	function getVideo( cbk ){
		var guts = (''
			+ '<div class="group find">'
				+ '<h3>Find Video:</h3>'
			+ '</div>'
			+ '<div class="group enter">'
				+ '<h3>&hellip;or enter URL:</h3>'
			+ '</div>'
		);
		var modal = showModal( guts, cbk );
		
		$('.insert-url', modal ).click(function(){
			var url = $('[name="image-url"]', modal ).val();
			if( ! url ) return;
			
			cbk && cbk( null, { url: url });
			modal.remove();
		});
	}
	
	function getImage( cbk ){
		var guts = (''
			+ '<div class="step step-1">' 
				+ '<div class="group find">'
					+ '<h3>Find Image:</h3>'
					+ '<div class="finder"></div>'
				+ '</div>'
				+ '<div class="group enter">'
					+ '<h3>&hellip;or enter URL:</h3>'
					+ '<input type="text" name="image-url">'
					+ '<button class="insert-url">Insert &rarr;</button>'
				+ '</div>'
			+ '</div>'
			
			+ '<div class="step step-2">'
				+ '<button class="back">&larr; Back</button>'
				+ '<h3>Choose aspect ratio:</h3>'
			+ '</div>'
		);
		
		var modal = showModal( guts, cbk );
		var finder = o.contentFinder({ quick: true, types: ['image']}, $('.finder', modal )[0]);
		
		$('.insert-url', modal ).click(function(){
			var url = $('[name="image-url"]', modal ).val();
			if( ! url ) return;
			
			cbk && cbk( null, { url: url });
			modal.remove();
		});
	}
	
	function getLink( cbk ){
		var guts = (''
			+ '<div class="group enter">'
				+ '<h3>Enter URL:</h3>'
				+ '<input type="text" name="url" class="url-field" placeholder="http://example.com">'
			+ '</div>'

			+ '<div class="group find">'		
				+ '<h3>Find Article / Content:</h3>'
			+ '</div>'
		);
		var modal = showModal( guts, cbk );
		var field = $('[name="url"]', modal );
		
		field.keyup(function( e ){
			if( e.keyCode !== 13 /* Enter/Return */ ) return;
			
			var url = field.val();
			if( ! url ) return;
			
			cbk && cbk( null, url );
			modal.remove();
		});
		
		field[0].select();
	}
	
	function showModal( html, cbk ){
		var elem = $(''
			+ '<div class="edit-modal">'
				+ html
				+ '<button class="close">&times;</button>'
			+ '</div>'
		);
		
		$('button.close', elem ).click(function(){
			elem.remove();
			cbk && cbk('closed');
		});
		
		return elem.appendTo('body');
	}
    
    return exports;
})();

o.contentFinder = (function(){
	function contentFinder( userOpts, root, cbk ){
		// If called wihout 'new', make a new instance anyway
		if( ! (this instanceof contentFinder) ){
			return new contentFinder( userOpts, root, cbk );
		}
		
		var field;
		var list;
		var opts = {};
		
		setup();
		function setup(){
			opts = $.extend( opts, userOpts );
			build();
			
		}
		
		function build(){
			$(root).html(''
				+ '<div class="quick-finder">'
					+ '<div class="controls">'
						+ '<div class="field">'
							+ '<input class="search-field" type="text" placeholder="Search…">'
						+ '</div>'
						+ ( opts.quick ? ''
							: '<div class="options">'
								+ ''
							+ '</div>' 
						)
					+ '</div>'
					+ '<div class="results">'
						+ '<ul></ul>'
					+ '</div>'					
				+ '</div>'
			);
		}
		
		function buildItem( item, opts ){
			
		}
	}
	
	return contentFinder;
})();

o.eventify = (function(){
	
});
