LatestEpisode = function(videos) {

  this.$videoPlayer = $('bulbs-video');
  this.videoPlayerSrc = this.$videoPlayer.attr('src');
  this.latestVideo = videos[0].id + '.json';
  this.$videoPlayer.attr('src', this.videoPlayerSrc + this.latestVideo);

  if (typeof this.videoPlayerSrc === 'undefined') {
    throw Error('LatestEpisode requires bulbs-video to have a videohub base url.');
  }
};

module.exports = LatestEpisode;