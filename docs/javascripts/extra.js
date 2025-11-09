// Extra JavaScript for Dataset Generator documentation

document$.subscribe(function() {
  // Add copy buttons to code blocks
  var codeBlocks = document.querySelectorAll('pre code');
  codeBlocks.forEach(function(block) {
    var button = document.createElement('button');
    button.className = 'md-clipboard';
    button.title = 'Copy to clipboard';
    button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19 21H8V7h11m0-2H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2m-3-4H4a2 2 0 0 0-2 2v14h2V3h12V1z"/></svg>';
    button.addEventListener('click', function() {
      navigator.clipboard.writeText(block.textContent);
    });
    block.parentNode.style.position = 'relative';
    block.parentNode.appendChild(button);
  });
});