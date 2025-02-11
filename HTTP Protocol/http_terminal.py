import client
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTTP client", add_help=False)
    parser.add_argument("-m", "--method", required=True)
    parser.add_argument("-u", "--url", required=True)
    parser.add_argument(
        "-h",
        "--header",
        type=str,
        default="{}",
    )
    parser.add_argument("-d", "--data", type=str, default="")

    args = parser.parse_args()

    method = args.method
    url = args.url
    headers = eval(
        args.header
    )  # Convert string representation of dictionary to actual dictionary
    data = args.data

    response = client.request(method, url, headers=headers, body=data)
    # print(response)
