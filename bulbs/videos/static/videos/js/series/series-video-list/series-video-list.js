var SeriesVideoList = function () {
  this.$seriesList = $('#series-list');
  this.source = this.$seriesList.data('channel-series');
  this.loadSeries();
};

SeriesVideoList.prototype.loadSeries = function () {
  $.getJSON(this.source, this.seriesFetched.bind(this));
};

SeriesVideoList.prototype.seriesFetched = function (data) {
  var that = this;

  data
    .forEach(function (series) {
      $('<li>',{
        'data-track-action' : 'Series Flyout: Browse',
        'data-track-label' : '/series/' + series.slug,
        'html': $('<a>',{
          'class' : '',
          'href' : '/series/' + series.slug,
          'html' : series.name,
        })
      }).appendTo(that.$seriesList);
    });
};

module.exports = SeriesVideoList;