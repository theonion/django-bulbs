describe('LatestEpisode', function() {

  var LatestEpisode = require('./series-video-latest-episode');
  var videos = [
    { id: 5400, title: 'A Show About Music', poster: { id: 1234 } },
    { id: 6000, title: 'A Show About Movies', poster: { id: 1235 } }
  ];
  var videoPlayer;

  afterEach(function () {
    videoPlayer.remove();
  });

  context('normal functionality', function () {

    beforeEach(function() {
      videoPlayerSrc = 'http://onionstudios.com/';
      videoPlayer = $('<bulbs-video src="' + videoPlayerSrc + '">');

      $('body').append(videoPlayer);

      latestEpisode = new LatestEpisode(videos);
    });

    it('adds most recent video in series to player', function() {
      expect($(videoPlayer).attr('src')).to.equal(videoPlayerSrc + videos[0].id + '.json');
    });

  });

  context('should fail when', function () {

    it('not provided videohub base url', function() {
      videoPlayer = $('<bulbs-video>');
      $('body').append(videoPlayer);
      var subject = sinon.spy(LatestEpisode);

      expect(function () {
        new subject(videos);
      }).to.throw('LatestEpisode requires bulbs-video to have a videohub base url.');
    });
  });

});