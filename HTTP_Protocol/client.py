import socket
import re
import ssl
import json


def request(method, url, headers="", body=""):
    """
    Builds the request to HTTP Server
    """
    # Parse the URL to get host, port, URI, and security status
    host, port, uri, is_secure = parse_url(url)

    # Ensure headers is a list of tuples
    if isinstance(headers, dict):
        headers = list(headers.items())

    # Establish a socket connection to the server
    sock = socket_client(host, port, is_secure)

    # Build the HTTP request string
    request_string = build_request(method, host, uri, headers, body)

    # Print the request for debugging purposes
    # print(request_string)

    # Send the HTTP request to the server
    sock.sendall(request_string.encode())

    # Initialize an empty response
    response = b""

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

    response = response.decode("iso-8859-1")  # Decode the response from bytes to string

    status_code, response_headers, response_body = parse_response(response)

    # Redirect if necessary

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
        status_code, response_headers, response_body = request(
            "GET",
            dict(response_headers)["Location"],
            headers,
        )

    response_json = {
        "status": int(status_code.split()[0]),
        "headers": {key: value for key, value in response_headers},
        "body": response_body,
    }

    # print(response_json)

    return json.dumps(response_json, indent=4)


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


# request("GET", "http://google.com/")
