describe('SeriesMeta', function() {
  var SeriesMeta = require('./series-meta');
  var seriesContainer;

  beforeEach(function() {
    seriesContainer = $('<div id="seriesContainer">')
      .append('<div id="series-video-list">')
      .append('<div class="series-title">')
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
        series_name: 'AV Undercover'
      };
      TestHelper.stub(SeriesMeta.prototype, 'fetchSeriesMeta');
      seriesMeta = new SeriesMeta();
      seriesMeta.seriesMetaFetched(data);
    });

    it('populates the series description', function() {
      expect(seriesMeta.$seriesDescription.html()).to.eql(data.series_description);
    });

    it('populates the series title', function() {
      expect(seriesMeta.$seriesTitle.html()).to.eql(data.series_name);
    });
  });
});
