SeriesVideoGrid = function (videos, selector) {

  this.$seriesGrid = $(selector || '#series-video-list');
  this.$carousel = $('bulbs-carousel-slider bulbs-carousel-track');
  this.bettyUrl = this.$seriesGrid.data('bettyUrl');

  if (typeof this.bettyUrl === 'undefined') {
    throw Error('SeriesVideoGrid requires series-video-list to have a data-betty-url attribute.');
  }

  this.appendVideos(videos);
};

SeriesVideoGrid.prototype.appendVideos = function (videos) {
  var that = this;

  videos
    .forEach(function (video) {

    var videoTitle = video.title;
    var videoHref = '/v/' + video.id;
    var posterSource = that.bettyUrl + '/' + video.poster.id + '/16x9/480.jpg';

    var anchor = $('<a>',{
      'class' : 'video-item',
      'href' : videoHref,
      'data-track-action' : 'Single Series: Episodes',
      'data-track-label' : videoHref,
      'html': $('<figure>',{
        'class' : 'content',
        'html' : '<div class="image"><bulbs-video-play-button></bulbs-video-play-button><img src="' + posterSource + '"></div>',
      }).add($('<p>',{
        'html' : videoTitle
      }))
    });

    if (that.$seriesGrid.length > 0) {
      anchor.appendTo(that.$seriesGrid);
    }

    if (that.$carousel.length > 0) {
      $('<bulbs-carousel-item>').html(anchor).appendTo(that.$carousel);
    }
  });
};

module.exports = SeriesVideoGrid;
