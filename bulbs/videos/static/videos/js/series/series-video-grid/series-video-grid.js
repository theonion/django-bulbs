SeriesVideoGrid = function (videos) {

  this.$seriesGrid = $('#series-video-list');
  this.bettyUrl = this.$seriesGrid.data('betty-url');

  var that = this;

  videos
    .forEach(function (video) {
    var videoTitle = video.title;
    var videoHref = '/v/' + video.id;
    var posterSource = that.bettyUrl + '/' + video.poster.id + '/16x9/480.jpg';
    $('<a>',{
        'class' : 'video-item',
        'href' : videoHref,
        'data-track-action' : 'Series: Recirc',
        'data-track-label' : videoHref,
        'html': $('<figure>',{
          'class' : 'content',
          'html' : '<div class="image"><bulbs-video-play-button></bulbs-video-play-button><img src="' + posterSource + '"></div>',
        }).add($('<p>',{
          'html' : videoTitle
        }))
      }).appendTo(that.$seriesGrid);
    });
};

module.exports = SeriesVideoGrid;