# Se importa el módulo client que contiene la lógica para realizar solicitudes HTTP
import client
# Se importa el módulo argparse para manejar los argumentos de la línea de comandos
import argparse

# Punto de entrada principal cuando se ejecuta este script
if __name__ == "__main__":
    # Se crea un objeto ArgumentParser con una descripción de la aplicación
    parser = argparse.ArgumentParser(description="HTTP client")
    
    # Se define el argumento obligatorio -m / --method para especificar el método HTTP (ej. GET, POST)
    parser.add_argument("-m", "--method", required=True, help="HTTP method, e.g., GET")
    
    # Se define el argumento obligatorio -u / --url para la URL de destino de la solicitud
    parser.add_argument(
        "-u", "--url", required=True, help="URL, e.g., http://localhost:4333/example"
    )
    
    # Se define el argumento opcional -H / --header para pasar encabezados en formato JSON (por defecto se usa un diccionario vacío)
    parser.add_argument(
        "-H",
        "--header",
        type=str,
        default="{}",
        help='HTTP headers in JSON format, e.g., {"User-Agent": "device"}',
    )
    
    # Se define el argumento opcional -d / --data para proveer el contenido del cuerpo en solicitudes POST/PUT
    parser.add_argument(
        "-d", "--data", type=str, default="", help="Body content for POST/PUT requests"
    )
    
    # Se analiza la línea de comandos y se obtienen los argumentos
    args = parser.parse_args()

    # Se asignan los valores obtenidos a variables locales
    method = args.method
    url = args.url
    # Se convierte la representación en cadena del diccionario de encabezados a un objeto diccionario real
    headers = eval(args.header)
    data = args.data

    # Se invoca la función request del módulo client con los parámetros proporcionados
    response = client.request(method, url, headers=headers, body=data)
    
    # Se imprime la respuesta obtenida de la solicitud HTTP
    print(response)