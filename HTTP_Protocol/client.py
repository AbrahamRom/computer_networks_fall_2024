import socket
import re
import ssl
import json
from CharacterUtils import CharacterUtils  # Importamos CharacterUtils para manejar caracteres especiales

def request(method, url, headers=None, body=""):
    """
    Construye y envía una solicitud HTTP al servidor.
    
    Parámetros:
      method  -> Método HTTP (GET, POST, etc.)
      url     -> URL completa a la que se hace la solicitud
      headers -> Headers en formato JSON (como string)
      body    -> Contenido del cuerpo de la solicitud
    """
        # --- Validación de métodos no soportados ---
    allowed_methods = ["GET", "POST", "HEAD", "PUT", "DELETE", "OPTIONS", "TRACE", "CONNECT"]
    if method.upper() not in allowed_methods:
        return {
            "status_line": "HTTP/1.1 405 Method Not Allowed",
            "http_version": "HTTP/1.1",
            "status": 405,
            "reason": "Method Not Allowed",
            "headers": {},
            "body": "Method not supported"
        }

    # Convertir headers de string JSON a lista de tuplas si es necesario
    if isinstance(headers, str):
        try:
            headers_dict = json.loads(headers.replace('\\"', '"'))
            headers = list(headers_dict.items())
        except:
            headers = []
    elif headers is None:
        headers = []
    
      # --- Validación de JSON malformado ---
    content_type = next((v for k, v in headers if k.lower() == "content-type"), None)
    if content_type == "application/json" and body:
        try:
            json.loads(body)
        except json.JSONDecodeError:
            return {
                "status_line": "HTTP/1.1 400 Bad Request",
                "http_version": "HTTP/1.1",
                "status": 400,
                "reason": "Bad Request",
                "headers": {},
                "body": "Malformed JSON body"
            }
    
    # Se obtiene el host, puerto, URI y el estado de seguridad (si es HTTPS) de la URL.
    host, port, uri, is_secure = parse_url(url)

    # Se establece la conexión de socket con el servidor (con soporte para TLS si es necesario).
    sock = socket_client(host, port, is_secure)

    # Se construye el string de la solicitud HTTP que se enviará.
    request_string = build_request(method, host, uri, headers, body)

    # Se envía la solicitud completa al servidor.
    sock.sendall(request_string.encode())

    # Se inicializa la variable respuesta como un objeto de bytes vacío.
    response = b""

    # Se recibe la respuesta del servidor en bloques de 4096 bytes.
    while True:
        try:
            data = sock.recv(4096)  # Se reciben datos en bloques de 4096 bytes.
            if not data:
                break   # Se sale del bucle si no se reciben más datos.
            response += data  # Se acumulan los datos recibidos.
        except socket.timeout:
            break  # Se sale del bucle en caso de que ocurra un timeout.

    # Se cierra la conexión de socket.
    sock.close()

    response = response.decode()  # Se decodifica la respuesta de bytes a una cadena.

    # Se analiza la respuesta para extraer el código de estado, los encabezados y el cuerpo
    status_code, response_headers, response_body = parse_response(response)
 # Detección de Transfer-Encoding: chunked
    headers_dict = dict(response_headers)
    if "Transfer-Encoding" in headers_dict and headers_dict["Transfer-Encoding"] == "chunked":
        response_body = handle_chunked_body(response_body)

    return {
        "status_line": f"HTTP/1.1 {status_code}",
        "http_version": "HTTP/1.1",
        "status": int(status_code),
        "reason": status_code.split(' ', 1)[1] if ' ' in status_code else "",
        "headers": headers_dict,
        "body": response_body
    }


def handle_chunked_body(body):
    """Procesa cuerpos en formato chunked"""
    decoded_body = ""
    while True:
        chunk_size_line, body = body.split(CharacterUtils.crlf, 1)
        chunk_size = int(chunk_size_line.split(';', 1)[0], 16)
        
        if chunk_size == 0:
            break
            
        decoded_body += body[:chunk_size]
        body = body[chunk_size + len(CharacterUtils.crlf):]
        
    return decoded_body

def parse_response(response):
    """
    Analiza la respuesta HTTP separándola en el código de estado, encabezados y cuerpo.
    
    Parámetros:
      response -> Cadena completa de la respuesta HTTP

    Retorna:
      status_code      -> Código de estado HTTP extraído de la línea de estado
      response_headers -> Lista de encabezados en formato [[clave, valor], ...]
      body             -> Cuerpo del mensaje de respuesta
    """
    # --- Manejo de respuestas sin cuerpo ---
    if "\r\n\r\n" not in response:
        header_section = response
        body = ""
    else:
        header_section, body = response.split("\r\n\r\n", 1)

    header_lines = header_section.split("\r\n")
    
    # --- Manejo de líneas vacías ---
    if not header_lines:
        return "000", [], ""

    status_line = header_lines[0]
    status_code = status_line.split(" ", 2)[1] if len(status_line.split()) >= 2 else "000"
    
    response_headers = []
    for line in header_lines[1:]:
        if ": " in line:
            key, value = line.split(": ", 1)
            response_headers.append([key, value])

    return status_code, response_headers, body



