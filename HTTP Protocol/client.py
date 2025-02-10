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
    Analiza la respuesta HTTP separándola en el código de estado, encabezados y cuerpo.
    
    Parámetros:
      response -> Cadena completa de la respuesta HTTP

    Retorna:
      status_code      -> Código de estado HTTP extraído de la línea de estado
      response_headers -> Lista de encabezados en formato [[clave, valor], ...]
      body             -> Cuerpo del mensaje de respuesta
    """
    # Se divide la respuesta en dos secciones: encabezado y cuerpo.
    header_section, body = response.split("\r\n\r\n", 1)

    # Se separan las líneas de los encabezados.
    header_lines = header_section.split("\r\n")

    # La primera línea es la línea de estado (por ejemplo "HTTP/1.1 200 OK").
    status_line = header_lines[0]

    # Se extrae el código de estado (porción después del primer espacio).
    status_code = status_line.split(" ", 1)[1]

    # Se recorren las líneas restantes para extraer cada encabezado.
    response_headers = []
    for line in header_lines[1:]:
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

    # Se agregan los encabezados proporcionados.
    for key, value in headers:
        request += f"{key}: {value}\r\n"
    # Se deja una línea en blanco para separar los encabezados del cuerpo.
    request += "\r\n"
    # Se añade el cuerpo de la solicitud (si lo hubiese).
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


# Llamada de prueba a la función request para una URL externa.
request("GET", "http://google.com/")
