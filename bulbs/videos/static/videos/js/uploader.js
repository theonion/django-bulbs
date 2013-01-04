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
    
    var root = django.jQuery(fileInput[0]).parent();
    var labelHTML = root.find("label")[0].outerHTML;
    var finishedHTML = labelHTML + constructFinishedHTML( root, url + "/" + path );
    var errorHTML =  labelHTML + "Could not upload the file at this time. Are you connected to the internet?";

    root.find("input").remove();
    root.find("a").remove();

    var progress = ProgressBar( root, true );
    
    // TODO: use this: http://bencoe.tumblr.com/post/30685403088/browser-side-amazon-s3-uploads-using-cors
    var xhr = new XMLHttpRequest();
    
    xhr.onreadystatechange = function(e){
        if( xhr.readyState !== 4 ){ return; }
        root.html( finishedHTML );
    }
    
    xhr.upload.addEventListener('progress', function( e ){
        var percent = (e.loaded / e.total ) * 100;
        progress.update( percent );
    }, false);
    
    xhr.upload.addEventListener('error', function( e ){
        root.html( errorHTML );
        root.html();
    }, false);
    
    xhr.upload.addEventListener('abort', function( e ){
        root.html( errorHTML );
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
    
    var exports = {};
    exports.update = update;
    return exports;
}

function constructFinishedHTML( container, filename ){
    var name = container.find("input[type='file']").attr('name');
    var id = container.find("input[type='file']").attr('name');;
    return "<input class='vURLField' type='text' name='" + name + "' id='" + id + "' value='" + filename + "'/>";
}


django.jQuery(document).ready(function($) {
    $('.video-upload').each(function(index, element) {
        $(element).click(uploadClick);
    });
});