import requests
import time
import json
import logging
import os
import sys
import dns.resolver
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init()

class SimpleScanner:
    def __init__(self, target_url, output_dir="scan_results"):
        self.target_url = target_url
        self.output_dir = output_dir
        self.discovered_endpoints = set()
        self.subdomains = set()
        self.forms = []
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{output_dir}/scan.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def validate_url(self):
        """Validate if the URL is accessible and properly formatted."""
        try:
            parsed = urlparse(self.target_url)
            if parsed.scheme not in ["http", "https"]:
                raise ValueError("URL must start with http:// or https://")
            
            self.logger.info(f"{Fore.BLUE}Validating URL: {self.target_url}{Style.RESET_ALL}")
            response = requests.get(
                self.target_url, 
                timeout=10,
                headers={'User-Agent': 'SimpleScanner/1.0'},
                verify=False
            )
            
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

    def crawl_site(self):
        """Simple crawler to discover endpoints."""
        self.logger.info(f"{Fore.BLUE}Starting endpoint discovery{Style.RESET_ALL}")
        
        # Add the base URL to start
        to_visit = {self.target_url}
        visited = set()
        
        while to_visit:
            current_url = to_visit.pop()
            if current_url in visited:
                continue
                
            visited.add(current_url)
            self.discovered_endpoints.add(current_url)
            self.logger.info(f"Crawling: {current_url}")
            
            try:
                response = requests.get(
                    current_url, 
                    timeout=5,
                    headers={'User-Agent': 'SimpleScanner/1.0'},
                    verify=False
                )
                
                # Only process HTML responses
                if 'text/html' in response.headers.get('Content-Type', ''):
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all links
                    for a_tag in soup.find_all('a', href=True):
                        href = a_tag['href']
                        
                        # Handle relative URLs
                        if not href.startswith(('http://', 'https://')):
                            href = urljoin(current_url, href)
                        
                        # Only follow links to the same domain
                        if urlparse(href).netloc == urlparse(self.target_url).netloc:
                            to_visit.add(href)
            
            except Exception as e:
                self.logger.warning(f"Error crawling {current_url}: {str(e)}")
        
        # Save results
        self.save_results("endpoints.json", list(self.discovered_endpoints))
        self.logger.info(f"{Fore.GREEN}Endpoint discovery completed. Found {len(self.discovered_endpoints)} endpoints{Style.RESET_ALL}")

    def analyze_endpoints_with_methods(self):
        """Analyze endpoints to determine HTTP methods and form parameters"""
        self.logger.info(f"{Fore.BLUE}Analyzing endpoints for HTTP methods and parameters{Style.RESET_ALL}")
        
        endpoints_data = []
        
        # Process all discovered endpoints
        for url in self.discovered_endpoints:
            try:
                # First check if the endpoint is accessible
                response = requests.get(
                    url,
                    timeout=5,
                    headers={'User-Agent': 'SimpleScanner/1.0'},
                    verify=False
                )
                
                # Extract path from URL
                parsed_url = urlparse(url)
                path = parsed_url.path if parsed_url.path else "/"
                
                # Initialize endpoint data
                endpoint = {
                    "path": path,
                    "url": url,
                    "methods": ["GET"],  # Default method
                    "form_fields": []
                }
                
                # Process HTML to find forms
                if 'text/html' in response.headers.get('Content-Type', ''):
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find forms on the page
                    for form in soup.find_all('form'):
                        form_method = form.get('method', 'get').upper()
                        form_action = form.get('action', '')
                        
                        # Handle relative URLs in form action
                        if form_action and not form_action.startswith(('http://', 'https://')):
                            form_action = urljoin(url, form_action)
                        elif not form_action:
                            form_action = url
                            
                        # Extract path from form action
                        form_path = urlparse(form_action).path if urlparse(form_action).path else path
                        
                        # Create new endpoint for form target if it differs from current URL
                        if form_path != path:
                            form_endpoint = {
                                "path": form_path,
                                "url": form_action,
                                "methods": [form_method],
                                "form_fields": []
                            }
                            
                            # Add form fields
                            for input_field in form.find_all(['input', 'textarea', 'select']):
                                if input_field.name == 'input':
                                    field_type = input_field.get('type', 'text')
                                    field_name = input_field.get('name', '')
                                elif input_field.name == 'textarea':
                                    field_type = 'textarea'
                                    field_name = input_field.get('name', '')
                                else:  # select
                                    field_type = 'select'
                                    field_name = input_field.get('name', '')
                                
                                if field_name:  # Only add fields with names
                                    form_endpoint["form_fields"].append({
                                        "name": field_name,
                                        "type": field_type,
                                        "required": input_field.get('required') is not None
                                    })
                            
                            endpoints_data.append(form_endpoint)
                        else:
                            # Add method to existing endpoint if it's the current page
                            if form_method not in endpoint["methods"]:
                                endpoint["methods"].append(form_method)
                            
                            # Add form fields to current endpoint
                            for input_field in form.find_all(['input', 'textarea', 'select']):
                                if input_field.name == 'input':
                                    field_type = input_field.get('type', 'text')
                                    field_name = input_field.get('name', '')
                                elif input_field.name == 'textarea':
                                    field_type = 'textarea'
                                    field_name = input_field.get('name', '')
                                else:  # select
                                    field_type = 'select'
                                    field_name = input_field.get('name', '')
                                
                                if field_name:  # Only add fields with names
                                    endpoint["form_fields"].append({
                                        "name": field_name,
                                        "type": field_type,
                                        "required": input_field.get('required') is not None
                                    })
                
                # Add the current endpoint if it has interesting data (forms or non-GET methods)
                if endpoint["form_fields"] or len(endpoint["methods"]) > 1:
                    endpoints_data.append(endpoint)
                
            except Exception as e:
                self.logger.warning(f"Error analyzing endpoint {url}: {str(e)}")
        
        # Save detailed endpoints data
        self.save_results("detailed_endpoints.json", endpoints_data)
        self.logger.info(f"{Fore.GREEN}Endpoint analysis completed. Found {len(endpoints_data)} endpoints with forms/methods{Style.RESET_ALL}")
        
        return endpoints_data

    def save_results(self, filename, data):
        """Save scan results to a JSON file."""
        try:
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            self.logger.info(f"Results saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving results to {filename}: {str(e)}")
    
    def run_scan(self):
        """Run the complete scan process."""
        self.logger.info(f"{Fore.BLUE}Starting security scan for {self.target_url}{Style.RESET_ALL}")
        
        if not self.validate_url():
            return
        
        self.crawl_site()
        # self.enumerate_subdomains()  # Uncomment if you have this method implemented
        # self.analyze_structure()  # Uncomment if you have this method implemented
        
        # Add the new method call
        detailed_endpoints = self.analyze_endpoints_with_methods()
        
        self.logger.info(f"{Fore.GREEN}Scan completed successfully{Style.RESET_ALL}")
        return detailed_endpoints

