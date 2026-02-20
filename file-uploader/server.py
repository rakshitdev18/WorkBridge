import http.server
import socketserver
import json
import base64
import os
import urllib.parse
from datetime import datetime

PORT = 3000
UPLOAD_DIR = "uploads"

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

class UploadHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/upload':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # Parse JSON data
                data = json.loads(post_data.decode('utf-8'))
                filename = data.get('filename')
                content = data.get('content')
                
                if filename and content:
                    # Decode and save file
                    file_content = base64.b64decode(content)
                    filepath = os.path.join(UPLOAD_DIR, filename)
                    
                    # Handle duplicate filenames
                    counter = 1
                    original_filepath = filepath
                    while os.path.exists(filepath):
                        name, ext = os.path.splitext(original_filepath)
                        filepath = f"{name}_{counter}{ext}"
                        counter += 1
                    
                    with open(filepath, 'wb') as f:
                        f.write(file_content)
                    
                    print(f"✅ Saved: {os.path.basename(filepath)}")
                    
                    # Send success response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'status': 'success',
                        'file': os.path.basename(filepath),
                        'path': filepath
                    }).encode())
                    return
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
                return
        
        self.send_response(404)
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/':
            # Serve the webpage
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Get list of uploaded files
            files = []
            if os.path.exists(UPLOAD_DIR):
                files = sorted(os.listdir(UPLOAD_DIR), reverse=True)[:50]  # Last 50 files
            
            # Generate HTML
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Uploaded Files</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{ 
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: #f5f5f5;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 800px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        padding: 20px;
                    }}
                    h1 {{
                        color: #333;
                        margin-bottom: 20px;
                        padding-bottom: 10px;
                        border-bottom: 2px solid #007acc;
                    }}
                    .file-list {{
                        list-style: none;
                    }}
                    .file-item {{
                        padding: 12px 15px;
                        border-bottom: 1px solid #eee;
                        display: flex;
                        align-items: center;
                        transition: background 0.2s;
                    }}
                    .file-item:hover {{
                        background: #f8f9fa;
                    }}
                    .file-item a {{
                        color: #007acc;
                        text-decoration: none;
                        flex: 1;
                        font-family: 'Monaco', 'Menlo', monospace;
                        font-size: 14px;
                    }}
                    .file-item a:hover {{
                        text-decoration: underline;
                    }}
                    .file-time {{
                        color: #999;
                        font-size: 12px;
                        margin-left: 15px;
                    }}
                    .empty {{
                        text-align: center;
                        color: #999;
                        padding: 40px;
                        font-style: italic;
                    }}
                    .status {{
                        margin-top: 20px;
                        padding: 10px;
                        background: #e8f4fd;
                        border-radius: 5px;
                        color: #007acc;
                        font-size: 14px;
                    }}
                    .refresh {{
                        text-align: right;
                        margin-bottom: 10px;
                    }}
                    .refresh button {{
                        background: #007acc;
                        color: white;
                        border: none;
                        padding: 5px 15px;
                        border-radius: 3px;
                        cursor: pointer;
                        font-size: 12px;
                    }}
                    .refresh button:hover {{
                        background: #005a9e;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📁 Uploaded Files</h1>
                    <div class="refresh">
                        <button onclick="location.reload()">↻ Refresh</button>
                    </div>
                    
                    <div class="file-list" id="fileList">
                        {''.join(f'''
                        <div class="file-item">
                            <a href="/files/{f}" target="_blank">{f}</a>
                            <span class="file-time">{datetime.fromtimestamp(os.path.getmtime(os.path.join(UPLOAD_DIR, f))).strftime('%Y-%m-%d %H:%M:%S')}</span>
                        </div>
                        ''' for f in files) if files else '<div class="empty">📪 No files uploaded yet</div>'}
                    </div>
                    
                    <div class="status">
                        ⚡ Server running on port {PORT} • {len(files)} file(s) uploaded
                    </div>
                </div>
                
                <script>
                    // Auto-refresh every 5 seconds
                    setTimeout(() => location.reload(), 5000);
                </script>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
        
        elif self.path.startswith('/files/'):
            # Serve uploaded files
            filename = self.path[7:]  # Remove '/files/'
            filepath = os.path.join(UPLOAD_DIR, filename)
            
            if os.path.exists(filepath) and os.path.isfile(filepath):
                self.send_response(200)
                # Try to determine content type
                if filename.endswith(('.txt', '.py', '.js', '.html', '.css', '.json', '.md')):
                    self.send_header('Content-type', 'text/plain')
                elif filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    self.send_header('Content-type', 'image/jpeg')
                else:
                    self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'File not found')
        
        else:
            super().do_GET()

# Run server
if __name__ == '__main__':
    print(f"""
    ╔════════════════════════════════════════╗
    ║   File Uploader Server                  ║
    ╠════════════════════════════════════════╣
    ║  • Server: http://localhost:{PORT}        ║
    ║  • Upload: http://localhost:{PORT}/upload ║
    ║  • Files: http://localhost:{PORT}/files/  ║
    ║  • Upload dir: {UPLOAD_DIR}/              ║
    ╚════════════════════════════════════════╝
    """)
    
    with socketserver.TCPServer(("", PORT), UploadHandler) as httpd:
        httpd.serve_forever()