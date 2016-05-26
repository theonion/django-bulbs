LatestEpisode = function(videos) {

  this.$videoPlayer = $('bulbs-video');
  this.videoPlayerSrc = this.$videoPlayer.attr('src');
  this.latestVideo = videos[0].id + '.json';
  this.$videoPlayer.attr('src', this.videoPlayerSrc + this.latestVideo);

};

module.exports = LatestEpisode;