import requests
import time
import sys
import json

def check_url(url):
    try:
        response = requests.get(url)
        return response.status_code
    except requests.RequestException:
        return None

def main():
    url = sys.argv[1]
    interval = int(sys.argv[2])
    
    while True:
        status_code = check_url(url)
        event = {
            "status": status_code
        }
        print(json.dumps(event))
        sys.stdout.flush()
        time.sleep(interval)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: url_check.py <url> <interval>")
        sys.exit(1)
    
    main()
