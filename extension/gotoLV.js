document.getElementById('myButton').addEventListener('click', function() {
    // Define the URL you want to navigate to
    var targetUrl = 'https://example.com';

    // Open a new tab with the specified URL
    chrome.tabs.create({ url: targetUrl });
});