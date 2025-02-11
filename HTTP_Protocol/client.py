import socket
import ssl
import argparse
import json
import re
from CharacterUtils import CharacterUtils

class HTTPClient:
    def __init__(self, url):
        host, port, path = parse_url(url)
        self.host = host
        self.port = port
        self.path = path
        self.use_https = url.startswith("https://")

    def send_request(self, method: str, headers: str, data: str):
        req_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        if self.use_https:
            context = ssl.create_default_context()
            req_socket = context.wrap_socket(req_socket, server_hostname=self.host)
            self.port = 443
            
        req_socket.connect((self.host, self.port))        
        request = build_http_request(method=method, uri=self.path, headers=headers, body=data)
        req_socket.send(request.encode())
        response = self.receive_response(req_socket)
        req_socket.close()
        return response

    
     
    def receive_response(self, req_socket: socket.socket):
        head = ""
        while True:
            data = req_socket.recv(1)
            if not data:
                break
            head += data.decode("iso-8859-1")
            if head.endswith(CharacterUtils.crlf * 2):
                break
        
        header_contents = parse_response_head(head)
        body = ""
        
        if "Transfer-Encoding" in header_contents["headers_fields"] and header_contents["headers_fields"]["Transfer-Encoding"] == "chunked":
            body = self.chunked_body(req_socket)
        elif "Content-Length" in header_contents["headers_fields"]:
            body = req_socket.recv(int(header_contents["headers_fields"]["Content-Length"])).decode("iso-8859-1")
        
        status_line = f"{header_contents['http_version']} {header_contents['status_code']} {header_contents['reason_phrase']}"
        return {
            "status_line": status_line,
            "http_version": header_contents['http_version'],
            "status": header_contents['status_code'],
            "reason": header_contents['reason_phrase'],
            "headers": header_contents["headers_fields"],
            "body": body
        }



    
    def chunked_body(self, req_socket: socket.socket):
        body = b''
        while True:
            chunk_size_line = b''
            while True:
                byte = req_socket.recv(1)
                if not byte:
                    raise ConnectionError("Unexpected EOF")
                chunk_size_line += byte
                if chunk_size_line.endswith(CharacterUtils.crlf.encode()):
                    break
            
            chunk_size_str = chunk_size_line.strip().split(b';', 1)[0]
            chunk_size = int(chunk_size_str, 16)
            if chunk_size == 0:
                break
            
            chunk_data = b''
            while len(chunk_data) < chunk_size:
                remaining = chunk_size - len(chunk_data)
                chunk_data += req_socket.recv(remaining)
            
            body += chunk_data
            
            crlf = req_socket.recv(2)
        
        return body.decode("iso-8859-1")


def parse_response_head(head: str) -> dict:
        """Parses the response head to extract the HTTP version, status code, reason phrase, and headers."""
        status_line, headers_section = head.split(CharacterUtils.crlf, 1)
        headers_list = headers_section.split(CharacterUtils.crlf)
        
        header_fields = {}
        for header in headers_list:
            if not header:
                continue
            key, value = re.split(r":\s+", header, 1)
            header_fields[key] = value

        http_version, status_code, reason_phrase = status_line.split(CharacterUtils.space, 2)

        return {
            "http_version": http_version,
            "status_code": int(status_code),
            "reason_phrase": reason_phrase,
            "headers_fields": header_fields
        }


def parse_args():
    parser = argparse.ArgumentParser(description="Send an HTTP request.")
    parser.add_argument("-m", "--method", required=True, help="HTTP method")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-H", "--headers", default="{}", help="Headers in JSON format")
    parser.add_argument("-d", "--data", default="", help="Request body")
    return vars(parser.parse_args())

def main():
    args = parse_args()
    client = HTTPClient(args["url"])
    response = client.send_request(
        method=args["method"].upper(),
        headers=args["headers"],
        data=args["data"]
    )
    print(json.dumps(response, indent=4))

def format_http_version(min: int, max: int):
    return "HTTP" + "/" + str(min) + '.' + str(max)

    
def parse_url(url: str):
    if url.startswith("http://"):
        url = url[7:] 
        default_port = 80
    elif url.startswith("https://"):
        url = url[8:] 
        default_port = 443
    else:
        default_port = 80

    # Split the host and path
    split_index = url.find("/")
    if split_index == -1:
        domain_part = url
        path = "/"
    else:
        domain_part = url[:split_index]
        path = url[split_index:]

    # Extract port if specified
    port_index = domain_part.find(":")
    if port_index == -1:
        host = domain_part
        port = default_port
    else:
        host = domain_part[:port_index]
        port = int(domain_part[port_index + 1:])

    return host, port, path

def is_supported_method(method: str) -> bool:
    """Checks if the given method is a valid HTTP method."""
    return method in ["OPTIONS", "GET", "HEAD", "POST", "PUT", "DELETE", "TRACE", "CONNECT"]

    
def create_request_line(method: str, uri: str, http_version: str) -> str:
    """Constructs the request line using the HTTP method, URI, and version."""
    separator = CharacterUtils.space
    line_break = CharacterUtils.crlf
    return method + separator + uri + separator + http_version + line_break

    
def format_headers(headers_json: str) -> str:
    """Formats HTTP headers from a JSON string representation."""
    if not headers_json:
        return ""
    headers_dict = json.loads(headers_json)
    headers = ""
    for key, value in headers_dict.items():
        headers += key + ": " + value + CharacterUtils.crlf
    return headers


def build_http_request(method: str, uri: str, headers: str = None, body: str = None) -> str:
    """Builds the complete HTTP request by assembling the request line, headers, and body."""
    request_line = create_request_line(method, uri, format_http_version(1, 1))
    headers_section = format_headers(headers)
    return request_line + headers_section + CharacterUtils.crlf + (body if body else "")



if __name__ == "__main__":
    main()