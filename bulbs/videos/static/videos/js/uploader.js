function uploadClick(e) {
    e.preventDefault();

    var url = e.target.dataset.url;
    var data = new FormData();
    for(var key in e.target.dataset) {
        if(key != 'url') {
            data.append(key, e.target.dataset[key]);
        }
    }
    console.log(django.jQuery(e.target));
    var fileInput = django.jQuery(e.target).siblings("input[type='file']");
    if(fileInput[0].files.length !== 0) {
        console.log(fileInput[0].files[0]);
        data.append(fileInput[0].files[0]);
    }

    // TODO: use this: http://bencoe.tumblr.com/post/30685403088/browser-side-amazon-s3-uploads-using-cors
    django.jQuery(url, {
        type: 'POST',
        data: data
    });
}

django.jQuery(document).ready(function($) {
    $('.video-upload').each(function(index, element) {
        $(element).click(uploadClick);
    });
});