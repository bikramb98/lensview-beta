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
          var user_handle = data.user_handle_list;

          // Loop through each string property in the object and create a <p> element for each
          for (var key in stringsObject) {
              if (stringsObject.hasOwnProperty(key)) {
                  var stringElement = document.createElement('p');
                  stringElement.textContent = user_handle[key] + ": " + stringsObject[key];
                  stringElement.style.marginBottom = '30px';
                  stringElement.style.display = 'block'; 
                  contentContainer.appendChild(stringElement);
              }
          }

          document.getElementById('gotoLVButton').addEventListener('click', function() {
            // Define the URL you want to navigate to
            var targetUrl;

            if (post_id === 0) {
                targetUrl = 'https://testnet.lensview.io';
            } else {
                targetUrl = 'https://testnet.lensview.io/posts/' + post_id;
            }
        
            // Open a new tab with the specified URL
            chrome.tabs.create({ url: targetUrl });
        });


      })
      .catch((error) => {
          console.error('Error:', error);
      });
  });
});

