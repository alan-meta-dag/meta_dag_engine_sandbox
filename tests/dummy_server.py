from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 讀取請求
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length)

        # 固定回傳格式（模擬 openai/chat）
        reply = {
            "choices": [
                {"message": {"content": "dummy reply"}}
            ]
        }

        response = json.dumps(reply).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)


if __name__ == "__main__":
    print("Dummy server listening on http://localhost:8000/chat")
    server = HTTPServer(("localhost", 8000), Handler)
    server.serve_forever()
