// WebSocket connection for polling JSON files
let ws;
let reconnectInterval = 3000;
let currentFeed = null;

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/`;

    ws = new WebSocket(wsUrl);

    ws.onopen = function() {
        console.log('WebSocket connected');
        updateConnectionStatus(true);
        if (currentFeed) {
            ws.send(currentFeed);
        }
    };

    ws.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            if (data.error) {
                console.warn('Server error:', data.error);
                setFeedStatus(data.error);
                return;
            }
            displayJsonData(data);
        } catch (error) {
            console.error('Error parsing JSON:', error);
        }
    };

    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
        updateConnectionStatus(false);
    };

    ws.onclose = function() {
        console.log('WebSocket disconnected');
        updateConnectionStatus(false);
        setTimeout(connectWebSocket, reconnectInterval);
    };
}

function displayJsonData(data) {
    const tbody = document.getElementById('local-body');
    if (!tbody) return;
    if (typeof data === 'string') {
        try {
            data = JSON.parse(data);
        } catch (e) {
            console.error('Failed to parse data string:', e);
            return;
        }
    }

    const row = document.createElement('tr');

    const name = data.name || 'N/A';
    const price = data.price !== undefined ? data.price : 'N/A';
    const delta = data.delta !== undefined ? data.delta : 'N/A';
    const rawJson = JSON.stringify(data, null, 2);

    row.innerHTML = `
        <td>${name}</td>
        <td class="price">${price}</td>
        <td class="delta">${delta}</td>
        <td><pre style="margin: 0; font-size: 11px; max-width: 300px; overflow-x: auto;">${rawJson}<re></td>
    `;

    tbody.insertBefore(row, tbody.firstChild);

    while (tbody.children.length > 5) {
        tbody.removeChild(tbody.lastChild);
    }
}

function updateConnectionStatus(connected) {
    console.log(`Connection status: ${connected ? 'Connected' : 'Disconnected'}`);
}

function setFeedStatus(message) {
    const status = document.getElementById('feed-status');
    if (status) {
        status.textContent = message;
        if (message !== 'No feed selected.') {
            status.classList.add('active');
        } else {
            status.classList.remove('active');
        }
    }
}

function clearDisplayedData() {
    const tbody = document.getElementById('local-body');
    if (tbody) {
        tbody.innerHTML = '';
    }
}

function requestFeed(feedName) {
    currentFeed = feedName;
    clearDisplayedData();
    setFeedStatus(`Watching ${feedName}`);

    if (ws && ws.readyState === WebSocket.OPEN) {
        console.log('Sending exchange feed request:', feedName);
        ws.send(feedName);
    } else {
        console.warn('WebSocket not connected, will send once connected');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    connectWebSocket();

    document.querySelectorAll('.feed-btn').forEach((button) => {
        button.addEventListener('click', () => {
            document.querySelectorAll('.feed-btn').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            requestFeed(button.dataset.feed);
        });
    });
});
