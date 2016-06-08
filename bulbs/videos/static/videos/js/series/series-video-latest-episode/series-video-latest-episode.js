LatestEpisode = function(videos) {

  this.$videoPlayer = $('bulbs-video');
  this.$latestVideoTitle = $('#latest-video-title');
  this.videoPlayerSrc = this.$videoPlayer.attr('src');
  this.latestVideo = videos[0].id + '.json';
  this.$videoPlayer.attr('src', this.videoPlayerSrc + this.latestVideo);

  this.$latestVideoTitle.html(videos[0].title);

  if (typeof this.videoPlayerSrc === 'undefined') {
    throw Error('LatestEpisode requires bulbs-video to have a videohub base url.');
  }
};

module.exports = LatestEpisode;