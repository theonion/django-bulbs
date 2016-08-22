SeriesMeta = function() {
  this.$seriesGrid = $('#series-video-list');
  this.videohubBase = this.$seriesGrid.data('videohub-base');
  this.seriesSlug = this.$seriesGrid.data('series-slug') || window.location.href.split('/')[4];
  this.$seriesTitle = $('.series-title');
  this.$seriesImage = $('.series-image');
  this.$seriesEpisodes = $('.series-episodes');
  this.$seriesDescription = $('.series-description');
  this.source = this.videohubBase + '/series/' + this.seriesSlug + '.json';
  this.fetchSeriesMeta();
};

SeriesMeta.prototype.fetchSeriesMeta = function() {
  $.getJSON(this.source, this.seriesMetaFetched.bind(this));
};

SeriesMeta.prototype.seriesMetaFetched = function(data) {

  /* Some shows are standalone and have no seasons */

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
    var isOnion = $('.onion-series-page').length > 0;
    var logo = isOnion  ? data.series_logo_3x1 : data.series_logo;
    $('<img>', {
        'src' : logo,
        'alt' : data.series_name
    }).appendTo(this.$seriesImage);
  }
};

module.exports = SeriesMeta;
