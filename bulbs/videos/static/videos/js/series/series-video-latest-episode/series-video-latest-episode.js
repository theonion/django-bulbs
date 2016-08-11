LatestEpisode = function(videos) {

  this.$videoPlayer = $('bulbs-video');
  this.$latestVideoTitle = $('#latest-video-title');
  this.$latestVideoDescription = $('#latest-video-description');
  this.$latestVideoShareTools = $('.latest-video-share-tools');
  this.$videohubBaseUrl = this.$videoPlayer.data('videohub-base');
  this.latestEpisode = videos[0].id + '.json';
  this.latestEpisodeHref = '/v/' + videos[0].id;
  this.latestVideoTitle = videos[0].title;

  this.$videoPlayer.attr('src', this.$videohubBaseUrl + '/video/' + this.latestEpisode);

  this.$latestVideoShareTools.attr('share-url',
   'http://' + $(this.$latestVideoShareTools).attr('share-url') + this.latestEpisodeHref);
  this.$latestVideoShareTools.attr('share-title', this.latestVideoTitle);

  $('<a>', {
      'href' : this.latestEpisodeHref,
      'data-track-action' : 'Single Series: Latest Episode Title',
      'data-track-label' : this.latestEpisodeHref,
      'html' : '<h2>' + this.latestVideoTitle + '</h2>'

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
