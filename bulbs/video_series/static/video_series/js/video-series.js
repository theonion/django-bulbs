var SeriesVideoGrid = require('./series-video-grid.js');
var LatestEpisode = require('./latest-episode.js');

SeriesPage = function(seriesSlug) {
  this.fetchSeriesVideos(seriesSlug)
};

SeriesPage.prototype.fetchSeriesVideos = function(seriesSlug) {
  // Make request to: 
  // http://www.onionstudios.com/api/series/film-club/videos`
};

SeriesPage.prototype.seriesVideosFetched = function(data) {
  // Make request to: 
  this.latestEpisode = new LatestEpisode(data.videos);
  this.seriesVideoGrid = new SeriesVideoGrid(data.videos);
};

module.exports = SeriesPage;

LatestEpisode = function(videos) {
  // 1. fetch videos[0]
  // 2. Add <bulbs-video> to the DOM with the video id
};

module.exports = LatestEpisode;

SeriesVideoGrid = function(videos) {
  // Add grid to the DOM
};

module.exports = SeriesVideoGrid;