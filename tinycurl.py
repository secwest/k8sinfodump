import sys
import urllib.request
import ssl
import http.cookiejar
import json
import os

def send_request(url, method, data=None, headers=None, auth=None, verbose=False, include_header=False, output_file=None):
    context = ssl._create_unverified_context()
    request = urllib.request.Request(url, method=method)

    if headers:
        for key, value in headers.items():
            request.add_header(key, value)

    if auth:
        user, password = auth
        credentials = f'{user}:{password}'
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        request.add_header('Authorization', f'Basic {encoded_credentials}')

    if data:
        if isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
        else:
            data = data.encode('utf-8')
        request.add_header('Content-Type', 'application/json')
        request.data = data

    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    try:
        with opener.open(request, context=context) as response:
            output = response.read().decode('utf-8')
            if include_header:
                header_info = str(response.info())
                output = header_info + output

            if output_file:
                with open(output_file, 'w') as file:
                    file.write(output)

            if verbose:
                print(f"URL: {url}")
                print(f"Method: {method}")
                print(f"Status Code: {response.status}")
                print(f"Response: {output}")

            return output

    except Exception as e:
        if verbose:
            print(f"Error: {e}")
        return f"Error: {e}"

def parse_arguments(args):
    url = args[1]
    method = "GET"
    data = None
    headers = {}
    auth = None
    verbose = False
    include_header = False
    output_file = None

    for i in range(2, len(args)):
        if args[i] == '-o':
            output_file = args[i + 1]
        elif args[i] == '-u':
            auth = tuple(args[i + 1].split(":"))
        elif args[i] == '-v':
            verbose = True
        elif args[i] == '-i':
            include_header = True
        elif args[i] == '-X':
            method = args[i + 1]
        elif args[i] == '-d':
            data = args[i + 1]
        elif args[i] == '-H':
            key, value = args[i + 1].split(": ")
            headers[key] = value

    return url, method, data, headers, auth, verbose, include_header, output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <URL> [options]")
        sys.exit(1)

    url, method, data, headers, auth, verbose, include_header, output_file = parse_arguments(sys.argv)
    result = send_request(url, method, data, headers, auth, verbose, include_header, output_file)
    
    if result and not output_file:
        print(result)

# Note: This script implements basic functionality of curl options.
# It does not cover all features and options available in curl.
