$(document).ready(function() {
  $('div.expandable p').expander({
    slicePoint:       60,  // default is 100
    expandPrefix:     ' ', // default is '... '
    expandText:       '[...]', // default is 'read more'
    userCollapseText: '[^]'  // default is 'read less'
  });
});
