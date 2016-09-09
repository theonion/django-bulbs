var karmaConfig = require('./karma.conf');

module.exports = function (config) {
  config.set(Object.assign({
    browsers: ['Chrome_travis_ci'],
    captureTimeout: 0,
    colors: false,
    autoWatch: false,
    singleRun: true,
    customLaunchers: {
      Chrome_travis_ci: {
        base: 'Chrome',
        flags: ['--no-sandbox'],
      },
    },
  }, karmaConfig));
};
