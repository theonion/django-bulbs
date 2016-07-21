LatestEpisode = function(videos) {

  this.$videoPlayer = $('bulbs-video');
  this.$latestVideoTitle = $('#latest-video-title');
  this.$latestVideoDescription = $('#latest-video-description');
  this.$videohubBaseUrl = this.$videoPlayer.data('videohub-base');
  this.latestEpisode = videos[0].id + '.json';
  this.latestEpisodeHref = '/v/' + videos[0].id;

  this.$videoPlayer.attr('src', this.$videohubBaseUrl + '/video/' + this.latestEpisode);

  $('<a>', {
      'href' : this.latestEpisodeHref,
      'data-track-action' : 'Single Series: Latest Episode Title',
      'data-track-label' : this.latestEpisodeHref,
      'html' : '<h2>' + videos[0].title + '</h2>'

  }).appendTo(this.$latestVideoTitle);

  if (videos[0].description) {
    $('<p>' +  videos[0].description + '</p>')
      .appendTo(this.$latestVideoDescription);
  }

  if (typeof this.$videohubBaseUrl === 'undefined') {
    throw Error('LatestEpisode requires bulbs-video to have a videohub base url.');
  }
};

module.exports = LatestEpisode;
