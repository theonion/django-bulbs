var VideoRecircList = function() {
  $videoItem = 'video-item';
  $videoRecircList = $('#video-list');
  $bettyUrl = $videoRecircList.data('betty-url');
  $source = $videoRecircList.data('source');
  $recircCount = $videoRecircList.data('count');
  this.init();
};

VideoRecircList.prototype.init = function() {
  this.loadVideoRecirc();
};

VideoRecircList.prototype.loadVideoRecirc = function() {
  $.getJSON($source, function(data) {
    $.each(data.results.slice(0,$recircCount), function(index, video) {
      $videoTitle = video.title;
      $videoHref = '/v/' + video.id;
      $posterSource = $bettyUrl + '/' + video.poster.id
      $('<a>',{
        'class' : $videoItem,
        'href' : $videoHref,
        'data-track-action' : 'Video: Recirc',
        'data-track-label' : $videoHref,
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