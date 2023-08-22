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
      .then(response => response.json())  // Parse the response as JSON
      .then(data => {
          var stringsObject = data.comments_list; // The data object directly
          var contentContainer = document.getElementById('content');
          var post_id = data.post_id;

          console.log(post_id)

          // Loop through each string property in the object and create a <p> element for each
          for (var key in stringsObject) {
            console.log("hi")
              if (stringsObject.hasOwnProperty(key)) {
                  var stringElement = document.createElement('p');
                  stringElement.textContent = stringsObject[key];
                  stringElement.style.marginBottom = '100px';
                  stringElement.style.display = 'block'; 
                  contentContainer.appendChild(stringElement);
              }
          }
      })
      .catch((error) => {
          console.error('Error:', error);
      });
  });
});
document.getElementById('gotoLVButton').addEventListener('click', function() {
    // Define the URL you want to navigate to
    var targetUrl = 'https://testnet.lensview.io';

    // Open a new tab with the specified URL
    chrome.tabs.create({ url: targetUrl });
});
