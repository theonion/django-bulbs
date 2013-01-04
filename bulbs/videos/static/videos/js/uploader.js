function uploadClick(e) {
    e.preventDefault();

    var url = e.target.dataset.url;
    var data = new FormData();

    var fileInput = django.jQuery(e.target).siblings("input[type='file']");
    if(fileInput[0].files.length !== 0) {
        var file = fileInput[0].files[0];
        data.append('key', aws_attrs.directory + "/" + file.name);

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

    // TODO: use this: http://bencoe.tumblr.com/post/30685403088/browser-side-amazon-s3-uploads-using-cors
    var xhr = new XMLHttpRequest();
    xhr.onload = function(e) {
        console.log(e);
        console.log(xhr);
    };

    xhr.open("POST", url);
    xhr.send(data);
}

django.jQuery(document).ready(function($) {
    $('.video-upload').each(function(index, element) {
        $(element).click(uploadClick);
    });
});