import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor

# Reuse session for better performance
session = requests.Session()

def check_reflected_xss(session, url, params):
    try:
        response = session.get(url, params=params)
        return response
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def find_input_fields(soup):
    input_fields = soup.find_all(['input', 'textarea'])
    return [(field.get('name', ''), field.get('value', '')) for field in input_fields if field.get('name')]

def crawl_application(url):
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return find_input_fields(soup)

def test_xss_on_input_fields(url, input_fields, payloads, verbose, rate_limit):
    print(f"Testing {len(payloads)} payloads against {len(input_fields)} input fields in {url}\n")

    def test_single_payload(payload):
        params = {field_name: payload for field_name, _ in input_fields}
        response = check_reflected_xss(session, url, params)
        if response:
            for field_name, _ in input_fields:
                if verbose:
                    print(f"Payload {'detected' if payload in response.text else 'not detected'} in input field '{field_name}'\n")
            return response.status_code

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(test_single_payload, payload) for payload in payloads]

        for future in futures:
            status_code = future.result()
            if verbose:
                print(f"Response status code: {status_code}")

        if rate_limit > 0:
            print(f"Waiting for {rate_limit} seconds before sending the next batch of requests...")
            time.sleep(rate_limit)

def start_xss_test():
    url = input("Enter the URL: ")
    payload_file = input("Enter the path to the payload file: ")
    
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
