import socket
from threading import Thread

# Token de autorización requerido para acceder a recursos seguros
AUTHORIZED_TOKEN = "12345"

def handle_client(client_socket):
    """
    Función que maneja la comunicación con cada cliente conectado.
    Procesa la solicitud HTTP y envía la respuesta correspondiente.
    """
    try:
        # Se recibe la solicitud del cliente y se decodifica
        request = client_socket.recv(4096).decode()
        if not request.strip():  # Si la solicitud está vacía
            response = "HTTP/1.1 400 Bad Request\r\n\r\n"
            client_socket.sendall(response.encode())
            client_socket.close()
            return

        # Se extraen el método HTTP y la URI de la primera línea de la solicitud
        method, uri, _ = request.split("\r\n")[0].split(" ")
        print(f"Request received: {method} {uri}")

        # Se procesan los encabezados de la solicitud y se almacenan en un diccionario
        headers = {}
        for line in request.split("\r\n")[1:]:
            if not line:  # Se detiene al llegar a una línea vacía (separador de encabezados y cuerpo)
                break
            key, value = line.split(": ")
            headers[key] = value

        # Variables para construir la respuesta
        response_status = ""
        response_headers = ""
        response_body = ""

        # Procesamiento de la solicitud según el método HTTP
        if method == "GET":
            # Si se accede a una ruta segura, se procesa la autorización
            if uri.startswith("/secure"):
                authorized = authoritation_process(client_socket, method, uri, headers)
                if not authorized:
                    return  # Si falla la autorización, la respuesta ya fue enviada
                else:
                    response_body = "<h1>GET request successful! You accessed a protected resource.</h1>"
            else:
                response_body = "<h1>Welcome</h1>"

        elif method == "POST":
            # Para solicitudes POST en rutas seguras se verifica la autorización
            if uri.startswith("/secure"):
                authorized = authoritation_process(client_socket, method, uri, headers)
                if not authorized:
                    return
                else:
                    try:
                        # Validar la longitud del cuerpo de la solicitud
                        content_length = int(headers.get("Content-Length", 0))
                        body = request.split("\r\n\r\n")[1][:content_length]
                        # Se verifica el tipo de contenido procesando JSON, XML o texto plano
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
                            # Manejo de cuerpos de texto o tipos desconocidos
                            response_body = f"POST request successful! Plain text body received: {body}."
                    except (IndexError, ValueError) as e:
                        response_status = "HTTP/1.1 400 Bad Request"
                        response_body = f"<h1>{str(e)}</h1>"
            else:
                response_body = "<h1>POST request successful</h1>"

        elif method == "HEAD":
            # Para HEAD se retorna solo encabezados sin cuerpo
            response_headers = [
                f"Content-Length: 0",
            ]
        elif method == "PUT":
            # Ejemplo de respuesta para solicitud PUT (actualización de recurso)
            response_body = f"<h1>PUT request successful! Resource '{uri}' would be updated if this were implemented.</h1>"
        elif method == "DELETE":
            # Ejemplo de respuesta para solicitud DELETE (eliminación de recurso)
            response_body = f"<h1>DELETE request successful! Resource '{uri}' would be deleted if this were implemented.</h1>"
        elif method == "OPTIONS":
            # Respuesta para OPTIONS con métodos permitidos y sin contenido
            response_status = "HTTP/1.1 204 No Content"
            response_headers = [
                "Allow: GET, POST, HEAD, PUT, DELETE, OPTIONS, TRACE, CONNECT",
                "Content-Length: 0",
            ]
        elif method == "TRACE":
            # Para TRACE la respuesta es la misma solicitud recibida
            response_body = request
            response_headers = [
                "Content-Type: message/http",
                f"Content-Length: {len(response_body)}",
            ]
        elif method == "CONNECT":
            # En CONNECT se establece un túnel hacia el recurso solicitado
            target = uri.strip("/")
            response_body = f"CONNECT method successful! Tunneling to {target} established."
        else:
            # Para métodos no permitidos se retorna error 405
            response_status = "HTTP/1.1 405 Method Not Allowed"
            response_body = f"<h1>Method '{method}' not allowed.</h1>"

        # Si no se ha definido explícitamente un estado, se asume 200 OK
        if not response_status:
            response_status = "HTTP/1.1 200 OK"
        # Si no se han definido encabezados, se configura Content-Type y Content-Length por defecto
        if not response_headers:
            response_headers = [
                "Content-Type: text/html",
                f"Content-Length: {len(response_body)}",
            ]
        # Se construye la respuesta concatenando el estado, encabezados y cuerpo
        response = (
            response_status
            + "\r\n"
            + "\r\n".join(response_headers)
            + "\r\n\r\n"
            + response_body
        )

    except Exception as e:
        # En caso de error se envía una respuesta genérica de error interno del servidor
        response = "HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\nInternal Server Error"

    # Se envía la respuesta al cliente y se cierra la conexión
    client_socket.sendall(response.encode())
    client_socket.close()

def authoritation_process(client_socket, method, uri, headers):
    """
    Función para gestionar la autorización en solicitudes a recursos seguros.
    Se verifica la presencia y validez del encabezado Authorization.
    """
    if "Authorization" in headers:
        # Se extrae y limpia el token de autenticación
        auth_token = headers["Authorization"].replace("Bearer ", "").strip()
        if auth_token != AUTHORIZED_TOKEN:
            # Token inválido: se envía respuesta 401 Unauthorized
            response = "HTTP/1.1 401 Unauthorized\r\nContent-Type: text/html\r\n\r\n<h1>Invalid or missing authorization token.</h1>"
            client_socket.sendall(response.encode())
            client_socket.close()
            return False
        else:
            return True
    else:
        # Si falta el encabezado de autorización, se retorna 401 Unauthorized
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
        Thread(
            target=handle_client, args=(client_socket,)
        ).start()  # posiblemente coma faltante


if __name__ == "__main__":
    run_server()
