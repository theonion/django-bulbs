SeriesPage = function() {
  this.$seriesGrid = $('#series-video-list');
  this.seriesSlug = this.$seriesGrid.data('series-slug');
  this.videohubBase = this.$seriesGrid.data('videohub-base');
  var sourceUrl = this.videohubBase + '/api/series/' + this.seriesSlug + '/videos';
  this.seriesVideoGrid = new SeriesVideoGrid(sourceUrl);
  this.fetchSeriesVideos(sourceUrl);
};

SeriesPage.prototype.fetchSeriesVideos = function(sourceUrl) {
  $.getJSON(sourceUrl, this.seriesVideosFetched.bind(this));
};

SeriesPage.prototype.seriesVideosFetched = function(data) {
  this.latestEpisode = new LatestEpisode(data.results);
};

module.exports = SeriesPage;
