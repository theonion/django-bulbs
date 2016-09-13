module.exports = (function () { // eslint-disable-line no-unused-vars
  // These quasi-copies of lodash methods are used instead of lodash
  // because we do not want to depend on it here
  function isUndefined (suspect) {
    return typeof(suspect) === 'undefined';
  }

  function requireArgument (value, message) {
    if (isUndefined(value)) { throw new Error(message); }
  }

  function assign (target, source) {
    Object.keys(source).forEach(function (key) {
      target[key] = source[key];
    });
  }

  function defaults (target, source) {
    Object.keys(source).forEach(function (key) {
      if (!target[key]) { target[key] = source[key]; }
    });
  }

  function stripTrailingSlash (string) {
    return string.replace(/\/?$/, '');
  }

  function stripBeginingSlash (string) {
    return string.replace(/^\/?/, '');
  }

  function stripEndSlashes (string) {
    return stripTrailingSlash(stripBeginingSlash(string));
  }

  function compact (list) {
    var newList = [];
    list.forEach(function (item) {
      if (!isUndefined(item) || item.length > 0) {
        newList.push(item);
      }
    });

    return newList;
  }

  function SpecialCoverageLoader (element, listElement, options) {
    requireArgument(element, 'new SpecialCoverageLoader(element, listElement, options): element is undefined');
    requireArgument(listElement, 'new SpecialCoverageLoader(element, listElement, options): listElement is undefined');
    requireArgument(element.dataset.total, 'new SpecialCoverageLoader(element, listElement, options): element has no data-total value');
    requireArgument(element.dataset.perPage, 'new SpecialCoverageLoader(element, listElement, options): element has no data-per-page value');

    options = options || {};
    this.total = parseInt(element.dataset.total, 10);
    this.perPage = parseInt(element.dataset.perPage, 10);
    this.currentPage = 1;
    this.listElement = listElement;
    this.element = element;
    this.isLoading = false;
    this.defaultText = element.innerHTML;
    this.loadingText = 'Loading...';

    var defaultBaseUrl = [
      window.location.protocol, '//',
      window.location.hostname + ':' + window.location.port,
      window.location.pathname,
      window.location.search,
      window.location.hash,
    ].join('');

    defaults(options, { baseUrl: defaultBaseUrl });
    options.baseUrl = stripTrailingSlash(options.baseUrl);
    assign(this, options);

    element.addEventListener('click', function () {
      var url = this.buildUrl(this.currentPage, this.perPage, this.baseUrl);
      this.loadMore(url);
    }.bind(this));
  }

  assign(SpecialCoverageLoader.prototype, {
    nextOffset: function (currentPage, perPage) {
      requireArgument(currentPage, 'SpecialCoverageLoader.nextOffset(currentPage, perPage): currentPage is undefined');
      requireArgument(perPage, 'SpecialCoverageLoader.nextOffset(currentPage, perPage): perPage is undefined');

      return currentPage * perPage;
    },

    buildUrl: function (currentPage, perPage, baseUrl) {
      requireArgument(currentPage, 'SpecialCoverageLoader.buildUrl(currentPage, perPage, baseUrl, offset): currentPage is undefined');
      requireArgument(perPage, 'SpecialCoverageLoader.buildUrl(currentPage, perPage, baseUrl, offset): perPage is undefined');
      requireArgument(baseUrl, 'SpecialCoverageLoader.buildUrl(currentPage, perPage, baseUrl, offset): baseUrl is undefined');

      var offset = this.nextOffset(currentPage, perPage);
      var parser = document.createElement('a');

      parser.href = stripTrailingSlash(baseUrl);

      return compact([
        parser.protocol + '/',
        parser.hostname,
        stripEndSlashes(parser.pathname),
        'more',
        offset + parser.search,
      ]).join('/');
    },

    loadMore: function (url) {
      if (this.isLoading) { return; }
      requireArgument(url, 'SpecialCoverageLoader.loadMore(url): url is undefined');
      this.isLoading = true;
      this.element.innerHTML = this.loadingText;
      $.ajax({
        url: url,
        type: 'get',
        dataType: 'html',
      })
        .done(this.handleLoadMoreSuccess.bind(this))
        .fail(this.handleLoadMoreFailure.bind(this));
    },

    toggleLoadingState: function (loadingState, element) {
      requireArgument(loadingState, 'SpecialCoverageLoader.toggleLoadingState(loadingState, element): loadingState is undefined');
      requireArgument(element, 'SpecialCoverageLoader.toggleLoadingState(loadingState, element): element is undefined');
      this.isLoading = !loadingState;
      element.innerHTML = this.isLoading ? this.loadingText : this.defaultText;
    },

    handleLoadMoreSuccess: function (response) {
      this.toggleLoadingState(this.isLoading, this.element);
      requireArgument(response, 'SpecialCoverageLoader.handleLoadMoreSuccess(response): response is undefined');
      response = response.trim();
      if (response) {
        this.currentPage += 1;
        this.listElement.innerHTML = this.listElement.innerHTML + response;
      }
      this.setButtonVisibility(response);
    },

    handleLoadMoreFailure: function (response) {
      this.toggleLoadingState(this.isLoading, this.element);
      requireArgument(response, 'SpecialCoverageLoader.handleLoadMoreFailure(response): response id undefined');

      var message = [
        'SpecialCoverageLoader.loadMore("',
        this.buildUrl(this.currentPage, this.perPage, this.baseUrl),
        '"): server responded with "',
        response.status,
        ' ',
        response.statusText,
        '"',
      ].join('');

      console.log(message);
    },

    hideElement: function () {
      this.element.style.display = 'none';
    },

    isLastPage: function (total, listElement) {
      requireArgument(total, 'SpecialCoverageLoader.isLastPage(total, listElement): total is undefined');
      requireArgument(listElement, 'SpecialCoverageLoader.isLastPage(total, listElement): listElement is undefined');

      var listItems = [];
      for (var i = 0; i < listElement.children.length; i += 1) {
        var item = listElement.children[i];

        if (item.classList.contains('sc-landing-list-item')) {
          listItems.push(item);
        }
      }

      return total <= listItems.length;
    },

    setButtonVisibility: function (response) {
      requireArgument(response, 'SpecialCoverageLoader.setButtonVisibility(response): response is undefined');

      if (!response || this.isLastPage(this.total, this.listElement)) {
        this.hideElement();
      }
    },
  });
  return SpecialCoverageLoader;
})();
