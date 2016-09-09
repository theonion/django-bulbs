var SeriesVideoGrid = require('../series-video-grid/series-video-grid');
var VideoDetailSeriesMeta = require('../video-detail-series-meta/video-detail-series-meta');
var CurrentEpisodeData = require('../current-episode-data/current-episode-data');

var VideoDetailPage = function () {
  this.$detailGrid = $('#detail-video-list');
  this.currentVideoSrc = $('bulbs-video').attr('src');
  this.videohubBase = this.$detailGrid.data('videohub-base');
  this.fetchVideo();
};

VideoDetailPage.prototype.fetchVideo = function () {
  $.getJSON(this.currentVideoSrc, this.videoDataFetched.bind(this));
};

VideoDetailPage.prototype.videoDataFetched = function (videoObject) {
  var source = this.videohubBase + '/api/series/' + videoObject.series_slug + '/videos';
  new CurrentEpisodeData(videoObject); // eslint-disable-line no-new
  new VideoDetailSeriesMeta(videoObject.series_slug); // eslint-disable-line no-new
  this.seriesVideoGrid = new SeriesVideoGrid(source, '#detail-video-list');
};

module.exports = VideoDetailPage;
