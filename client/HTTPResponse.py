from CharacterUtils import CharacterUtils
import re


class HTTPResponse:
    
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