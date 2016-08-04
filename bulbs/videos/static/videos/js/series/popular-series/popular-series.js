var PopularSeries = function () {
  this.$popularSeries = $('#popular-series');
  this.source = this.$popularSeries.data('channel-series');
  this.loadPopularSeries();
};

PopularSeries.prototype.loadPopularSeries = function () {
  $.getJSON(this.source, this.popularSeriesFetched.bind(this));
};

PopularSeries.prototype.loadSeriesData = function (seriesSlug) {
  var videohubBase = $('#popular-series').data('videohub-base');
  var queryString = videohubBase + '/series/' + seriesSlug + '.json';
  $.getJSON(queryString, this.seriesDataFetched.bind(this));
};

PopularSeries.prototype.popularSeriesFetched = function (data) {
  var currentSeriesSlug = this.$popularSeries.data('series-slug');
  data.forEach(function (series, index) {
    if(series.slug === currentSeriesSlug) {
      data.splice(index, 0);
    }
  });

  for(var i = 0; i < data.length; i++) {
    var series = data[i];
    this.loadSeriesData(series.slug);
  };
};

PopularSeries.prototype.seriesDataFetched = function (data) {
  // build markup for popular series
  var seriesLink = '<a \
                        class="popular-series-item" \
                        href="/series/' + data.series_slug + '" \
                        data-track-action="Single Series: Popular Series" \
                        data-track-label="' + data.series_slug + '"></a>';
  var $container = $(seriesLink);
  var seriesTitle = '<div class="popular-series-item-title">' +
    data.series_name + '</div>';
  var seriesEpisodesCount = '<div class="popular-series-item-episodes">'
    + data.total_episodes + ' Videos</div>';
  if (data.total_seasons > 0) {
    var seriesSeasonsCount = '<div class="popular-series-item-seasons">'
    + data.total_seasons + ' Seasons</div>';
  } else {
    var seriesSeasonsCount = '';
  }
  var seriesLogo = '<div class="series-logo"><img src="' + data.series_logo + '" alt="' + data.series_name + '"></img></div>';

  var seriesMeta = seriesLogo + seriesTitle + seriesSeasonsCount + seriesEpisodesCount;

  $container.append(seriesMeta);
  $('#popular-series').append($container);
};

module.exports = PopularSeries;
