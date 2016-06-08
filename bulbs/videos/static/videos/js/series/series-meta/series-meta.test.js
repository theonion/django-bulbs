describe('SeriesMeta', function() {
  var SeriesMeta = require('./series-meta');
  var seriesContainer;

  beforeEach(function() {
    seriesContainer = document.createElement('div');

    seriesVideoList = document.createElement('div');
    seriesVideoList.id = 'series-video-list';
    seriesContainer.appendChild(seriesVideoList);

    var seriesTitle = document.createElement('div');
    seriesTitle.class= 'series-title';
    seriesContainer.appendChild(seriesTitle);

    var seriesDescription = document.createElement('div');
    seriesDescription.class = 'series-description';
    seriesContainer.appendChild(seriesDescription);

    $('body').append(seriesContainer);
  });

  afterEach(function() {
    document.body.removeChild(seriesContainer);
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
      expect($('.series-description').html()).to.eql(data.series_description);
    });

    it('populates the series title', function() {
      expect(seriesMeta.$seriesTitle.html()).to.eql(data.series_name);
    });
  });
});
