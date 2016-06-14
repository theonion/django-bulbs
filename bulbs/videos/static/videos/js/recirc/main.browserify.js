var VideoRecircList = require('./video-recirc-list/video-recirc-list');
var SeriesVideoList = require('../series/series-video-list/series-video-list');

$(document).ready(function () {
  new VideoRecircList();
  new SeriesVideoList();
});