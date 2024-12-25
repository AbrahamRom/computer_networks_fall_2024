import sys
import client

if __name__ == '__main__':
    # Check if the number of command-line arguments is not equal to 2
    if len(sys.argv) != 2:
        # Print usage message and exit with status code 1
        print("Usage: python http_terminal.py <url>")
        sys.exit(1)
    else:
        # Get the URL from the command-line arguments
        url = sys.argv[1]
        # Make a GET request to the specified URL using the client module
        client.request("GET", url)