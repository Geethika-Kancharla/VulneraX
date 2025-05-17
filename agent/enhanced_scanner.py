import json
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

class EnhancedSecurityScanner:
    def __init__(self, endpoints_file, output_file):
        self.endpoints_file = endpoints_file
        self.output_file = output_file
        self.results = []
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def load_endpoints(self):
        with open(self.endpoints_file, 'r') as f:
            return json.load(f)
            
    def analyze_endpoint(self, url):
        # Skip non-HTML resources
        if any(ext in url.lower() for ext in ['.css', '.js', '.svg', '.png', '.jpg', '.jpeg', '.gif']):
            return None
            
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            if not response.ok or 'text/html' not in response.headers.get('Content-Type', ''):
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract the path from the URL
            from urllib.parse import urlparse
            path = urlparse(url).path
            if not path:
                path = "/"
                
            endpoint_data = {
                "path": path,
                "methods": self.detect_methods(soup, url),
                "form_fields": self.extract_form_fields(soup, url)
            }
            
            # Add API endpoints if detected
            api_endpoints = self.detect_api_endpoints(soup, response.text, url)
            if api_endpoints:
                endpoint_data["api_endpoints"] = api_endpoints
                
            return endpoint_data
            
        except Exception as e:
            print(f"Error analyzing {url}: {str(e)}")
            return None
            
    def detect_methods(self, soup, url):
        methods = ["GET"]  # Default method is GET
        
        # Check for forms with POST method
        forms = soup.find_all('form')
        for form in forms:
            form_method = form.get('method', 'get').upper()
            if form_method not in methods:
                methods.append(form_method)
                
        # Look for JavaScript fetch/axios calls with methods
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                # Look for fetch with method specification
                fetch_patterns = re.finditer(r'fetch\s*\(\s*[\'"].*?[\'"]\s*,\s*\{\s*method\s*:\s*[\'"](\w+)[\'"]', script.string)
                for match in fetch_patterns:
                    method = match.group(1).upper()
                    if method not in methods:
                        methods.append(method)
                        
                # Look for axios calls
                axios_patterns = re.finditer(r'axios\.(get|post|put|delete|patch)', script.string)
                for match in axios_patterns:
                    method = match.group(1).upper()
                    if method not in methods:
                        methods.append(method)
                        
        return methods
        
    def extract_form_fields(self, soup, url):
        form_fields = []
        forms = soup.find_all('form')
        
        for form in forms:
            inputs = form.find_all(['input', 'textarea', 'select'])
            
            for inp in inputs:
                if inp.name == 'input' and inp.get('type') == 'submit':
                    continue
                    
                field = {
                    "name": inp.get('name', ''),
                    "type": inp.get('type', 'text') if inp.name == 'input' else inp.name,
                    "required": inp.has_attr('required')
                }
                
                # Add placeholder if available
                if inp.has_attr('placeholder'):
                    field["placeholder"] = inp.get('placeholder')
                    
                # Add options for select elements
                if inp.name == 'select':
                    options = inp.find_all('option')
                    field["options"] = [opt.get('value', '') for opt in options if opt.get('value')]
                    
                if field["name"]:  # Only add fields with names
                    form_fields.append(field)
                    
        return form_fields
        
    def detect_api_endpoints(self, soup, html_content, base_url):
        api_endpoints = []
        
        # Look for API endpoints in JavaScript
        api_patterns = [
            r'(?:url|endpoint|api):\s*[\'"](/api/[^\'"]*)[\'"]',
            r'(?:fetch|axios)\s*\(\s*[\'"](?:/api/[^\'"]*)[\'"]',
            r'(?:fetch|axios)\s*\(\s*[\'"](?:https?://[^/]+/api/[^\'"]*)[\'"]'
        ]
        
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                for pattern in api_patterns:
                    matches = re.finditer(pattern, script.string)
                    for match in matches:
                        endpoint = match.group(1)
                        if endpoint.startswith('/'):
                            endpoint = urljoin(base_url, endpoint)
                        api_endpoints.append({
                            "url": endpoint,
                            "method": "unknown"  # Would need more context to determine method
                        })
                        
        return api_endpoints
        
    def scan(self):
        endpoints = self.load_endpoints()
        
        for url in endpoints:
            print(f"Analyzing: {url}")
            result = self.analyze_endpoint(url)
            if result:
                self.results.append(result)
                
        self.save_results()
        
    def save_results(self):
        with open(self.output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Results saved to {self.output_file}")
        
if __name__ == "__main__":
    scanner = EnhancedSecurityScanner(
        endpoints_file="/Users/yuktha/Desktop/maheshbabu/example/agent/scan_results/endpoints.json",
        output_file="/Users/yuktha/Desktop/maheshbabu/example/agent/scan_results/detailed_endpoints.json"
    )
    scanner.scan()