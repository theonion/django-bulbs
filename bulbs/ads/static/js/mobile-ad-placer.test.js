describe('MobileAdPlacer', function () {
  var mobileAdPlacer = require('./mobile-ad-placer');
  var faker = require('faker');

  var article = '<section class="article-text"></section>'
  var paragraph351 = '<p>' + faker.lorem.words(351) + '</p>';
  var paragraph20 = '<p>' + faker.lorem.words(20) + '</p>';

  beforeEach(function () {
    $('body').append(article);
    window.ads = {loadAds: function() { return }};
  });

  afterEach(function () {
    $('.article-text').remove();
  });

  it('places ad after 350 words', function () {
    $('.article-text').append(paragraph351);
    mobileAdPlacer.placeAds();
    var articleContents = $('.article-text').children();
    expect($(articleContents[1]).attr('class')).to.equal("dfp dfp-slot-inread");
  });

  it('places multiple ads', function () {
    $('.article-text').append(paragraph351);
    $('.article-text').append(paragraph351);
    adElement = document.createElement('ad');
    mobileAdPlacer.placeAds(adElement);
    var ads = $('.article-text').find('.dfp-slot-inread');
    expect(ads.length).to.equal(2);
  });

  it('only places ads after paragraph breaks', function () {
    adElement = document.createElement('ad');
    var bigAssParagraph = '<p>' + faker.lorem.words(1000) + '</p>';
    $('.article-text').append(bigAssParagraph);

    mobileAdPlacer.placeAds(adElement);
    var articleContents = $('.article-text').children();
    // sanity check ad is placed
    expect($('.article-text').find('.dfp').length).to.equal(1);
    // not placed within p element
    expect($('p').find('.dfp').length).to.equal(0);
  });

  it('places no more than 4 ads', function () {
    adElement = document.createElement('ad');
    for(var i = 0; i < 5; i++) {
      $('.article-text').append(paragraph351);
    }
    mobileAdPlacer.placeAds();
    var ads = $('.article-text').find('.dfp-slot-inread');
    expect(ads.length).to.equal(4);
  });
});
