describe('PopularSeries', function () {
  var PopularSeries = require('./popular-series');
  var seriesDataList = [
    { id: 1, slug: 'funky', name: 'Funky' },
    { id: 2, slug: 'cool-series', name: 'Cool Series' },
    { id: 3, slug: 'daf-series', name: 'DAF Series' },
    { id: 4, slug: 'lame-series', name: 'Lame Series' },
    { id: 5, slug: 'trivial-series', name: 'Trivial Series' }
  ];


  beforeEach(function () {
    var popularSeriesDiv = "<div id='popular-series' \
            data-channel-series='foobar.com/channel/funky/series.json' \
            data-vidoehub-base='foobar.com' \
            data-series-slug='funk-yeah'> \
       </div>"
    $('body').append(popularSeriesDiv);
  });

  afterEach(function () {
    $('#popular-series').remove();
  });

  it('calls loadPopularSeries', function () {
    TestHelper.spyOn(PopularSeries.prototype, 'loadPopularSeries');
    new PopularSeries();
    expect(PopularSeries.prototype.loadPopularSeries.called).to.equal(true);
  });

  it('uses the data-series-channel attribute to fetch channel data', function () {
    TestHelper.spyOn($, 'getJSON');
    new PopularSeries();
    var expected = $.getJSON.calledWith('foobar.com/channel/funky/series.json');
    expect(expected).to.equal(true);
  });
});
