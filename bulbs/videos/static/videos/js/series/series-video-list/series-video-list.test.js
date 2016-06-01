describe('SeriesVideoList', function() {
  var SeriesVideoList = require('./series-video-list');
  var seriesList;

  beforeEach(function() {
    seriesList = document.createElement('div');
    seriesList.id = 'series-list';

    $('body').append(seriesList);
  });

  afterEach(function() {
    document.body.removeChild(seriesList);
  });

  describe('#seriesFetched', function() {
    var seriesVideoList, data;

    beforeEach(function() {
      TestHelper.stub(SeriesVideoList.prototype, 'loadSeries');

      data = [
        { slug: 'av-undercover', name: 'AV Undercover' },
        { slug: 'polite-fight', name: 'Polite Fight' }
      ];

      seriesVideoList = new SeriesVideoList();
      seriesVideoList.seriesFetched(data);
    });

    it('adds a link for every video series', function() {
      var links = seriesVideoList.$seriesList.find('li a');

      links.each(function(index, link) {
        expect($(link).attr('href')).to.equal('/series/' + data[index].slug);
        expect($(link).html()).to.equal(data[index].name);
      });
    });
  });
});
