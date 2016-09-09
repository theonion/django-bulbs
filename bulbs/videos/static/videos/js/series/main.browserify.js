/* eslint no-new: 0*/
var SeriesMeta = require('./series-meta/series-meta');
var SeriesVideoList = require('./series-video-list/series-video-list');
var PopularSeries = require('./popular-series/popular-series');
var SeriesPage = require('./series-page/series-page');
var VideoDetailPage = require('./video-detail-page/video-detail-page');

$(document).ready(function () {
  if($('body').hasClass('video-detail')) {
    new SeriesMeta();
    new SeriesPage();
  }
  new SeriesVideoList();
  new PopularSeries();
  new VideoDetailPage();
});

