import client
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTTP client")
    parser.add_argument("-m", "--method", required=True, help="HTTP method, e.g., GET")
    parser.add_argument(
        "-u", "--url", required=True, help="URL, e.g., http://localhost:4333/example"
    )
    parser.add_argument(
        "-H",
        "--header",
        type=str,
        default="{}",
        help='HTTP headers in JSON format, e.g., {"User-Agent": "device"}',
    )
    parser.add_argument(
        "-d", "--data", type=str, default="", help="Body content for POST/PUT requests"
    )

    args = parser.parse_args()

    method = args.method
    url = args.url
    headers = eval(
        args.header
    )  # Convert string representation of dictionary to actual dictionary
    data = args.data

    response = client.request(method, url, headers=headers, body=data)
    print(response)
