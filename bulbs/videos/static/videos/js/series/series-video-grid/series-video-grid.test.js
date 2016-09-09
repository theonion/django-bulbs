describe('SeriesVideoGrid', function () {

  var SeriesVideoGrid = require('./series-video-grid');
  var videos = [
    { id: 5400, title: 'A Show About Music', poster: { id: 1234 } },
    { id: 6000, title: 'A Show About Movies', poster: { id: 1235 } },
  ];
  var seriesGrid;

  afterEach(function () {
    seriesGrid.remove();
  });

  context('normal functionality', function () {
    var seriesVideoGrid;
    var bettyUrl;
    beforeEach(function () {
      bettyUrl = 'http://i.onionstatic.com';
      seriesGrid = $('<div id="series-video-list" data-betty-url="' + bettyUrl + '">');

      $('body').append(seriesGrid);

      seriesVideoGrid = new SeriesVideoGrid(videos);
    });

    it('adds a link for every video series', function () {
      var links = seriesVideoGrid.$seriesGrid.find('a');

      links.each(function (index, link) {
        expect($(link).attr('href')).to.equal('/v/' + videos[index].id);
        expect($(link).find('p').html()).to.equal(videos[index].title);
      });
    });

    it('adds a title for every video series', function () {
      var titles = seriesVideoGrid.$seriesGrid.find('a p');

      titles.each(function (index, title) {
        expect($(title).html()).to.equal(videos[index].title);
      });
    });

    it('adds a poster image url for every video series', function () {
      var posters = seriesVideoGrid.$seriesGrid.find('a img');

      posters.each(function (index, poster) {
        expect($(poster).attr('src')).to.equal(bettyUrl + '/' + videos[index].poster.id + '/16x9/480.jpg');
      });
    });
  });

  context('should fail when', function () {

    it('not provided betty url data attr', function () {
      seriesGrid = $('<div id="series-video-list">');
      $('body').append(seriesGrid);
      var subject = sinon.spy(SeriesVideoGrid);

      expect(function () {
        new subject(videos); // eslint-disable-line no-new
      }).to.throw('SeriesVideoGrid requires series-video-list to have a data-betty-url attribute.');
    });
  });

});
