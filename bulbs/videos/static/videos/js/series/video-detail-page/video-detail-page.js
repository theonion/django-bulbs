var SeriesVideoGrid = require('../series-video-grid/series-video-grid');
var VideoDetailSeriesMeta = require('../video-detail-series-meta/video-detail-series-meta');

VideoDetailPage = function() {
  this.$detailGrid = $('#detail-video-list');
  this.currentVideoSrc = $('bulbs-video').attr('src');
  this.videohubBase = this.$detailGrid.data('videohub-base');
  this.fetchVideo();
};

VideoDetailPage.prototype.fetchVideo = function() {
  $.getJSON(this.currentVideoSrc, this.videoDataFetched.bind(this));
};

VideoDetailPage.prototype.videoDataFetched = function(videoObject) {
  var source = this.videohubBase + '/api/series/' + videoObject.series_slug + '/videos';
  new CurrentEpisodeData(videoObject);
  new VideoDetailSeriesMeta(videoObject.series_slug);
  this.seriesVideoGrid = new SeriesVideoGrid(source, '#detail-video-list');
};

module.exports = VideoDetailPage;
