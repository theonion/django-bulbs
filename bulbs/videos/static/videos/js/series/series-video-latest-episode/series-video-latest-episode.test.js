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

  var videohubBaseUrl = 'http://onionstudios.com';
  var videoPlayer = $('<bulbs-video data-videohub-base="' + videohubBaseUrl + '">');
  var latestVideoTitle = '<div id="latest-video-title"></div>';
  var latestVideoDescription = '<div id="latest-video-description"></div>';
  var latestVideoShareTools = '<share-tools \
                                  class="latest-video-share-tools" \
                                  share-url="foo.bar" \
                              </share-tools>';

  context('normal functionality', function () {

    beforeEach(function() {

      $('body').append(videoPlayer);
      $('body').append(latestVideoTitle);
      $('body').append(latestVideoDescription);
      $('body').append(latestVideoShareTools);

      latestEpisode = new LatestEpisode(videos);
    });

    afterEach(function() {
      videoPlayer.remove();
      $('#latest-video-title').remove();
      $('#latest-video-description').remove();
      $('share-tools').remove();
    });

    it('adds most recent video in series to player', function() {
      var expected = videohubBaseUrl + '/video/' + videos[0].id + '.json';
      expect($(videoPlayer).attr('src')).to.equal(expected);
    });

    it('appends the latest video title', function() {
      var videoTitle = $('#latest-video-title h2').html()
      expect(videoTitle).to.equal("A Show About Music");
    });

    it('appends the latest video description', function() {
      var videoDescription = $('#latest-video-description p').html()
      expect(videoDescription).to.equal("it sucks");
    });

    describe('share-tools', function () {
      it('appends the latest video title', function() {
        var videoShareToolsTitle = $('.latest-video-share-tools').attr('share-title');
        expect(videoShareToolsTitle).to.equal("A Show About Music");
      });

      it('appends the latest video url', function() {
        var videoShareToolsUrl = $('.latest-video-share-tools').attr('share-url');
        expect(videoShareToolsUrl).to.equal("http://foo.bar/v/5400");
      });
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
      $('bulbs-video').remove();
    });
  });

});
