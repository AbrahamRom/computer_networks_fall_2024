import socket
import re
import ssl


def request(method, url, headers="", body=""):
    """
    Construye y envía una solicitud HTTP al servidor.
    
    Parámetros:
      method  -> Método HTTP (GET, POST, etc.)
      url     -> URL completa a la que se hace la solicitud
      headers -> Lista de tuplas con encabezados [(clave, valor), ...]
      body    -> Contenido del cuerpo de la solicitud
    """
    # Se obtiene el host, puerto, URI y el estado de seguridad (si es HTTPS) de la URL.
    host, port, uri, is_secure = parse_url(url)

     # Se establece la conexión de socket con el servidor (con soporte para TLS si es necesario).
    sock = socket_client(host, port, is_secure)

    # Se construye el string de la solicitud HTTP que se enviará.
    request_string = build_request(method, host, uri, headers, body)

    # Se imprime la solicitud para fines de depuración.
    print(request_string)

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
            response += data # Se acumulan los datos recibidos.
        except socket.timeout:
            break  # Se sale del bucle en caso de que ocurra un timeout.

    # Se cierra la conexión de socket.
    sock.close()

    response = response.decode() # Se decodifica la respuesta de bytes a una cadena.

    # Se analiza la respuesta para extraer el código de estado, los encabezados y el cuerpo
    status_code, response_headers, response_body = parse_response(response)

     # Si es necesario, se realiza una redirección en base al código de estado y la presencia de un encabezado Location:

    if (
        status_code.startswith("300") or status_code.startswith("305")
    ) and "Location" in dict(response_headers):
        print("Redirecting to: ", dict(response_headers)["Location"])
        status_code, response_headers, response_body = request(
            method,
            dict(response_headers)["Location"],
            headers,
        )
    elif (
        (
            status_code.startswith("301")
            or status_code.startswith("302")
            or status_code.startswith("307")
        )
        and "Location" in dict(response_headers)
        and (method == "GET" or method == "HEAD")
    ):
        print("Redirecting to: ", dict(response_headers)["Location"])
        status_code, response_headers, response_body = request(
            method,
            dict(response_headers)["Location"],
            headers,
        )
    elif status_code.startswith("303") and "Location" in dict(response_headers):
        print("Redirecting to: ", dict(response_headers)["Location"])
          # En este caso se fuerza el método GET en la redirección.
        status_code, response_headers, response_body = request(
            "GET",
            dict(response_headers)["Location"],
            headers,
        )

     # Se retorna el código de estado, los encabezados y el cuerpo obtenidos de la respuesta.
    return status_code, response_headers, response_body


def parse_response(response):
    """
    Parses the HTTP response into status code, headers, and body
    """
    # Split the response into headers and body
    header_section, body = response.split("\r\n\r\n", 1)

    # Split the header section into individual lines
    header_lines = header_section.split("\r\n")

    # Extract the status line (first line of the header section)
    status_line = header_lines[0]

    # Extract the status code from the status line
    status_code = status_line.split(" ", 1)[1]

    # Extract the headers from the remaining lines
    response_headers = []
    for line in header_lines[1:]:
        key, value = line.split(": ", 1)
        response_headers.append([key, value])

    # print(response_headers)

    return status_code, response_headers, body


def build_request(method, host, uri, headers, body):
    """
    Builts the request string to be sent to the server
    """

    request = f"{method} {uri} HTTP/1.1\r\nHost: {host}\r\n"

    for key, value in headers:  # Add headers to the request
        request += f"{key}: {value}\r\n"
    request += "\r\n"  # Add a blank line to separate headers and body
    request += body  # Add the body to the request

    return request


def socket_client(host, port, is_secure):
    """
    Connect and return the socket object
    """
    # Create a socket object with IPv4 and TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set a timeout of 10 seconds for the socket operations
    sock.settimeout(10)

    if is_secure:  # If the URL is https, wrap the socket with SSL
        # Create a default SSL context
        context = ssl.create_default_context()
        # Wrap the socket with SSL for secure communication
        sock = context.wrap_socket(sock, server_hostname=host)

    # Connect the socket to the specified host and port
    sock.connect((host, port))

    # Return the connected socket object
    return sock


def parse_url(url):
    """
    Parse the URL string and get host, port and URI
    """
    # Default port and security
    port = 80
    is_secure = False

    # Check if the URL starts with http:// or https://
    if url.startswith("http://"):
        # Remove the http:// prefix
        url = url[7:]
    elif url.startswith("https://"):
        # Remove the https:// prefix and set port to 443
        url = url[8:]
        port = 443
        is_secure = True

    # Extract host, port, and URI using regex
    match = re.match(r"([^:/?#]+)(?::(\d+))?(.*)", url)
    if match:
        host = match.group(1)  # Extract host
        if match.group(2):
            port = int(match.group(2))  # Extract port if specified
        uri = match.group(3) if match.group(3) else "/"  # Extract URI or set to '/'
    else:
        raise ValueError("Invalid URL")  # Raise error if URL is invalid

    return host, port, uri, is_secure  # Return parsed components


request("GET", "http://google.com/")
