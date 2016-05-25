var SeriesPage = function () {
  this.$seriesRecircList = $('#series-video-list');
  this.bettyUrl = this.$seriesRecircList.data('betty-url');
  this.source = this.$seriesRecircList.data('series-content');
  this.init();
};

SeriesPage.prototype.init = function () {
  this.loadSeriesRecirc();
};

SeriesPage.prototype.loadSeriesRecirc = function () {
  $.getJSON(this.source, this.seriesRecircFetched.bind(this));
};

SeriesPage.prototype.seriesRecircFetched = function (data) {
  var that = this;

  data.results
    .forEach(function (video) {
    var videoTitle = video.title;
    var videoHref = '/v/' + video.id;
    var posterSource = that.bettyUrl + '/' + video.poster.id;
      $('<a>',{
        'class' : 'video-item',
        'href' : videoHref,
        'data-track-action' : 'Series: Recirc',
        'data-track-label' : videoHref,
        'html': $('<figure>',{
          'class' : 'content',
          'html' : '<div class="image"><bulbs-video-play-button></bulbs-video-play-button><img src="' + posterSource + '/16x9/480.jpg"></div>',
        }).add($('<p>',{
          'html' : videoTitle
        }))
      }).appendTo(that.$seriesRecircList);
    });
};

new SeriesPage();