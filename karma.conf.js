module.exports = function (config) {
  config.set({
    basePath: '',

    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: [
      'browserify',
      'sinon-chai',
      'mocha',
    ],

    // list of files / patterns to load in the browser
    files: [
      'node_modules/jquery/dist/jquery.min.js',
      'test_helper.js',
      'bulbs/**/*.test.js',
    ],

    // list of files to exclude
    exclude: [],

    preprocessors: {
      'bulbs/**/*.test.js': ['browserify'],
    },

    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['html', 'progress'],

    client: {
      mocha: {
        reporter: 'html',
        ui: 'bdd',
      },
    },

    // web server port
    port: 9876,

    // enable / disable colors in the output (reporters and logs)
    colors: true,

    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,

    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,

    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['Chrome'],

    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: false,

    customLaunchers: {
      Chrome_travis_ci: {
        base: 'Chrome',
        flags: ['--no-sandbox'],
      },
    },
  });

  if (process.env.TRAVIS) {
    config.captureTimeout = 0;
    config.browsers = ['Chrome_travis_ci'];
    config.singleRun = true;
    config.autoWatch = false;
  }
};
