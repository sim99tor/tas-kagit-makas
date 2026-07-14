import http.server
import socketserver
import socket
import os
import webbrowser

PORT = 8000
MAX_PORT_TRIES = 10
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    pass

os.chdir(SCRIPT_DIR)


def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "localhost"


def create_server(port: int):
    for attempt in range(MAX_PORT_TRIES):
        try:
            server = socketserver.ThreadingTCPServer(("0.0.0.0", port), Handler)
            return server, port
        except OSError:
            port += 1
    raise OSError(f"Portları bağlayamadım: {PORT}..{PORT + MAX_PORT_TRIES - 1}")


def main() -> None:
    local_ip = get_local_ip()
    server, bound_port = create_server(PORT)
    url_local = f"http://localhost:{bound_port}/rock-paper-scissors.html"
    url_network = f"http://{local_ip}:{bound_port}/rock-paper-scissors.html"

    print("Servis başlatılıyor. Tarayıcıda açmak için:")
    print(f"  {url_local}")
    print("Aynı ağdaki arkadaşlar için:")
    print(f"  {url_network}")
    print("Sunucu durdurmak için Ctrl+C basın.")

    webbrowser.open(url_local)
    with server:
        server.serve_forever()


if __name__ == "__main__":
    main()
