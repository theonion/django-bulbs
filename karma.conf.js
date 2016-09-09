module.exports = function (config) {
  var configuration = {
    basePath: '',
    port: 9876,
    colors: true,
    logLevel: config.LOG_INFO,
    autoWatch: true,
    browsers: ['Chrome'],
    singleRun: false,
    exclude: [],

    frameworks: [
      'browserify',
      'sinon-chai',
      'mocha',
    ],

    files: [
      'node_modules/jquery/dist/jquery.min.js',
      'test_helper.js',
      'bulbs/**/*.test.js',
    ],

    preprocessors: {
      'bulbs/**/*.test.js': ['browserify'],
    },

    reporters: ['progress'],

    client: {
      mocha: {
        reporter: 'html',
        ui: 'bdd',
      },
    },
  };

  if (process.env.TRAVIS) {
    configuration.browsers = ['Chrome_travis_ci'];
    configuration.captureTimeout = 0;
    configuration.colors = false;
    configuration.autoWatch = false;
    configuration.singleRun = true;
    configuration.customLaunchers = {
      Chrome_travis_ci: {
        base: 'Chrome',
        flags: ['--no-sandbox'],
      },
    };
  }

  config.set(configuration);
};
