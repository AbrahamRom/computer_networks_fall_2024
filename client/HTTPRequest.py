from CharacterUtils import CharacterUtils
from HttpHelper import HttpHelper 
import json


class HTTPRequest:
    
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
        request_line = HTTPRequest.create_request_line(method, uri, HttpHelper.format_http_version(1, 1))
        headers_section = HTTPRequest.format_headers(headers)
        return request_line + headers_section + CharacterUtils.crlf + (body if body else "")
