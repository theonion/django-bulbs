var VideoRecircList = function() {
  $videoItem = 'video-item';
  $videoRecircList = $('#video-list');
  $bettyUrl = $videoRecircList.data('betty-url');
  $source = $videoRecircList.data('source');
  this.init();
};

VideoRecircList.prototype.init = function() {
  this.loadVideoRecirc();
};

VideoRecircList.prototype.loadVideoRecirc = function() {
  $.getJSON($source, function(data) {
    console.log(data);
    $.each(data.results.slice(0,8), function(index, video) {
      $videoTitle = video.title;
      $videoHref = '/v/' + video.id;
      $posterSource = $bettyUrl + '/' + video.poster.id
      $('<a>',{
        'class' : $videoItem,
        'href' : $videoHref,
        'html': $('<figure>',{
          'class' : 'content',
          'html' : '<div class="image"><img src="' + $posterSource + '/16x9/480.jpg"></div>'
        }).add($('<p>',{
          'html' : $videoTitle
        }))
      }).appendTo($videoRecircList);
    });
  });
};

new VideoRecircList();