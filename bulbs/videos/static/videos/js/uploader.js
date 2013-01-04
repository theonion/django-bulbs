function uploadClick(e) {
    var self = this;
    
    e.preventDefault();
    
    var path = "";
    var url = e.target.dataset.url;
    var data = new FormData();

    var fileInput = django.jQuery(e.target).siblings("input[type='file']");
    if(fileInput[0].files.length !== 0) {
        var file = fileInput[0].files[0];
        path = aws_attrs.directory + "/" + file.name;
        data.append('key', path);

        data.append('AWSAccessKeyId', aws_attrs.AWSAccessKeyId);
        data.append('acl', aws_attrs.acl);
        data.append('success_action_redirect', aws_attrs.success_action_redirect);
        data.append('policy', aws_attrs.policy);
        data.append('signature', aws_attrs.signature);
    
        data.append('file', file);
    } else {
        alert("You didn't select a file!");
        return;
    }
    
    var filename = "s3://" + aws_attrs.bucket + "/" + path
    
    var root = django.jQuery(fileInput[0]).closest('div');
    var input = root.find(".initial input");
    var error = "Could not upload the file at this time. Are you connected to the internet?";

    root.find(".initial").hide();
    root.find(".upload").hide();
    var progress = ProgressBar( root, true );
    
    // TODO: use this: http://bencoe.tumblr.com/post/30685403088/browser-side-amazon-s3-uploads-using-cors
    var xhr = new XMLHttpRequest();
    
    xhr.onreadystatechange = function(e){
        if( xhr.readyState !== 4 ){ return; }
        progress.remove();
        showInitial( root );
        input.val( filename );
    }
    
    xhr.upload.addEventListener('progress', function( e ){
        var percent = (e.loaded / e.total ) * 100;
        progress.update( percent );
    }, false);
    
    xhr.upload.addEventListener('error', function( e ){
        showInitial( root );
        input.val('');
        alert( error );
    }, false);
    
    xhr.upload.addEventListener('abort', function( e ){
        showInitial( root );
        input.val('');
        alert( error );
    }, false);
    
    xhr.open("POST", url);
    xhr.send(data);
}

function ProgressBar( div, append ){ 
    var root = django.jQuery(div);   
    append = append || false;
    var progressValue;
    var template = "\
        <div class='progress-wrap'>\
            <div class='progress-value' style='background-color: #0a0; width: 0%;'>\
                <div class='progress-text'>\
                    Uploading\
                </div>\
            </div>\
        </div>\
        ";
        
    setup();
    
    function setup(){
        !append && root.empty();
        // weird bug where append is getting rid of label
        root.append(template);
        progressValue = root.find(".progress-value");
    }
    
    function update( percent ){
        progressValue.css("width", percent + "%");
    }
    
    function remove(){
        root.find(".progress-wrap").remove();
    }
    
    var exports = {};
    exports.update = update;
    exports.remove = remove;
    return exports;
}

function showUpload( root ){
    root.find(".upload").show();
    root.find(".initial").hide();
}

function showInitial( root ){
    root.find(".upload").hide();
    root.find(".initial").show();
}

django.jQuery(document).ready(function($) { 
    $('.video-upload').each(function(index, element) {
        $(element).click(uploadClick);
    });
    
    $(".video-choose").click(function(e){
        showUpload( $(this).closest('div') );

    });
    
    $(".video-upload-close").click(function(e){
        showInitial( $(this).closest('div') );
    });
});