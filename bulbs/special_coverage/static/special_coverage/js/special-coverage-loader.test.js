/* eslint no-new: 0*/
var SpecialCoverageLoader = require('./special-coverage-loader');

describe('SpecialCoverageLoader', function () {
  var url;
  var element;
  var listElement;
  var requests;
  var currentPage;
  var perPage;
  var subject;
  var xhr;
  var sandbox;
  beforeEach(function () {
    sandbox = sinon.sandbox.create();
    xhr = sinon.useFakeXMLHttpRequest();
    requests = this.requests = [];

    xhr.onCreate = function (request) {
      requests.push(request);
    };

    url = 'http://example.com/some/page';
    currentPage = 1;
    perPage = 10;
    element = document.createElement('button');
    element.innerHTML = 'Load More';
    element.dataset.total = 20;
    element.dataset.perPage = 10;
    listElement = document.createElement('ul');
    subject = new SpecialCoverageLoader(element, listElement);
  });

  afterEach(function () {
    sandbox.restore();
  });

  it('requires an element', function () {
    expect(function () {
      new SpecialCoverageLoader();
    }).to.throw('new SpecialCoverageLoader(element, listElement, options): element is undefined');
  });

  it('requires a listElement', function () {
    expect(function () {
      new SpecialCoverageLoader(element);
    }).to.throw('new SpecialCoverageLoader(element, listElement, options): listElement is undefined');
  });

  it('requires a total data attribute value', function () {
    delete element.dataset.total;
    expect(function () {
      new SpecialCoverageLoader(element, listElement);
    }).to.throw('new SpecialCoverageLoader(element, listElement, options): element has no data-total value');
  });

  it('requires a perPage data attribute value', function () {
    delete element.dataset.perPage;
    expect(function () {
      new SpecialCoverageLoader(element, listElement);
    }).to.throw('new SpecialCoverageLoader(element, listElement, options): element has no data-per-page value');
  });

  it('has a current page', function () {
    expect(subject.currentPage).to.equal(1);
  });

  it('has a baseUrl', function () {
    expect(subject.baseUrl).to.equal(window.location.href);
  });

  it('strips the trailing slash from the baseUrl', function () {
    subject = new SpecialCoverageLoader(element, listElement, { baseUrl: 'http://staff.avclub.com/special/1996-week/' });
    expect(subject.baseUrl).to.equal('http://staff.avclub.com/special/1996-week');
  });

  it('registers loadMore to the element click', function () {
    sandbox.stub(subject, 'loadMore');
    element.click();
    var offset = subject.nextOffset(1, 10);
    var loadUrl = subject.buildUrl(1, 10, subject.baseUrl, offset);
    expect(subject.loadMore).to.have.been.calledWith(loadUrl);
  });

  it('saves a reference to the list element', function () {
    expect(subject.listElement).to.equal(listElement);
  });

  it('saves a reference to the element', function () {
    expect(subject.element).to.equal(element);
  });

  it('saves a reference to the data total value', function () {
    expect(subject.total).to.equal(20);
  });

  it('saves a reference to the data perPage value', function () {
    expect(subject.perPage).to.equal(10);
  });

  it('has an isLoading flag', function () {
    expect(subject.isLoading).to.equal(false);
  });

  it('saves a reference to the default text', function () {
    expect(subject.defaultText).to.equal('Load More');
  });

  it('has loadingText', function () {
    expect(subject.loadingText).to.equal('Loading...');
  });

  describe('options', function () {
    it('accepts an optional baseUrl value', function () {
      subject = new SpecialCoverageLoader(element, listElement, { baseUrl: url });
      expect(subject.baseUrl).to.equal(url);
    });
  });

  describe('nextOffset', function () {
    it('throws and error if no currentPage is given', function () {
      expect(function () {
        subject.nextOffset();
      }).to.throw('SpecialCoverageLoader.nextOffset(currentPage, perPage): currentPage is undefined');
    });

    it('throws an error if no perPage value is given', function () {
      expect(function () {
        subject.nextOffset(1);
      }).to.throw('SpecialCoverageLoader.nextOffset(currentPage, perPage): perPage is undefined');
    });

    it('returns the page times the perPage value', function () {
      expect(subject.nextOffset(2, 10)).to.equal(20);
    });
  });

  describe('buildUrl', function () {
    it('throws an error if no baseUrl is given', function () {
      expect(function () {
        subject.buildUrl();
      }).to.throw('SpecialCoverageLoader.buildUrl(currentPage, perPage, baseUrl, offset): currentPage is undefined');
    });

    it('throws an error if no perPage value is given', function () {
      expect(function () {
        subject.buildUrl(currentPage);
      }).to.throw('SpecialCoverageLoader.buildUrl(currentPage, perPage, baseUrl, offset): perPage is undefined');
    });

    it('throws an error if no baseUrl is given', function () {
      expect(function () {
        subject.buildUrl(currentPage, perPage);
      }).to.throw('SpecialCoverageLoader.buildUrl(currentPage, perPage, baseUrl, offset): baseUrl is undefined');
    });

    it('returns a url with the next offset', function () {
      expect(subject.buildUrl(currentPage, perPage, url)).to.equal(url + '/more/' + 10);
    });

    it('returns a url with query parameters appended', function () {
      var queryUrl = url + '?full_preview=true';
      expect(subject.buildUrl(currentPage, perPage, queryUrl)).to.equal(url + '/more/10?full_preview=true');
    });
  });

  describe('loadMore', function () {
    it('does nothing when there is a pending load', function () {
      subject.isLoading = true;
      subject.loadMore(url);
      expect(requests.length).to.equal(0);
    });

    it('throws an error if no url is given', function () {
      expect(function () {
        subject.loadMore();
      }).to.throw('SpecialCoverageLoader.loadMore(url): url is undefined');
    });

    it('sets the element text to the loading text ', function () {
      sandbox.stub(subject, 'handleLoadMoreSuccess');
      subject.loadMore(url);
      expect(subject.element.innerHTML).to.equal(subject.loadingText);
    });

    it('loads more content items', function () {
      subject.loadMore(url);
      var request = requests[0];
      expect(request.method).to.equal('GET');
      expect(request.requestHeaders.Accept).to.match(/text\/html/);
      expect(request.url).to.equal(url);
    });

    it('sets the isLoading flag to true', function () {
      sandbox.stub(subject, 'handleLoadMoreSuccess');
      subject.loadMore(url);
      expect(subject.isLoading).to.equal(true);
    });
  });

  describe('handleLoadMoreSuccess', function () {
    it('throws an error if no response is given', function () {
      expect(function () {
        subject.handleLoadMoreSuccess();
      }).to.throw('SpecialCoverageLoader.handleLoadMoreSuccess(response): response is undefined');
    });

    it('does nothing if the response is empty', function () {
      var html = subject.listElement.innerHTML;
      subject.handleLoadMoreSuccess('    ');
      expect(subject.listElement.innerHTML).to.equal(html);
    });

    it('appends the response to the list element', function () {
      subject.handleLoadMoreSuccess('content');
      expect(subject.listElement.innerHTML).to.equal('content');
    });

    it('increases the currentPage by 1', function () {
      var page = subject.currentPage;
      subject.handleLoadMoreSuccess('content');
      expect(subject.currentPage).to.equal(page + 1);
    });

    it('sets the button visibility', function () {
      sandbox.stub(subject, 'setButtonVisibility');
      subject.handleLoadMoreSuccess('content');
      expect(subject.setButtonVisibility).to.have.been.called;
    });

    it('toggles the loading state', function () {
      sandbox.stub(subject, 'toggleLoadingState');
      subject.handleLoadMoreSuccess('content');
      expect(subject.toggleLoadingState).to.have.been.calledWith(subject.isLoading, element);
    });
  });

  describe('toggleLoadingState', function () {
    it('throws an error if no loadingState is provided', function () {
      expect(() => {
        subject.toggleLoadingState();
      }).to.throw('SpecialCoverageLoader.toggleLoadingState(loadingState, element): loadingState is undefined');
    });

    it('throws an error if no element id given', function () {
      expect(() => {
        subject.toggleLoadingState(true);
      }).to.throw('SpecialCoverageLoader.toggleLoadingState(loadingState, element): element is undefined');
    });

    it('toggles the loading state', function () {
      subject.toggleLoadingState(true, element);
      expect(subject.isLoading).to.equal(false);

      subject.toggleLoadingState(false, element);
      expect(subject.isLoading).to.equal(true);
    });

    it('toggles the element text', function () {
      subject.toggleLoadingState(false, element);
      expect(element.innerHTML).to.equal(subject.loadingText);
    });
  });

  describe('isLastPage', function () {
    var total;
    var liElement;
    beforeEach(function () {
      total = 13;
      liElement = document.createElement('li');
      liElement.classList.add('sc-landing-list-item');
      listElement.appendChild(liElement);
    });

    it('throws an error if no total is given', function () {
      expect(function () {
        subject.isLastPage();
      }).to.throw('SpecialCoverageLoader.isLastPage(total, listElement): total is undefined');
    });

    it('throws an error if no listElement is given', function () {
      expect(function () {
        subject.isLastPage(1);
      }).to.throw('SpecialCoverageLoader.isLastPage(total, listElement): listElement is undefined');
    });

    it('returns false when there is more content', function () {
      expect(subject.isLastPage(total, listElement)).to.equal(false);
    });

    it('returns true when there is no more content', function () {
      expect(subject.isLastPage(1, listElement)).to.equal(true);
    });

    it('only considers .sc-landing-list-item children', function () {
      let carouselItem = document.createElement('li');
      var extraLiElement = document.createElement('li');

      carouselItem.classList.add('sc-landing-carousel');
      extraLiElement.classList.add('sc-landing-list-item');

      listElement.appendChild(carouselItem);
      listElement.appendChild(extraLiElement);

      expect(subject.isLastPage(2, listElement)).to.equal(true);
    });
  });

  describe('handleLoadMoreFailure', function () {
    it('throws an error if no response is given', function () {
      expect(function () {
        subject.handleLoadMoreFailure();
      }).to.throw('SpecialCoverageLoader.handleLoadMoreFailure(response): response id undefined');
    });

    it('logs the failure with the response and url attempted', function () {
      sandbox.stub(console, 'log');
      var nextUrl = subject.buildUrl(subject.currentPage, subject.perPage, subject.baseUrl);
      var response = {
        status: 404,
        statusText: 'Not Found',
      };
      var message = 'SpecialCoverageLoader.loadMore("' + nextUrl + '"): server responded with "404 Not Found"';
      subject.handleLoadMoreFailure(response);
      expect(console.log).to.have.been.calledWith(message);
    });

    it('toggles the loading state', function () {
      sandbox.stub(subject, 'toggleLoadingState');
      subject.handleLoadMoreFailure('content');
      expect(subject.toggleLoadingState).to.have.been.calledWith(subject.isLoading, subject.element);
    });
  });

  describe('setButtonVisibility', function () {
    beforeEach(function () {
      sandbox.stub(subject, 'hideElement');
    });

    it('throws an error if no response is given', function () {
      expect(function () {
        subject.setButtonVisibility();
      }).to.throw('SpecialCoverageLoader.setButtonVisibility(response): response is undefined');
    });

    it('hides the button if the response is empty', function () {
      subject.setButtonVisibility('');
      expect(subject.hideElement).to.have.been.called;
    });

    it('hides the button if on the last page', function () {
      sandbox.stub(subject, 'isLastPage').returns(true);
      subject.setButtonVisibility('not empty');
      expect(subject.hideElement).to.have.been.called;
    });
  });
});
