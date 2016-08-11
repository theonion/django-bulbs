CurrentEpisodeData = function(video) {
  this.$videoPlayer = $('bulbs-video');
  this.$currentVideoTitle = $('#current-video-title');
  this.$currentVideoDescription = $('#current-video-description');
  this.$currentVideoShareTools = $('.current-video-share-tools');
  this.$videohubBaseUrl = this.$videoPlayer.data('videohub-base');
  this.currentEpisodeHref = '/v/' + video.id;
  this.currentEpisode = video.id + '.json';
  this.currentVideoTitle = video.title;

  this.$videoPlayer.attr('src', this.$videohubBaseUrl + '/video/' + this.currentEpisode);

  this.$currentVideoShareTools.attr('share-url',
    'http://' + $(this.$currentVideoShareTools).attr('share-url') + this.currentEpisodeHref);
  this.$currentVideoShareTools.attr('share-title', this.currentVideoTitle);

  $('<a>', {
      'href' : this.currentEpisodeHref,
      'data-track-action' : 'Single Series: Current Episode Title',
      'data-track-label' : this.currentEpisodeHref,
      'html' : '<h2>' + this.currentVideoTitle + '</h2>'

  }).appendTo(this.$currentVideoTitle);

  if (video.description) {
    $('<p>' +  video.description + '</p>')
      .appendTo(this.$currentVideoDescription);
  }

  if (typeof this.$videohubBaseUrl === 'undefined') {
    throw Error('CurrentEpisode requires bulbs-video to have a videohub base url.');
  }
};

module.exports = CurrentEpisodeData;
