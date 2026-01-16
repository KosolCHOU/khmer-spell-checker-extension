// Proxy requests to avoid Mixed Content issues (HTTPS page -> HTTP localhost)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "checkText") {

        fetch("http://localhost:8001/api/spell-check/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text: request.text })
        })
            .then(response => response.json())
            .then(data => sendResponse({ success: true, data: data }))
            .catch(error => sendResponse({ success: false, error: error.toString() }));

        return true; // Keep the message channel open for async response
    }
});
