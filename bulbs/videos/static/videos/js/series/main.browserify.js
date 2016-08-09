var SeriesMeta = require('./series-meta/series-meta');
var SeriesVideoGrid = require('./series-video-grid/series-video-grid');
var LatestEpisode = require('./series-video-latest-episode/series-video-latest-episode');
var SeriesVideoList = require('./series-video-list/series-video-list');
var PopularSeries = require('./popular-series/popular-series');
var SeriesPage = require('./series-page/series-page');
var VideoDetailPage = require('./video-detail-page/video-detail-page');
var CurrentEpisodeData = require('./current-episode-data/current-episode-data');

$(document).ready(function () {
  if($('body').hasClass('video-detail')) {
    new SeriesMeta();
    new SeriesPage();
  }
  new SeriesVideoList();
  new PopularSeries();
  new VideoDetailPage();
});

