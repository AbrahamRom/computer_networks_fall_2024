import json
import socket
import ssl
import argparse
from CharacterUtils import CharacterUtils
from HttpHelper import HttpHelper
from HTTPRequest import HTTPRequest 
from HTTPResponse import HTTPResponse 

class HTTPClient :
    def __init__(self, url, use_https=False):
        host, port, path = HttpHelper.parse_url(url)
        self.host = host
        self.port = port
        self.url = url
        self.path = path
        self.use_https = use_https
    
    def send_request(self, method: str, header: str, data: str):
        req_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        if self.use_https:
                context = ssl.create_default_context()
                req_socket = context.wrap_socket(req_socket, server_hostname=self.host)
                self.port = 443
                
        req_socket.connect((self.host, self.port))        
        request = HTTPRequest.build_http_request(method=method, uri=self.path,  headers=header, body=data)
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
            head += data.decode()
            if head.endswith(CharacterUtils.crlf * 2):
                break
        header_contents = HTTPResponse.parse_response_head(head)
        
        if "Transfer-Encoding" in header_contents["headers_fields"] and header_contents["headers_fields"]["Transfer-Encoding"] == "chunked":
                body = self.chunked_body(req_socket)
                
        elif "Content-Length" in header_contents["headers_fields"]:
            body = req_socket.recv(int(header_contents["headers_fields"]["Content-Length"])).decode()
            
            
        status_line = (
        f"{header_contents['http_version']} "
        f"{header_contents['status_code']} "
        f"{header_contents['reason_phrase']}"
    )
        return {
            "status_line": status_line,
            "http_version": header_contents['http_version'],
            "status":header_contents['status_code'],
            "reason":header_contents['reason_phrase'],
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

            crlf = b''
            while len(crlf) < 2:
                crlf += req_socket.recv(1)

        trailers = b''
        while True:
            byte = req_socket.recv(1)
            if not byte:
                break
            trailers += byte
            if trailers.endswith(CharacterUtils.crlf * 2):
                break

        return body.decode()

def parse():
    """Parses command-line arguments for making an HTTP request."""
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
    

    return {
        "method": args.method.upper(),
        "url": args.url,
        "headers": args.headers,
        "data": args.data,
    }
    
    
def main():
    args = parse()
    
    client = HTTPClient(args["url"])
    response = client.send_request(method=args["method"], header=args["headers"], data=args["data"])
    print(json.dumps(response, indent=4))
    
if __name__=="__main__":
    main()