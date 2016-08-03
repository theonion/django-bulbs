var PaginateVideoGrid = function (selector, buttonClass, elementsPerPage = [ 6, 8, 10 ]) {
  this.$videoGrid = $(selector);
  this.currentPage = 1;
  this.$videos = this.$videoGrid.children();
  this.firstVideoItem = this.$videoGrid.children()[0];
  this.totalPages = this.getTotalPages();
  this.elementsPerPage = elementsPerPage;
  this.previousButton = $(buttonClass).find('previous-button')[0];
  this.nextButton = $(buttonClass).find('next-button')[0];

  this.previousPage = this.previousPage.bind(this);
  this.nextPage = this.nextPage.bind(this);
  this.handleResize = this.handleResize.bind(this);

  this.init();
};

PaginateVideoGrid.prototype.init = function() {
  this.previousButton.addEventListener('click', this.previousPage);
  this.nextButton.addEventListener('click', this.nextPage);
  $(window).bind('resize', this.handleResize);

  this.videosPerPage = this.getVideosPerPage(this.elementsPerPage);
  this.updateCurrentPage(this.currentPage);
  this.updateButtons();
};

PaginateVideoGrid.prototype.getVideosPerPage = function(elementsPerPage) {
  var viewportWidth = $(window).width();
  if (viewportWidth <= 450) {             // mobile
    return elementsPerPage[0];
  } else if (viewportWidth <= 600) {      // tablet
    return elementsPerPage[1];
  } else {
    return elementsPerPage[2];                           // desktop
  }
};

PaginateVideoGrid.prototype.updateCurrentPage = function (desiredPage) {
  // validate desiredPage
  if (desiredPage < 1) desiredPage = 1;
  if (desiredPage > this.totalPages) desiredPage = this.totalPages;

  // clear out current videos
  this.$videoGrid.empty();

  var index = (desiredPage - 1) * this.videosPerPage;
  var desiredPageVideoTotal = desiredPage * this.videosPerPage;
  var totalVideos = this.$videos.length;

  for (var i = index; i < desiredPageVideoTotal && i < totalVideos; i++) {
    this.$videoGrid.append(this.$videos[i]);
  }

  this.updateButtons();
};

PaginateVideoGrid.prototype.getTotalPages = function () {
  return Math.ceil(this.$videos.length / this.videosPerPage);
};

PaginateVideoGrid.prototype.nextPage = function () {
  if (this.currentPage < this.totalPages) {
    this.currentPage++;
    this.updateCurrentPage(this.currentPage);
  }
};

PaginateVideoGrid.prototype.previousPage = function () {
  if (this.currentPage > 1) {
    this.currentPage--;
    this.updateCurrentPage(this.currentPage);
  }
};

PaginateVideoGrid.prototype.updateButtons = function () {
  this.totalPages = this.getTotalPages();
  if (this.currentPage === 1) {
    $(this.previousButton).addClass('disabled');
  } else {
    $(this.previousButton).removeClass('disabled');
  }
  if (this.currentPage === this.totalPages) {
    $(this.nextButton).addClass('disabled');
  } else {
    $(this.nextButton).removeClass('disabled');
  }
};

PaginateVideoGrid.prototype.handleResize = function() {
  this.videosPerPage = this.getVideosPerPage(this.elementsPerPage);
  this.updateCurrentPage(this.currentPage);
};

module.exports = PaginateVideoGrid;
