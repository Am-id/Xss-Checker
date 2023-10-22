import requests
from bs4 import BeautifulSoup
import time

def check_reflected_xss(url, payload):
    response = requests.get(url, params={'input': payload})
    return response

def find_input_fields(soup):
    input_fields = soup.find_all(['input', 'textarea'])
    return [(field.get('name', ''), field.get('value', '')) for field in input_fields]

def crawl_application(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    input_fields = find_input_fields(soup)
    return input_fields

def test_xss_on_input_fields(url, input_fields, payloads, verbose, rate_limit):
    print(f"Testing {len(payloads)} payloads against {len(input_fields)} input fields in {url}\n")

    for payload in payloads:
        for field_name, field_value in input_fields:
            test_url = url
            if "?" in url:
                test_url += f"&{field_name}={payload}"
            else:
                test_url += f"?{field_name}={payload}"

            if verbose:
                print(f"Sending request to: {test_url}")

            response = check_reflected_xss(test_url, payload)
            print(f"Response status code: {response.status_code}")
            print(f"Payload {'detected' if payload in response.text else 'not detected'} in input field '{field_name}'\n")

            if rate_limit > 0:
                print(f"Waiting for {rate_limit} seconds before sending the next request...")
                time.sleep(rate_limit)

def start_xss_test():
    url = input("Enter the URL: ")
    payload_file = input("Enter the path to the payload file: ")
    payloads = []

    if not url or not payload_file:
        print("Please provide a URL and payload file.")
        return

    with open(payload_file, 'r', encoding='utf-8', errors='ignore') as file:
        payloads = [line.strip() for line in file]

    verbose = input("Enable verbose output? (yes/no): ").lower() == 'yes'
    rate_limit = int(input("Enter the rate limit (seconds): "))

    input_fields = crawl_application(url)
    test_xss_on_input_fields(url, input_fields, payloads, verbose, rate_limit)

if __name__ == "__main__":
    start_xss_test()
