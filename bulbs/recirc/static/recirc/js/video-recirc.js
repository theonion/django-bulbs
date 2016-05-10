var VideoRecircList = function() {
  this.videoItem = 'video-item';
  this.$videoRecircList = $('#video-list');
  this.$videoListTitle = $('#video-list-title');
  this.bettyUrl = this.$videoRecircList.data('betty-url');
  this.source = this.$videoRecircList.data('source');
  this.recircCount = this.$videoRecircList.data('count');
  this.init();
};

VideoRecircList.prototype.init = function() {
  this.loadVideoRecirc();
};

VideoRecircList.prototype.loadVideoRecirc = function() {
  $.getJSON(this.source, this.videoRecircFetched.bind(this));
};

VideoRecircList.prototype.videoRecircFetched = function(data) {
  var that = this;

  that.$videoListTitle.html('More From ' + data.series.name);
  
  $.each(data.videos.slice(0,this.recircCount), function(index, video) {
    var videoTitle = video.title;
    var videoHref = '/v/' + video.id;
    var posterSource = that.bettyUrl + '/' + video.poster.id;
    $('<a>',{
      'class' : that.videoItem,
      'href' : videoHref,
      'data-track-action' : 'Video: Recirc',
      'data-track-label' : videoHref,
      'html': $('<figure>',{
        'class' : 'content',
        'html' : '<div class="image"><bulbs-video-play-button></bulbs-video-play-button><img src="' + posterSource + '/16x9/480.jpg"></div>',
      }).add($('<p>',{
        'html' : videoTitle
      }))
    }).appendTo(that.$videoRecircList);
  });
};

new VideoRecircList();