def build_request(method, host, uri, headers, body):
    """
    Construye el string de la solicitud HTTP a enviar.
    
    Parámetros:
      method  -> Método HTTP (GET, POST, etc.)
      host    -> Host obtenido de la URL
      uri     -> URI o path de la URL
      headers -> Lista de tuplas con los encabezados
      body    -> Cuerpo de la solicitud
    
    Retorna:
      La cadena completa de la solicitud HTTP.
    """
    
    # Se construye la línea inicial de la solicitud y se agrega el encabezado 'Host'.
    request = f"{method} {uri} HTTP/1.1\r\nHost: {host}\r\n"
    body_bytes = body.encode() if body else b""
    
    # Añadir Content-Length si hay cuerpo y no está definido
    if body and not any(k.lower() == "content-length" for (k, _) in headers):
        request += f"Content-Length: {len(body_bytes)}\r\n"
    
    # Añadir headers
    for key, value in headers:
        request += f"{key}: {value}\r\n"
    
    request += "\r\n"
    
    # Añadir cuerpo solo si existe
    if body:
        request += body
    
    return request


def socket_client(host, port, is_secure):
    """
    Crea y establece una conexión de socket con el servidor.
    
    Parámetros:
      host      -> Dirección del servidor
      port      -> Puerto de conexión
      is_secure -> Booleano que indica si se debe usar SSL (HTTPS)
    
    Retorna:
      Objeto socket conectado.
    """
    # Se crea un socket IPv4 con protocolo TCP.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Se define un timeout de 10 segundos para las operaciones del socket.
    sock.settimeout(10)

    if is_secure:  # Si es una conexión HTTPS, se envuelve el socket en un contexto SSL.
        # Se crea un contexto SSL por defecto.
        context = ssl.create_default_context()
        # Se envuelve el socket para comunicación segura.
        sock = context.wrap_socket(sock, server_hostname=host)

    # Se conecta el socket al host y puerto especificados.
    sock.connect((host, port))

    return sock


def parse_url(url):
    """
    Analiza la URL y extrae el host, puerto y URI.
    
    Parámetros:
      url -> URL completa en formato cadena
      
    Retorna:
      host, port, uri, is_secure -> Componentes extraídos. is_secure es True si es HTTPS.
    """
    # Se definen los valores por defecto: puerto 80 y sin seguridad.
    port = 80
    is_secure = False

    # Se revisa si la URL comienza con http:// o https://
    if url.startswith("http://"):
        url = url[7:]  # Se elimina el prefijo "http://"
    elif url.startswith("https://"):
        url = url[8:]  # Se elimina el prefijo "https://"
        port = 443   # Se asigna el puerto 443 para conexiones seguras
        is_secure = True

    # Se utiliza una expresión regular para extraer el host, el puerto (si existe) y la URI.
    match = re.match(r"([^:/?#]+)(?::(\d+))?(.*)", url)
    if match:
        host = match.group(1)  # Se extrae el host.
        if match.group(2):
            port = int(match.group(2))  # Se extrae el puerto si está especificado.
        uri = match.group(3) if match.group(3) else "/"  # Se extrae la URI o se asigna '/' si está vacía.
    else:
        raise ValueError("Invalid URL")  # Se arroja un error si la URL no es válida.

    return host, port, uri, is_secure  # Se retornan los componentes parseados.


def main():
    """
    Función principal que parsea los argumentos de la línea de comandos y realiza la solicitud HTTP.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Send an HTTP request.")
    
    parser.add_argument(
        "-m", "--method", type=str, required=True,
        help="HTTP method of the request (e.g., GET, POST, PUT, DELETE)"
    )
    parser.add_argument(
        "-u", "--url", type=str, required=True,
        help="Target resource URL"
    )
    parser.add_argument(
        "-H", "--headers", type=str, default="{}",
        help="Headers for the request in JSON format (e.g., '{\"Content-Type\": \"application/json\"}')"
    )
    parser.add_argument(
        "-d", "--data", type=str, default="",
        help="Body of the request (useful for POST/PUT requests)"
    )
    
    args = parser.parse_args()

    # Realizar la solicitud HTTP
    response = request(args.method, args.url, args.headers, args.data)

    # Imprimir la respuesta en formato JSON
    print(json.dumps(response, indent=4))


if __name__ == "__main__":
    main()