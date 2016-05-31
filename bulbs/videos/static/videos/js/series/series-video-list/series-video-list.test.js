describe('VideoSeriesList', function() {
  var VideoSeriesList = require('./series-video-list');
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
    var videoSeriesList, data;

    beforeEach(function() {
      TestHelper.stub(VideoSeriesList.prototype, 'loadSeries');

      data = [
        { slug: 'av-undercover', name: 'AV Undercover' },
        { slug: 'polite-fight', name: 'Polite Fight' }
      ];

      videoSeriesList = new VideoSeriesList();
      videoSeriesList.seriesFetched(data);
    });

    it('adds a link for every video series', function() {
      var links = videoSeriesList.$seriesList.find('li a');

      links.each(function(index, link) {
        expect($(link).attr('href')).to.equal('/series/' + data[index].slug);
        expect($(link).html()).to.equal(data[index].name);
      });
    });
  });
});
