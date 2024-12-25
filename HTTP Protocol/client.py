import socket
import re
import ssl

methods = ["OPTIONS", "GET", "HEAD", "POST", "PUT", "DELETE", "TRACE", "CONNECT"]

def request(method, url, headers='', body=''):
    '''
    Builds the request to HTTP Server
    '''
    # Parse the URL to get host, port, URI, and security status
    host, port, uri, is_secure = parse_url(url)

    # Establish a socket connection to the server
    sock = socket_client(host, port, is_secure)

    # Build the HTTP request string
    request = build_request(method, host, uri, headers, body)

    # Print the request for debugging purposes
    print(request)

    # Send the HTTP request to the server
    sock.sendall(request.encode())

    # Initialize an empty response
    response = b''

    # Receive the response from the server
    while True:
        try:
            data = sock.recv(4096)  # Receive data in chunks of 4096 bytes
            if not data:
                break  # Exit loop if no more data is received
            response += data  # Append received data to the response
        except socket.timeout:
            break  # Exit loop if a timeout occurs

    # Close the socket connection
    sock.close()

    # Print the response from the server
    print(response.decode())

def build_request(method,host,uri,headers,body):
    '''
    Builts the request string to be sent to the server
    '''
    
    request = f"{method} {uri} HTTP/1.1\r\nHost: {host}\r\n"

    for key, value in headers: # Add headers to the request
        request += f"{key}: {value}\r\n"
    request += "\r\n" # Add a blank line to separate headers and body
    request += body # Add the body to the request

    return request

def socket_client(host, port, is_secure):
    '''
    Connect and return the socket object
    '''
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
    '''
    Parse the URL string and get host, port and URI
    '''
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
    match = re.match(r'([^:/?#]+)(?::(\d+))?(.*)', url)
    if match:
        host = match.group(1)  # Extract host
        if match.group(2):
            port = int(match.group(2))  # Extract port if specified
        uri = match.group(3) if match.group(3) else '/'  # Extract URI or set to '/'
    else:
        raise ValueError("Invalid URL")  # Raise error if URL is invalid

    return host, port, uri, is_secure  # Return parsed components
