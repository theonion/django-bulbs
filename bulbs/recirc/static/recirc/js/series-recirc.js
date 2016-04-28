var VideoRecircList = function() {
  $videoRecircList = $('#video-list');
  this.videoItem = 'video-item';
  this.bettyUrl = $videoRecircList.data('betty-url');
  this.source = $videoRecircList.data('source');
  this.recircCount = $videoRecircList.data('count');
  this.init();
};

VideoRecircList.prototype.init = function() {
  this.loadVideoRecirc();
};

VideoRecircList.prototype.loadVideoRecirc = function() {
  $.getJSON(this.source, function(data) {
    $.each(data.results.slice(0,this.recircCount), function(index, video) {
      var videoTitle = video.title;
      var videoHref = '/v/' + video.id;
      var posterSource = $bettyUrl + '/' + video.poster.id;
      $('<a>',{
        'class' : videoItem,
        'href' : videoHref,
        'data-track-action' : 'Video: Recirc',
        'data-track-label' : videoHref,
        'html': $('<figure>',{
          'class' : 'content',
          'html' : '<div class="image"><img src="' + posterSource + '/16x9/480.jpg"></div>'
        }).add($('<p>',{
          'html' : videoTitle
        }))
      }).appendTo($videoRecircList);
    });
  });
};

new VideoRecircList();