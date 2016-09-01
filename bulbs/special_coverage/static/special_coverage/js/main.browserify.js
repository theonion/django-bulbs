var SpecialCoverageLoader = require('./special-coverage-loader');

$(function () {
  var button = document.querySelector('.special-coverage-load-more');
  var list = document.querySelector('.sc-landing-list');

  if (button && list) {
    new SpecialCoverageLoader(button, list); // eslint-disable-line no-new
  }
});
