document.addEventListener('DOMContentLoaded', function () {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      var url = tabs[0].url;
      fetch('http://127.0.0.1:5000/api/analyze-url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: url })
      })
      .then(response => response.text())
      .then(data => {
        document.getElementById('content').textContent = data;
      })
      .catch((error) => {
        console.error('Error:', error);
      });
    });
  });