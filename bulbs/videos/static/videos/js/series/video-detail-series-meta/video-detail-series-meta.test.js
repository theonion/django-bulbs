describe('SeriesMeta', function() {
  var VideoDetailSeriesMeta = require('./video-detail-series-meta');
  var seriesSummary;

  beforeEach(function() {
     $('body').append(
        '<div id="detail-video-list" data-videohub-base="//foobar.com">'
      );
      seriesSummary = $('<a href="foo.bar" class="series-summary">')
        .append('<div class="series-logo">')
        .append('<div class="series-image">')
        .append('<div class="series-title">')
        .append('<div class="series-episodes">')
        .append('<div class="series-description">');

    $('body').append(seriesSummary);
  });

  afterEach(function() {
    seriesSummary.remove();
    $('#detail-video-list').remove();
  });

  describe('#seriesMetaFetched', function() {
    var videoDetailSeriesMeta, data;

    beforeEach(function() {
      data = {
        series_description: 'blah blah blah',
        series_name: 'series one',
        total_seasons: 2,
        total_episodes: 2,
        series_logo: 'www.coolcat.com/pix/5'
      };
      TestHelper.stub(VideoDetailSeriesMeta.prototype, 'fetchSeriesMeta');
      videoDetailSeriesMeta = new VideoDetailSeriesMeta('this-is-a-slug');
      videoDetailSeriesMeta.seriesMetaFetched(data);
    });

    it('populates the series description', function() {
      var seriesDescriptionHtml = videoDetailSeriesMeta.$seriesDescription.html();
      var expected = data.series_description;
      expect(seriesDescriptionHtml).to.eql(expected);
    });

    it('populates the series title', function() {
      var seriesTitleHtml = videoDetailSeriesMeta.$seriesTitle.html();
      var expected = data.series_name;
      expect(seriesTitleHtml).to.eql(expected);
    });

    it('populates the series episodes', function() {
      var seriesEpisodesHtml = videoDetailSeriesMeta.$seriesEpisodes.html();
      var expected = '2 Episodes';
      expect(seriesEpisodesHtml).to.eql(expected);
    });

    it('populates the series seasons', function() {
      var seriesSeasonsHtml = $('.series-seasons').html();
      var expected = '2 Seasons';
      expect(seriesSeasonsHtml).to.eql(expected);
    });

    it('populates the series logo', function() {
      var seriesImgSrc = $('.series-image img').attr('src');
      var expected = data.series_logo;
      expect(seriesImgSrc).to.eql(expected);
    });

    it('appends href to seires summary a tag', function() {
      var seriesSummaryHref = videoDetailSeriesMeta.$seriesSummary.attr('href');
      var expected = 'http://foo.bar/series/this-is-a-slug';
      expect(seriesSummaryHref).to.eql(expected);
    });
  });

  describe('#seriesMetaFetched with no seasons', function() {
    it('does not populate series seasons if there are none', function() {
      data = { total_seasons: 0 };
      TestHelper.stub(VideoDetailSeriesMeta.prototype, 'fetchSeriesMeta');
      videoDetailSeriesMeta = new VideoDetailSeriesMeta('this-is-a-slug');
      videoDetailSeriesMeta.seriesMetaFetched(data);
      expect($('.series-seasons').length).to.eql(0);
    });
  });
});