def run_security_scan(target_url):
    """Function to run a security scan on the provided URL."""
    scanner = SimpleScanner(target_url)
    detailed_endpoints = scanner.run_scan()
    
    # Format endpoint data in the requested format
    formatted_endpoints = []
    for endpoint in detailed_endpoints or []:
        for method in endpoint["methods"]:
            formatted_endpoint = {
                "path": endpoint["path"],
                "method": method,
                "form_fields": endpoint["form_fields"]
            }
            formatted_endpoints.append(formatted_endpoint)
    
    # Save the formatted endpoints
    output_dir = scanner.output_dir
    scanner.save_results("formatted_endpoints.json", formatted_endpoints)
    
    return {
        "message": f"Scan completed for {target_url}. Results saved to '{output_dir}' directory.",
        "endpoints": formatted_endpoints
    }

if __name__ == "__main__":
    target = input("Enter the target URL to scan (e.g., https://example.com): ")
    result = run_security_scan(target)
    print(f"Scan completed with {len(result['endpoints'])} endpoints found.")
    print(f"Results saved to {result['message'].split('Results saved to ')[1]}")
    
    # Display the first 3 endpoints as a preview
    preview = result["endpoints"][:3]
    if preview:
        print("\nPreview of discovered endpoints:")
        print(json.dumps(preview, indent=2))