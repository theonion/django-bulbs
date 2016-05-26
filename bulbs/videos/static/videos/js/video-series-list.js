var VideoSeriesList = function () {
  this.$seriesList = $('#series-list');
  this.source = this.$seriesList.data('channel-series');
  this.init();
};

VideoSeriesList.prototype.init = function () {
  this.loadSeries();
};

VideoSeriesList.prototype.loadSeries = function () {
  $.getJSON(this.source, this.seriesFetched.bind(this));
};

VideoSeriesList.prototype.seriesFetched = function (data) {
  var that = this;
  
  data
    .forEach(function (series) {
      $('<li>',{
        'class' : '',
        'data-track-action' : 'Video: Series',
        'data-track-label' : '/series/' + series.slug,
        'html': $('<a>',{
          'class' : '',
          'href' : '/series/' + series.slug,
          'html' : series.name,
        })
      }).appendTo(that.$seriesList);
    });
};

module.exports = VideoSeriesList;