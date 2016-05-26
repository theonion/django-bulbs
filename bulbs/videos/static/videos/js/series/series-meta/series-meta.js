SeriesMeta = function() {
  this.$seriesGrid = $('#series-video-list');
  this.videohubBase = this.$seriesGrid.data('videohub-base');
  this.seriesSlug = this.$seriesGrid.data('series-slug');
  this.source = this.videohubBase + '/series/' + this.seriesSlug + '.json';
  this.fetchSeriesMeta();
};

SeriesMeta.prototype.fetchSeriesMeta = function() {
  $.getJSON(this.source, this.seriesMetaFetched.bind(this));
};

SeriesMeta.prototype.seriesMetaFetched = function(data) {
  $('#series-description').html(data.series_description);
  $('#series-title').html(data.series_name);
  console.log(data);
};

module.exports = SeriesMeta;