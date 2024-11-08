from flask import Flask, request, Response, stream_with_context, send_from_directory
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

NVIDIA_API_BASE = "https://integrate.api.nvidia.com/v1"

@app.route('/')
def home():
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
                height: 100vh;
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
                max-width: 500px;
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
            p {
                color: #cccccc;
                line-height: 1.6;
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
            <h1>Nvidia API Proxy</h1>
            <div class="status">
                <div class="pulse"></div>
                <p><strong>Status: Active</strong></p>
            </div>
            <p>The proxy server is running and ready to handle requests.</p>
            <div class="endpoints">
                <p><strong>Available Endpoints:</strong></p>
                <div class="endpoint">POST /api/nvidia-proxy/chat/completions</div>
                <div class="endpoint">GET /test</div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/api/nvidia-proxy/chat/completions', methods=['POST'])
def proxy_to_nvidia():
    try:
        # Get incoming data
        incoming_data = request.get_json()
        
        # Forward to Nvidia API
        response = requests.post(
            f"{NVIDIA_API_BASE}/chat/completions",
            json=incoming_data,
            headers={
                'Authorization': f'Bearer {os.getenv("NVIDIA_API_KEY")}',
                'Content-Type': 'application/json'
            },
            stream=True
        )
        
        # Return the response
        return Response(
            stream_with_context(response.iter_content(chunk_size=8192)),
            status=response.status_code,
            content_type=response.headers.get('content-type', 'application/json')
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'error': str(e)}, 500

@app.route('/test', methods=['GET'])
def test():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(debug=True, port=5000)