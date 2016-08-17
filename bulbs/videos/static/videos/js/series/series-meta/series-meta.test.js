describe('SeriesMeta', function() {
  var SeriesMeta = require('./series-meta');
  var seriesContainer;

  beforeEach(function() {
    seriesContainer = $('<div id="seriesContainer">')
      .append('<div id="series-video-list">')
      .append('<div class="series-title">')
      .append('<div class="series-logo">')
      .append('<div class="series-image">')
      .append('<div class="series-description">');

    $('body').append(seriesContainer);
  });

  afterEach(function() {
    seriesContainer.remove();
  });

  describe('#seriesMetaFetched', function() {
    var seriesMeta, data;

    beforeEach(function() {
      data = {
        series_description: 'AV Undercover description',
        series_name: 'AV Undercover',
        series_logo: 'www.picture.com/regular-picture',
        series_logo_3x1: 'www.picture.com/three-by-one'
      };
      TestHelper.stub(SeriesMeta.prototype, 'fetchSeriesMeta');
      seriesMeta = new SeriesMeta();
      seriesMeta.seriesMetaFetched(data);
    });

    it('populates the series description', function() {
      var seriesDescriptionHtml = seriesMeta.$seriesDescription.html();
      var expected = data.series_description;
      expect(seriesDescriptionHtml).to.eql(expected);
    });

    it('populates the series title', function() {
      var seriesTitleHtml = seriesMeta.$seriesTitle.html();
      var expected = data.series_name;
      expect(seriesTitleHtml).to.eql(expected);
    });

    it('populates the series logo', function() {
      var seriesLogoSrc = $('.series-image img').attr('src');
      var expected = data.series_logo;
      expect(seriesLogoSrc).to.eql(expected);
    });
  });

  describe('not avclub', function () {
    it('populates series logo w/ 3x1', function () {
      // setup
      $('body').append('<div class="onion-series-page">');
      data = {
        series_logo: 'www.picture.com/regular-picture',
        series_logo_3x1: 'www.picture.com/three-by-one'
      };
      TestHelper.stub(SeriesMeta.prototype, 'fetchSeriesMeta');
      seriesMeta = new SeriesMeta();
      seriesMeta.seriesMetaFetched(data);

      var seriesLogoSrc = $('.series-image img').attr('src');
      var expected = data.series_logo_3x1;
      expect(seriesLogoSrc).to.eql(expected);

      // cleanup
      $('.onion-series-page').remove();
    });
  });
});
