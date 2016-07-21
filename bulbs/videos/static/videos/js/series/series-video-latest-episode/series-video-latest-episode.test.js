describe('LatestEpisode', function() {

  var LatestEpisode = require('./series-video-latest-episode');
  var videos = [
    {
      id: 5400,
      title: 'A Show About Music',
      poster: { id: 1234 },
      description: 'it sucks'
    },
    { id: 6000, title: 'A Show About Movies', poster: { id: 1235 } }
  ];
  var videoPlayer;

  afterEach(function () {
    videoPlayer.remove();
  });

  context('normal functionality', function () {

    beforeEach(function() {
      videohubBaseUrl = 'http://onionstudios.com';
      videoPlayer = $('<bulbs-video data-videohub-base="' + videohubBaseUrl + '">');

      $('body').append(videoPlayer);
      $('body').append('<div id="latest-video-title"></div>');
      $('body').append('<div id="latest-video-description"></div>');

      latestEpisode = new LatestEpisode(videos);
    });

    it('adds most recent video in series to player', function() {
      expect($(videoPlayer).attr('src')).to.equal(videohubBaseUrl + '/video/' + videos[0].id + '.json');
    });

    it('appends the latest video title', function() {
      var videoTitle = $('#latest-video-title h2').html()
      expect(videoTitle).to.equal("A Show About Music");
    });

    it('appends the latest video description', function() {
      var videoDescription = $('#latest-video-description p').html()
      expect(videoDescription).to.equal("it sucks");
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
