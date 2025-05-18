import requests
import time
import json
import logging
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from zapv2 import ZAPv2
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init()

class SecurityScanner:
    def __init__(self, target_url, output_dir="scan_results"):
        self.target_url = target_url
        self.output_dir = output_dir
        self.discovered_endpoints = {}  
        self.subdomains = set()
        self.forms = []
        self.attack_surfaces = []
        
        # Configure logging
        # logging.basicConfig(
        #     level=logging.INFO,
        #     format='%(asctime)s - %(levelname)s - %(message)s',
        #     handlers=[
        #         logging.FileHandler(f'{output_dir}/scan.log'),
        #         logging.StreamHandler()
        #     ]
        # )
        self.logger = logging.getLogger(__name__)
        
        # Initialize ZAP API
        self.zap = ZAPv2(
            proxies={'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}
        )

    def validate_url(self):
        """Validate if the URL is accessible and properly formatted."""
        try:
            parsed = urlparse(self.target_url)
            if parsed.scheme not in ["http", "https"]:
                raise ValueError("URL must start with http:// or https://")
            
            self.logger.info(f"{Fore.BLUE}Validating URL: {self.target_url}{Style.RESET_ALL}")
            response = requests.get(self.target_url, timeout=10, 
                                 headers={'User-Agent': 'SecurityScanner/1.0'})
            
            if response.status_code < 400:
                self.logger.info(f"{Fore.GREEN}URL is valid and accessible{Style.RESET_ALL}")
                return True
            else:
                self.logger.error(f"{Fore.RED}URL returned status code: {response.status_code}{Style.RESET_ALL}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"{Fore.RED}Error accessing URL: {str(e)}{Style.RESET_ALL}")
            return False
        except ValueError as e:
            self.logger.error(f"{Fore.RED}{str(e)}{Style.RESET_ALL}")
            return False

    def analyze_endpoint_details(self, url):
        """Analyze an endpoint for forms, inputs, and other details."""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            endpoint_details = {
                'url': url,
                'forms': [],
                'inputs': [],
                'buttons': [],
                'links': []
            }
            
            # Analyze forms
            forms = soup.find_all('form')
            for form in forms:
                form_data = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get'),
                    'id': form.get('id', ''),
                    'class': form.get('class', []),
                    'inputs': []
                }
                
                # Get all inputs within the form
                for input_field in form.find_all(['input', 'textarea', 'select']):
                    input_data = {
                        'type': input_field.get('type', 'text'),
                        'name': input_field.get('name', ''),
                        'id': input_field.get('id', ''),
                        'required': input_field.has_attr('required'),
                        'placeholder': input_field.get('placeholder', ''),
                        'value': input_field.get('value', ''),
                        'tag': input_field.name
                    }
                    form_data['inputs'].append(input_data)
                
                endpoint_details['forms'].append(form_data)
            
            # Find standalone inputs
            for input_field in soup.find_all(['input', 'textarea', 'select']):
                if not input_field.find_parent('form'):
                    input_data = {
                        'type': input_field.get('type', 'text'),
                        'name': input_field.get('name', ''),
                        'id': input_field.get('id', ''),
                        'required': input_field.has_attr('required'),
                        'placeholder': input_field.get('placeholder', ''),
                        'value': input_field.get('value', ''),
                        'tag': input_field.name
                    }
                    endpoint_details['inputs'].append(input_data)
            
            # Find buttons
            for button in soup.find_all('button'):
                button_data = {
                    'type': button.get('type', ''),
                    'name': button.get('name', ''),
                    'id': button.get('id', ''),
                    'text': button.get_text(strip=True),
                    'class': button.get('class', [])
                }
                endpoint_details['buttons'].append(button_data)
            
            # Find links
            for link in soup.find_all('a'):
                link_data = {
                    'href': link.get('href', ''),
                    'text': link.get_text(strip=True),
                    'id': link.get('id', ''),
                    'class': link.get('class', [])
                }
                endpoint_details['links'].append(link_data)
            
            return endpoint_details
            
        except Exception as e:
            self.logger.warning(f"Error analyzing endpoint {url}: {str(e)}")
            return None

    def discover_endpoints(self):
        """Discover endpoints using recursive crawling and ZAP scanning."""
        try:
            self.logger.info(f"{Fore.BLUE}Starting endpoint discovery{Style.RESET_ALL}")
            
            # Configure ZAP context
            context_id = self.zap.context.new_context('scan_context')
            self.zap.context.include_in_context('scan_context', f"^{self.target_url}.*$")
            
            # Start Spider scan
            scan_id = self.zap.spider.scan(self.target_url)
            
            # Monitor spider progress
            while int(self.zap.spider.status(scan_id)) < 100:
                progress = self.zap.spider.status(scan_id)
                self.logger.info(f"Spider progress: {progress}%")
                time.sleep(2)
            
            # Get discovered URLs
            urls = self.zap.spider.results(scan_id)
            for url in urls:
                self.logger.info(f"Discovered: {url}")
                endpoint_details = self.analyze_endpoint_details(url)
                if endpoint_details:
                    self.discovered_endpoints[url] = endpoint_details
            
            # Start Active Scan
            ascan_id = self.zap.ascan.scan(self.target_url)
            
            # Monitor active scan progress
            while int(self.zap.ascan.status(ascan_id)) < 100:
                progress = self.zap.ascan.status(ascan_id)
                self.logger.info(f"Active scan progress: {progress}%")
                time.sleep(2)
            
            # Get alerts (potential vulnerabilities)
            alerts = self.zap.core.alerts()
            for alert in alerts:
                self.attack_surfaces.append({
                    'url': alert.get('url'),
                    'param': alert.get('param'),
                    'attack': alert.get('attack'),
                    'evidence': alert.get('evidence'),
                    'risk': alert.get('risk'),
                    'confidence': alert.get('confidence'),
                    'description': alert.get('description'),
                    'solution': alert.get('solution')
                })
            
            # Save detailed results
            # self.save_results("endpoints.json", {
            #     'endpoints': self.discovered_endpoints,
            #     'attack_surfaces': self.attack_surfaces
            # })
            
            self.logger.info(f"{Fore.GREEN}Endpoint discovery completed. Found {len(self.discovered_endpoints)} endpoints and {len(self.attack_surfaces)} potential vulnerabilities{Style.RESET_ALL}")
            
            # Print detailed endpoint information
            self.logger.info("\nDetailed Endpoint Information:")
            for url, details in self.discovered_endpoints.items():
                self.logger.info(f"\nEndpoint: {url}")
                if details['forms']:
                    self.logger.info("Forms found:")
                    for form in details['forms']:
                        self.logger.info(f"  Form Action: {form['action']}")
                        self.logger.info(f"  Method: {form['method']}")
                        self.logger.info("  Inputs:")
                        for input_field in form['inputs']:
                            self.logger.info(f"    - Type: {input_field['type']}, Name: {input_field['name']}, Required: {input_field['required']}")
                
                if details['inputs']:
                    self.logger.info("Standalone inputs found:")
                    for input_field in details['inputs']:
                        self.logger.info(f"  - Type: {input_field['type']}, Name: {input_field['name']}, Required: {input_field['required']}")
            
        except Exception as e:
            self.logger.error(f"{Fore.RED}Error during endpoint discovery: {str(e)}{Style.RESET_ALL}")

    def enumerate_subdomains(self):
        """Enumerate subdomains using DNS queries and web scraping."""
        try:
            self.logger.info(f"{Fore.BLUE}Starting subdomain enumeration{Style.RESET_ALL}")
            
            parsed_url = urlparse(self.target_url)
            domain = parsed_url.netloc
            
            # Basic subdomain enumeration using common prefixes
            common_prefixes = ['www', 'admin', 'api', 'dev', 'test', 'staging']
            
            for prefix in common_prefixes:
                subdomain = f"{prefix}.{domain}"
                try:
                    response = requests.get(f"https://{subdomain}", timeout=5)
                    if response.status_code < 400:
                        self.subdomains.add(subdomain)
                        self.logger.info(f"Found subdomain: {subdomain}")
                except:
                    continue
            
            # Save results
            self.save_results("subdomains.json", list(self.subdomains))
            
            self.logger.info(f"{Fore.GREEN}Subdomain enumeration completed. Found {len(self.subdomains)} subdomains{Style.RESET_ALL}")
            
        except Exception as e:
            self.logger.error(f"{Fore.RED}Error during subdomain enumeration: {str(e)}{Style.RESET_ALL}")

    def analyze_structure(self):
        """Analyze the structure of the web application."""
        try:
            self.logger.info(f"{Fore.BLUE}Starting structure analysis{Style.RESET_ALL}")
            
            for url, details in self.discovered_endpoints.items():
                self.forms.extend(details['forms'])
            
            # Save results
            self.save_results("structure.json", {
                'forms': self.forms
            })
            
            self.logger.info(f"{Fore.GREEN}Structure analysis completed. Found {len(self.forms)} forms{Style.RESET_ALL}")
            
        except Exception as e:
            self.logger.error(f"{Fore.RED}Error during structure analysis: {str(e)}{Style.RESET_ALL}")

    def save_results(self, filename, data):
        """Save scan results to a JSON file."""
        try:
            with open(f"{self.output_dir}/{filename}", 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            self.logger.error(f"Error saving results to {filename}: {str(e)}")

    def run_scan(self):
        """Run the complete scan process."""
        self.logger.info(f"{Fore.BLUE}Starting security scan for {self.target_url}{Style.RESET_ALL}")
        
        if not self.validate_url():
            return
        
        self.discover_endpoints()
        self.enumerate_subdomains()
        self.analyze_structure()
        
        self.logger.info(f"{Fore.GREEN}Scan completed successfully{Style.RESET_ALL}")

def main():
    # Example usage
    target_url = "https://target.com"  
    scanner = SecurityScanner(target_url)
    scanner.run_scan()

if __name__ == "__main__":
    main()
