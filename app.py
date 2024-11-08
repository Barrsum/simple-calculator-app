from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import requests
import os
import threading
import time
from dotenv import load_dotenv
from itertools import cycle

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

NVIDIA_API_BASE = "https://integrate.api.nvidia.com/v1"

# API key rotation setup
api_keys = os.getenv("NVIDIA_API_KEYS", "").split(",")
api_key_cycle = cycle(api_keys)
api_key_lock = threading.Lock()

# Epic counter setup
counters = {
    'c1': 0,  # rightmost counter
    'c2': 0,  # second from right
    'c3': 0,  # middle counter
    'c4': 0,  # second from left
    'c5': 0   # leftmost counter
}
counter_lock = threading.Lock()

def get_next_api_key():
    with api_key_lock:
        return next(api_key_cycle)

def update_counters():
    global counters
    while True:
        with counter_lock:
            counters['c1'] = (counters['c1'] + 1) % 100
            if counters['c1'] == 0:
                counters['c2'] = (counters['c2'] + 1) % 100
                if counters['c2'] == 0:
                    counters['c3'] = (counters['c3'] + 1) % 100
                    if counters['c3'] == 0:
                        counters['c4'] = (counters['c4'] + 1) % 100
                        if counters['c4'] == 0:
                            counters['c5'] = (counters['c5'] + 1) % 100
        time.sleep(1)

# Start the counter thread
counter_thread = threading.Thread(target=update_counters, daemon=True)
counter_thread.start()

@app.route('/')
def home():
    active_keys = len(api_keys)
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nvidia API Proxy</title>
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #1a1a1a;
                color: #ffffff;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                text-align: center;
            }
            .container {
                background: #2d2d2d;
                padding: 2rem;
                border-radius: 1rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                max-width: 600px;
                width: 90%;
            }
            .status {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 1rem;
                margin: 2rem 0;
            }
            .pulse {
                width: 15px;
                height: 15px;
                background: #00ff00;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            h1 {
                color: #00ff00;
                margin-bottom: 1rem;
            }
            .epic-counter {
                display: flex;
                justify-content: center;
                gap: 10px;
                margin: 2rem 0;
            }
            .counter-digit {
                background: #000;
                padding: 1rem;
                border-radius: 0.5rem;
                min-width: 60px;
                font-size: 2rem;
                font-family: monospace;
                color: #00ff00;
                text-shadow: 0 0 10px #00ff00;
                border: 1px solid #00ff00;
            }
            .time-calc {
                background: #222;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 1rem 0;
                text-align: left;
            }
            .calc-button {
                background: #00ff00;
                color: #000;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 0.5rem;
                cursor: pointer;
                font-weight: bold;
                margin: 1rem 0;
                transition: all 0.3s;
            }
            .calc-button:hover {
                background: #00cc00;
                box-shadow: 0 0 10px #00ff00;
            }
            .endpoints {
                background: #222;
                padding: 1rem;
                border-radius: 0.5rem;
                margin-top: 2rem;
                text-align: left;
            }
            .endpoint {
                margin: 0.5rem 0;
                color: #00ff00;
                font-family: monospace;
            }
            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); }
                70% { box-shadow: 0 0 0 10px rgba(0, 255, 0, 0); }
                100% { box-shadow: 0 0 0 0 rgba(0, 255, 0, 0); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>--5--Way--Count--er--</h1>
            <div class="status">
                <div class="pulse"></div>
                <p><strong>Status: Active</strong></p>
            </div>
            <div class="epic-counter">
                <div class="counter-digit" id="c5">00</div>
                <div class="counter-digit" id="c4">00</div>
                <div class="counter-digit" id="c3">00</div>
                <div class="counter-digit" id="c2">00</div>
                <div class="counter-digit" id="c1">00</div>
            </div>
            <button class="calc-button" onclick="calculateTime()">Calculate Total Time</button>
            <div class="time-calc" id="timeCalc"></div>
            <div class="endpoints">
                <p><strong>Suggestions:</strong></p>
                <div class="endpoint"> A Snake Game? </div>
                <div class="endpoint">A Tetris Game?</div>
                <div class="endpoint">A Flappy Bird Game?</div>
            </div>
        </div>
        <script>
            function padNumber(num) {
                return num.toString().padStart(2, '0');
            }

            function updateCounters() {
                fetch('/counter')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('c1').textContent = padNumber(data.c1);
                        document.getElementById('c2').textContent = padNumber(data.c2);
                        document.getElementById('c3').textContent = padNumber(data.c3);
                        document.getElementById('c4').textContent = padNumber(data.c4);
                        document.getElementById('c5').textContent = padNumber(data.c5);
                    });
            }

            function calculateTime() {
                fetch('/counter')
                    .then(response => response.json())
                    .then(data => {
                        const totalSeconds = (data.c5 * 100000000) + 
                                          (data.c4 * 1000000) + 
                                          (data.c3 * 10000) + 
                                          (data.c2 * 100) + 
                                          data.c1;
                        
                        const years = Math.floor(totalSeconds / (365 * 24 * 60 * 60));
                        let remainder = totalSeconds % (365 * 24 * 60 * 60);
                        
                        const months = Math.floor(remainder / (30 * 24 * 60 * 60));
                        remainder = remainder % (30 * 24 * 60 * 60);
                        
                        const weeks = Math.floor(remainder / (7 * 24 * 60 * 60));
                        remainder = remainder % (7 * 24 * 60 * 60);
                        
                        const days = Math.floor(remainder / (24 * 60 * 60));
                        remainder = remainder % (24 * 60 * 60);
                        
                        const hours = Math.floor(remainder / (60 * 60));
                        remainder = remainder % (60 * 60);
                        
                        const minutes = Math.floor(remainder / 60);
                        const seconds = remainder % 60;

                        const timeCalc = document.getElementById('timeCalc');
                        timeCalc.innerHTML = `
                            <p><strong>Total time elapsed:</strong></p>
                            <p>🕒 ${totalSeconds.toLocaleString()} seconds</p>
                            <p>- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -</p>
                            <p>📅 ${years} years</p>
                            <p>📅 ${months} months</p>
                            <p>📅 ${weeks} weeks</p>
                            <p>📅 ${days} days</p>
                            <p>⏰ ${hours} hours</p>
                            <p>⏰ ${minutes} minutes</p>
                            <p>⏰ ${seconds} seconds</p>
                        `;
                    });
            }

            // Update counters every second
            setInterval(updateCounters, 1000);
        </script>
    </body>
    </html>
    '''

@app.route('/api/nvidia-proxy/chat/completions', methods=['POST'])
def proxy_to_nvidia():
    try:
        incoming_data = request.get_json()
        current_api_key = get_next_api_key()
        
        response = requests.post(
            f"{NVIDIA_API_BASE}/chat/completions",
            json=incoming_data,
            headers={
                'Authorization': f'Bearer {current_api_key}',
                'Content-Type': 'application/json'
            },
            stream=True
        )
        
        return Response(
            stream_with_context(response.iter_content(chunk_size=8192)),
            status=response.status_code,
            content_type=response.headers.get('content-type', 'application/json')
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'error': str(e)}, 500

@app.route('/counter', methods=['GET'])
def get_counter():
    with counter_lock:
        return counters

@app.route('/status', methods=['GET'])
def get_status():
    return {
        'active': True,
        'counters': counters,
        'active_api_keys': len(api_keys)
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000)