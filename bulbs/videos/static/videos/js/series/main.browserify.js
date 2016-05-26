var SeriesMeta = require('./series-meta/series-meta');
var SeriesVideoList = require('./series-video-list/series-video-list');
var SeriesVideoGrid = require('./series-video-grid/series-video-grid');
var LatestEpisode = require('./series-video-latest-episode/series-video-latest-episode');

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

$(document).ready(function () {
  new SeriesMeta();
  new SeriesPage();
  new SeriesVideoList();
});