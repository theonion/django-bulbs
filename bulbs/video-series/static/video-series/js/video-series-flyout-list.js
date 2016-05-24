var VideoSeriesFlyoutList = function() {
  this.$seriesList = $('#series-list');
  this.channelSlug = this.$seriesList.data('channel-slug');
  this.source = 'http://www.onionstudios.com/channel/' + this.channelSlug + '/series.json';
  this.init();
};

VideoSeriesFlyoutList.prototype.init = function() {
  this.loadSeries();
};

VideoSeriesFlyoutList.prototype.loadSeries = function() {
  $.getJSON(this.source, this.seriesFetched.bind(this));
};

VideoSeriesFlyoutList.prototype.seriesFetched = function(data) {
  var that = this;

  $.each(data.series, function(index, channel) {
    var seriesTitle = series.title;
    $('<a>',{
      'class' : 'foo',
      'href' : '/series/',
      'data-track-action' : 'Video: Recirc',
      'data-track-label' : 'Foo',
      'html': $('<li>',{
        'class' : '',
        'html' : 'series-title',
      })
    }).appendTo(that.$seriesList);
  });

};

new VideoSeriesFlyoutList();