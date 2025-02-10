# Lista de métodos HTTP permitidos para las solicitudes
methods = ["OPTIONS", "GET", "HEAD", "POST", "PUT", "DELETE", "TRACE", "CONNECT"]

# Lista de encabezados generales que pueden estar presentes en cualquier mensaje HTTP.
# Estos encabezados controlan aspectos generales de la comunicación, como el cacheo y la 
# conexión.
generalHeaders = [
    "Cache-Control", 
    "Connection", 
    "Date", 
    "Pragma", 
    "Trailer", 
    "Transfer-Enconding",  # Nota: Puede ser un error tipográfico, lo correcto es "Transfer-Encoding"
    "Upgrade", 
    "Via", 
    "Warning"
]

# Lista de encabezados específicos de las solicitudes. 
# Estos encabezados transmiten información acerca de la solicitud, como el host, el agente del usuario, 
# y detalles de autenticación o alcance.
requestHeaders = [
    "Accept",
    "Accept-Charset",
    "Accept-Encoding",
    "Accept-Language", 
    "Authorization", 
    "Expect", 
    "From", 
    "Host", 
    "If-Match", 
    "If-Modified-Since", 
    "If-None-Match", 
    "If-Range", 
    "If-Unmodified-Since", 
    "Max-Forwards", 
    "Proxy-Authorization",
    "Range", 
    "Referer", 
    "TE", 
    "User-Agent"
]

# Lista de encabezados relacionados con la entidad del mensaje HTTP. 
# Estos encabezados se utilizan para describir el contenido del cuerpo del mensaje, como su tipo, codificación
# y longitud.
entityHeaders = [
    "Allow", 
    "Content-Encoding", 
    "Content-Language",
    "Content-Length", 
    "Content-Location", 
    "Content-MD5", 
    "Content-Range", 
    "Content-Type", 
    "Expires", 
    "Last-Modified"
]
