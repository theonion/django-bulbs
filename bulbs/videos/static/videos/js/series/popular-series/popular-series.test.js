describe('PopularSeries', function () {
  var PopularSeries = require('./popular-series');
  var seriesData = [
    {
      channel_name: 'The Onion',
      series_name: 'Behind The Pen',
      series_slug: 'behind-the-pen',
      series_description: 'blah blah blah',
      series_logo: 'http://foobar.com/image/600.png',
      total_episodes: 6,
      total_seasons: 0
    },
    {
      total_episodes: 20,
      total_seasons: 1
    }];

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

  describe('series data fetched', function () {
    it('appends anchor tag with series link', function () {
      PopularSeries.prototype.seriesDataFetched(seriesData[0]);
      var expected = $('.popular-series-item').attr('href');
      expect(expected).to.equal('/series/behind-the-pen');
    });

    it('appends series title', function () {
      PopularSeries.prototype.seriesDataFetched(seriesData[0]);
      var expected = $('.popular-series-item-title').html();
      expect(expected).to.equal('Behind The Pen');
    });

    it('appends series episode count', function () {
      PopularSeries.prototype.seriesDataFetched(seriesData[0]);
      var expected = $('.popular-series-item-episodes').html();
      expect(expected).to.equal('6 Videos');
    });

    it('appends series season count', function () {
      PopularSeries.prototype.seriesDataFetched(seriesData[1]);
      var expected = $('.popular-series-item-seasons').html();
      expect(expected).to.equal('1 Seasons');
    });

    it('does not appends series season count if series seasons = 0', function () {
      PopularSeries.prototype.seriesDataFetched(seriesData[0]);
      var expected = $('.popular-series-item-seasons').length;
      expect(expected).to.equal(0);
    });

    it('appends series logo', function () {
      PopularSeries.prototype.seriesDataFetched(seriesData[0]);
      var expected = $('.series-logo img').attr('src');
      expect(expected).to.equal('http://foobar.com/image/600.png');
    });
  });
});
