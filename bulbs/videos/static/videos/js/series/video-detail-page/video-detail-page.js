VideoDetailPage = function() {
  this.VideoDetailSeriesMeta = require('../video-detail-series-meta/video-detail-series-meta');
  this.$detailGrid = $('#detail-video-list');
  this.currentVideoSrc = $('bulbs-video').attr('src');
  this.videohubBase = this.$detailGrid.data('videohub-base');
  this.fetchSeriesVideo();
};

VideoDetailPage.prototype.fetchSeriesVideo = function() {
  $.getJSON(this.currentVideoSrc, this.videoDataFetched.bind(this));
};

VideoDetailPage.prototype.videoDataFetched = function(videoObject) {
  var source = this.videohubBase + '/api/series/' + videoObject.series_slug + '/videos';
  new this.VideoDetailSeriesMeta(videoObject.series_slug);
  $.getJSON(source, this.videoSeriesFetched.bind(this, videoObject.id));
};

VideoDetailPage.prototype.videoSeriesFetched = function(videoObjectId, data) {
  var video = data.results.find(function findVideo(video) { return video.id === videoObjectId })
  new CurrentEpisodeData(video);
  this.seriesVideoGrid = new SeriesVideoGrid(data.results, '#detail-video-list');
};

module.exports = VideoDetailPage;
