var karmaConfig = require('./karma.conf');

module.exports = function (config) {
  config.set(Object.assign({
    browsers: ['PhantomJS'],
    captureTimeout: 0,
    reporters: ['progress'],
    colors: false,
    autoWatch: false,
  }, karmaConfig));
};
