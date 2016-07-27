'use strict';

describe('PaginateVideoGrid', function () {
  var paginate = require('./paginated-series-video-grid');
  var expected;

  beforeEach(function () {
    var videoGrid = '<div class="video-grid"></div>';
    var prevButton = '<video-series-previous></video-series-previous>';
    var nextButton = '<video-series-next></video-series-next>';
    var videoList = '<div class="video-list"></div>';

    $('body').append(videoGrid);
    $('.video-grid').append(prevButton);
    $('.video-grid').append(nextButton);
    $('.video-grid').append(videoList);
    for(var i = 0; i < 20; i++) {
      $('.video-list').append('<a class="video-item" id="' + i + '"></a>');
    }
  });

  afterEach(function () {
    $('.video-grid').remove();
  });

  describe('init', function () {
    it('adds click listener to previousButton', function () {
      sinon.spy(paginate.prototype, 'previousPage');
      new paginate('.video-list');
      $('video-series-previous').trigger('click');
      expect(paginate.prototype.previousPage.called).to.equal(true);
    });

    it('adds click listener to nextButton', function () {
      sinon.spy(paginate.prototype, 'nextPage');
      new paginate('.video-list');
      $('video-series-next').trigger('click');
      expect(paginate.prototype.nextPage.called).to.equal(true);
    });

    it('adds resize listener to window', function () {
      sinon.spy(paginate.prototype, 'handleResize');
      new paginate('.video-list');
      $(window).trigger('resize');
      expect(paginate.prototype.handleResize.called).to.equal(true);
    });

    it('calls getVideosPerPage', function () {
      sinon.spy(paginate.prototype, 'getVideosPerPage');
      new paginate('.video-list');
      expect(paginate.prototype.getVideosPerPage.called).to.equal(true);
    });

    it('calls updateCurrentPage', function () {
      sinon.spy(paginate.prototype, 'updateCurrentPage');
      new paginate('.video-list');
      expect(paginate.prototype.updateCurrentPage.called).to.equal(true);
      paginate.prototype.updateCurrentPage.restore();
    });

    it('calls updateButtons', function () {
      sinon.spy(paginate.prototype, 'updateButtons');
      new paginate('.video-list');
      expect(paginate.prototype.updateButtons.called).to.equal(true);
    });
  });

  describe('getVideosPerPage', function () {
    beforeEach(function () {
      new paginate('.video-list');
    });

    afterEach(function () {
      $.fn.width.restore();
    });

    it('returns 6 when the viewport is <= 450px', function () {
      sinon.stub($.fn, 'width').returns(449);
      var expected = paginate.prototype.getVideosPerPage();
      expect(expected).to.equal(6);
    });

    it('returns 8 when the viewport is <= 600px', function () {
      sinon.stub($.fn, 'width').returns(599);
      var expected = paginate.prototype.getVideosPerPage();
      expect(expected).to.equal(8);
    });

    it('returns 10 when the viewport is > 600px', function () {
      sinon.stub($.fn, 'width').returns(601);
      var expected = paginate.prototype.getVideosPerPage();
      expect(expected).to.equal(10);
    });
  });

  describe('toggling', function () {
    beforeEach(function () {
      sinon.stub($.fn, 'width').returns(601);
      new paginate('.video-list');
    });

    afterEach(function () {
      $.fn.width.restore();
    });

    it('updates the number of video elements to totalVideosPerPage', function () {
      var $videoListChildren = $('.video-list').children();
      // sanity check
      expect($videoListChildren.length).to.equal(10);
      expect($videoListChildren[9].id).to.equal('9');

      // trigger updateCurrentPage
      $('video-series-next').trigger('click');

      expected = $('.video-list').children()[9].id;
      expect(expected).to.equal('19');

      $('video-series-previous').trigger('click');
      expected = $('.video-list').children()[9].id;
      expect(expected).to.equal('9');
    });

    it('does not allow toggling to page -1', function () {
      $('video-series-previous').trigger('click');
      expected = $('.video-list').children()[9].id;
      expect(expected).to.equal('9');
    });

    it('does not allow toggling past the total number of pages', function () {
      $('video-series-next').trigger('click');
      expected = $('.video-list').children()[9].id;
      expect(expected).to.equal('19');

      $('video-series-next').trigger('click');
      expected = $('.video-list').children()[9].id;
      expect(expected).to.equal('19');
    });

    it('adds disabled class to prev button on 1st page', function () {
      expected = $('video-series-previous').hasClass('disabled');
      expect(expected).to.equal(true);
    });

    it('adds disabled class to next button on last page', function () {
      $('video-series-next').trigger('click');
      expected = $('video-series-next').hasClass('disabled');
      expect(expected).to.equal(true);
    });

    it('removes disabled class from prev when not on first page', function () {
      expected = $('video-series-previous').hasClass('disabled');
      expect(expected).to.equal(true);
      $('video-series-next').trigger('click');
      expected = $('video-series-previous').hasClass('disabled');
      expect(expected).to.equal(false);
    });

    it('removes disabled class from next when not on last page', function () {
      $('video-series-next').trigger('click');
      expected = $('video-series-next').hasClass('disabled');
      expect(expected).to.equal(true);
      $('video-series-previous').trigger('click');
      expected = $('video-series-next').hasClass('disabled');
      expect(expected).to.equal(false);
    });
  });
});
