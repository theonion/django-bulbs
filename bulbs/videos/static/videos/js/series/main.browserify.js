var SeriesMeta = require('./series-meta/series-meta');
var SeriesVideoGrid = require('./series-video-grid/series-video-grid');
var LatestEpisode = require('./series-video-latest-episode/series-video-latest-episode');
var SeriesVideoList = require('./series-video-list/series-video-list');
var SeriesPage = require('./series-page/series-page');

$(document).ready(function () {
  new SeriesMeta();
  new SeriesPage();
  new SeriesVideoList();
});