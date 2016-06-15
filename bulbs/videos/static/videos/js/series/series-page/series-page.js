SeriesPage = function() {
  this.$seriesGrid = $('#series-video-list');
  this.seriesSlug = this.$seriesGrid.data('series-slug');
  this.videohubBase = this.$seriesGrid.data('videohub-base');
  this.source = this.videohubBase + '/api/series/' + this.seriesSlug + '/videos';
  this.fetchSeriesVideos();
};

SeriesPage.prototype.fetchSeriesVideos = function() {
  $.getJSON(this.source, this.seriesVideosFetched.bind(this));
};

SeriesPage.prototype.seriesVideosFetched = function(data) {
  this.latestEpisode = new LatestEpisode(data.results);
  this.seriesVideoGrid = new SeriesVideoGrid(data.results);
};

module.exports = SeriesPage;