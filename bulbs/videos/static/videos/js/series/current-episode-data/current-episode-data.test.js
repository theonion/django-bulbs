describe('CurrentEpisodeData', function () {
  var CurrentEpisodeData = require('./current-episode-data');
  var video = {
      id: 5400,
      title: 'A Show About Music',
      poster: { id: 1234 },
      description: 'it sucks'
    };
  var videoPlayer;

  var videohubBaseUrl = 'http://onionstudios.com';
  var videoPlayer = $('<bulbs-video data-videohub-base="' + videohubBaseUrl + '">');
  var currentVideoTitle = '<div id="current-video-title"></div>';
  var currentVideoDescription = '<div id="current-video-description"></div>';
  var currentVideoShareTools = '<share-tools \
                                  class="current-video-share-tools" \
                                  share-url="foo.bar" \
                              </share-tools>';

  context('normal functionality', function () {

    beforeEach(function() {

      $('body').append(videoPlayer);
      $('body').append(currentVideoTitle);
      $('body').append(currentVideoDescription);
      $('body').append(currentVideoShareTools);

      currentEpisodeData = new CurrentEpisodeData(video);
    });

    afterEach(function() {
      videoPlayer.remove();
      $('#current-video-title').remove();
      $('#current-video-description').remove();
      $('share-tools').remove();
    });

    it('adds current video in series to player', function() {
      var expected = videohubBaseUrl + '/video/' + video.id + '.json';
      expect($(videoPlayer).attr('src')).to.equal(expected);
    });

    it('appends the current video title', function() {
      var videoTitle = $('#current-video-title h2').html()
      expect(videoTitle).to.equal("A Show About Music");
    });

    it('appends the current video description', function() {
      var videoDescription = $('#current-video-description p').html()
      expect(videoDescription).to.equal("it sucks");
    });

    describe('share-tools', function () {
      it('appends the current video title', function() {
        var videoShareToolsTitle = $('.current-video-share-tools').attr('share-title');
        expect(videoShareToolsTitle).to.equal("A Show About Music");
      });

      it('appends the current video url', function() {
        var videoShareToolsUrl = $('.current-video-share-tools').attr('share-url');
        expect(videoShareToolsUrl).to.equal("http://foo.bar/v/5400");
      });
    });
  });

  context('should fail when', function () {

    it('not provided videohub base url', function() {
      videoPlayer = $('<bulbs-video>');
      $('body').append(videoPlayer);
      var subject = sinon.spy(CurrentEpisodeData);

      expect(function () {
        new subject(video);
      }).to.throw('CurrentEpisode requires bulbs-video to have a videohub base url.');
      $('bulbs-video').remove();
    });
  });

});
