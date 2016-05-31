SeriesMeta = function() {
  this.$seriesGrid = $('#series-video-list');
  this.videohubBase = this.$seriesGrid.data('videohub-base');
  this.seriesSlug = this.$seriesGrid.data('series-slug');
  this.$seriesTitle = $('#series-title');
  this.source = this.videohubBase + '/series/' + this.seriesSlug + '.json';
  this.fetchSeriesMeta();
};

SeriesMeta.prototype.fetchSeriesMeta = function() {
  $.getJSON(this.source, this.seriesMetaFetched.bind(this));
};

SeriesMeta.prototype.seriesMetaFetched = function(data) {
  $('#series-description').html(data.series_description);
  this.$seriesTitle.html(data.series_name);
  /* Commenting this out until we resolve logo crop issue
  if (data.series_logo) {
    $('<img>', {
        'id' : 'series-logo',
        'src' : data.series_logo,
        'alt' : data.series_name
    }).appendTo(this.$seriesTitle);
  } else {
    this.$seriesTitle.html(data.series_name);
  }*/
};

module.exports = SeriesMeta;