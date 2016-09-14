'use strict';
var adHtml = '<div class="dfp dfp-slot-inread" data-ad-unit="inread"> \
                Content continues below advertisement \
              </div>';


var MobileAdPlacer = {
  placeAds: function () {
    var articleText = $('.article-text');
    var paragraphs = articleText.find('p');
    var wordCount = 0;
    var adsPlaced = 0;

    for (var i = 0; i < paragraphs.length; i++) {
      var paragraphLength = MobileAdPlacer.wordCount($(paragraphs[i]).html());
      wordCount = wordCount + paragraphLength;

      if(wordCount > 350 && adsPlaced < 4) {
        // place ad
        $(paragraphs[i]).after(adHtml);
        wordCount = 0;
        adsPlaced++;
      }
    }
    if (window.ads) {
      window.ads.loadAds();
    }
  },
  wordCount: function (paragraph) {
    return paragraph.split(' ').length;
  },
};

module.exports = MobileAdPlacer;
