

class HttpHelper:
    
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