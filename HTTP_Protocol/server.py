import socket
from threading import Thread

AUTHORIZED_TOKEN = "12345"


def handle_client(client_socket):
    try:
        request = client_socket.recv(4096).decode()
        if not request.strip():  # Empty request
            response = "HTTP/1.1 400 Bad Request\r\n\r\n"
            client_socket.sendall(response.encode())
            client_socket.close()
            return

        method, uri, _ = request.split("\r\n")[0].split(" ")

        print(f"Request received: {method} {uri}")

        headers = {}
        for line in request.split("\r\n")[1:]:
            if not line:
                break
            key, value = line.split(": ")
            headers[key] = value

        # Response structure

        response_status = ""
        response_headers = ""
        response_body = ""

        # Process the request by method

        if method == "GET":
            if uri.startswith("/secure"):
                authorized = authoritation_process(client_socket, method, uri, headers)
                if not authorized:
                    return
                else:
                    response_body = "<h1>GET request successful! You accessed a protected resource.</h1>"
            else:
                response_body = "<h1>Welcome</h1>"

        elif method == "POST":
            if uri.startswith("/secure"):
                authorized = authoritation_process(client_socket, method, uri, headers)
                if not authorized:
                    return
                else:
                    try:
                        # Validate lenght
                        content_length = int(headers.get("Content-Length", 0))
                        body = request.split("\r\n\r\n")[1][:content_length]

                        content_type = headers.get("Content-Type", "text/plain")
                        if content_type == "application/json":
                            try:
                                import json

                                json.loads(body)  # Intentar parsear como JSON
                                response_body = f"<h1>POST request successful! JSON body received: {body}.</h1>"
                            except json.JSONDecodeError:
                                raise ValueError("Malformed JSON body")
                        elif content_type == "application/xml":
                            try:
                                import xml.etree.ElementTree as ET

                                ET.fromstring(body)  # Intentar parsear como XML
                                response_body = f"<h1>POST request successful! XML body received: {body}.</h1>"
                            except ET.ParseError:
                                raise ValueError("Malformed XML body")
                        else:
                            # Manejar cuerpos de texto o desconocidos
                            response_body = f"POST request successful! Plain text body received: {body}."
                    except (IndexError, ValueError) as e:
                        response_status = "HTTP/1.1 400 Bad Request"
                        response_body = f"<h1>{str(e)}</h1>"
            else:
                response_body = "<h1>POST request successful</h1>"

        elif method == "HEAD":
            response_headers = [
                f"Content-Length: 0",
            ]
        elif method == "PUT":
            response_body = f"<h1>PUT request successful! Resource '{uri}' would be updated if this were implemented.</h1>"
        elif method == "DELETE":
            response_body = f"<h1>DELETE request successful! Resource '{uri}' would be deleted if this were implemented.</h1>"
        elif method == "OPTIONS":
            response_status = "HTTP/1.1 204 No Content"
            response_headers = [
                "Allow: GET, POST, HEAD, PUT, DELETE, OPTIONS, TRACE, CONNECT",
                "Content-Length: 0",
            ]
        elif method == "TRACE":
            response_body = request
            response_headers = [
                "Content-Type: message/http",
                f"Content-Length: {len(response_body)}",
            ]
        elif method == "CONNECT":
            target = uri.strip("/")
            response_body = (
                f"CONNECT method successful! Tunneling to {target} established."
            )
        else:
            response_status = "HTTP/1.1 405 Method Not Allowed"
            response_body = f"<h1>Method '{method}' not allowed.</h1>"

        if not response_status:
            response_status = "HTTP/1.1 200 OK"
        if not response_headers:
            response_headers = [
                "Content-Type: text/html",
                f"Content-Length: {len(response_body)}",
            ]
        response = (
            response_status
            + "\r\n"
            + "\r\n".join(response_headers)
            + "\r\n\r\n"
            + response_body
        )

    except Exception as e:
        response = "HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\nInternal Server Error"

    client_socket.sendall(response.encode())
    client_socket.close()


def authoritation_process(client_socket, method, uri, headers):
    if "Authorization" in headers:
        auth_token = headers["Authorization"].replace("Bearer ", "").strip()
        if auth_token != AUTHORIZED_TOKEN:
            response = "HTTP/1.1 401 Unauthorized\r\nContent-Type: text/html\r\n\r\n<h1>Invalid or missing authorization token.</h1>"
            client_socket.sendall(response.encode())
            client_socket.close()
            return False
        else:
            return True
    else:
        response = "HTTP/1.1 401 Unauthorized\r\nContent-Type: text/html\r\n\r\n<h1>Authorization header missing.</h1>"
        client_socket.sendall(response.encode())
        client_socket.close()
        return False


def run_server(host="localhost", port=8080):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Servidor escuchando en {host}:{port}")

    while True:
        client_socket, client_address = server.accept()
        print(f"Conexión entrante de {client_address}")
        Thread(target=handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    run_server()
