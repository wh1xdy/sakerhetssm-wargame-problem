import http.server
import ssl

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        # Read the length of the POST body from headers
        content_length = int(self.headers.get('Content-Length', 0))
        # Read the body data
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # Print the received POST data
        print("Received POST data:", post_data)

        # Send an HTTP 200 response
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")  # Respond to the client

def run_server(certfile='server.crt', keyfile='server.key', port=4443):
    server_address = ('127.0.0.1', port)
    
    # Create the base HTTP server
    httpd = http.server.HTTPServer(server_address, MyHandler)
    
    # Wrap the server socket with SSL
    httpd.socket = ssl.wrap_socket(
        httpd.socket,
        certfile=certfile, 
        keyfile=keyfile,
        server_side=True
    )
    
    print(f"Serving on https://127.0.0.1:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()

