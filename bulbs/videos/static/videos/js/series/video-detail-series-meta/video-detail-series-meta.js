VideoDetailSeriesMeta = function (seriesSlug) {
  this.seriesSlug = seriesSlug;
  this.$detailGrid = $('#detail-video-list');
  this.videohubBase = this.$detailGrid.data('videohub-base');
  this.$seriesTitle = $('.series-title');
  this.$seriesTitle = $('.series-title');
  this.$seriesImage = $('.series-image');
  this.$seriesEpisodes = $('.series-episodes');
  this.$seriesDescription = $('.series-description');
  this.source = this.videohubBase + '/series/' + this.seriesSlug + '.json';
  this.fetchSeriesMeta();
};

VideoDetailSeriesMeta.prototype.fetchSeriesMeta = function () {
  $.getJSON(this.source, this.seriesMetaFetched.bind(this));
}

VideoDetailSeriesMeta.prototype.seriesMetaFetched = function(data) {
  if (data.total_seasons != 0) {
    $('<li>', {
        'class': 'series-seasons',
        'html' : data.total_seasons + ' Seasons'
    }).insertBefore(this.$seriesEpisodes);
  }

  this.$seriesEpisodes.html(data.total_episodes + ' Episodes');

  this.$seriesDescription.html(data.series_description);

  this.$seriesTitle.html(data.series_name);

  if (data.series_logo) {
    $('<img>', {
        'src' : data.series_logo,
        'alt' : data.series_name
    }).appendTo(this.$seriesImage);
  }
};

module.exports = VideoDetailSeriesMeta;
