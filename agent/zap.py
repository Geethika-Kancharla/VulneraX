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
from zapv2 import ZAPv2
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init()

class SecurityScanner:
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
        
        # Initialize ZAP API
        try:
            self.zap = ZAPv2(
                proxies={'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'},
                apikey='changeme'
            )
            self.zap.core.version
            self.logger.info(f"{Fore.GREEN}Successfully connected to OWASP ZAP{Style.RESET_ALL}")
        except Exception as e:
            self.logger.error(f"{Fore.RED}Failed to connect to OWASP ZAP. Make sure it's running on localhost:8080{Style.RESET_ALL}")
            self.logger.error(f"Error: {str(e)}")
            sys.exit(1)

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
                headers={'User-Agent': 'SecurityScanner/1.0'},
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

    def discover_endpoints(self):
        """Discover endpoints using ZAP Spider."""
        try:
            self.logger.info(f"{Fore.BLUE}Starting endpoint discovery{Style.RESET_ALL}")
            
            # Configure ZAP context
            context_name = 'scan_context'
            context_id = self.zap.context.new_context(context_name)
            self.zap.context.include_in_context(context_name, self.target_url + ".*")
            
            # Start spider scan
            scan_id = self.zap.spider.scan(self.target_url)
            
            # Monitor progress
            while int(self.zap.spider.status(scan_id)) < 100:
                progress = self.zap.spider.status(scan_id)
                self.logger.info(f"Spider progress: {progress}%")
                time.sleep(2)
            
            # Get results
            urls = self.zap.spider.results(scan_id)
            for url in urls:
                self.discovered_endpoints.add(url)
                self.logger.info(f"Discovered: {url}")
            
            # Save results
            self.save_results("endpoints.json", list(self.discovered_endpoints))
            
            self.logger.info(f"{Fore.GREEN}Endpoint discovery completed. Found {len(self.discovered_endpoints)} endpoints{Style.RESET_ALL}")
            
        except Exception as e:
            self.logger.error(f"{Fore.RED}Error during endpoint discovery: {str(e)}{Style.RESET_ALL}")
            self._fallback_crawl()

    def check_subdomain(self, subdomain):
        """Check if a subdomain exists and is accessible."""
        try:
            # First try DNS resolution
            dns.resolver.resolve(subdomain, 'A')
            
            # Then try HTTP(S) connection
            for protocol in ['https://', 'http://']:
                try:
                    response = requests.get(
                        f"{protocol}{subdomain}",
                        timeout=5,
                        verify=False,
                        allow_redirects=True
                    )
                    if response.status_code < 400:
                        self.subdomains.add(subdomain)
                        self.logger.info(f"Found subdomain: {subdomain}")
                        return True
                except requests.RequestException:
                    continue
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            pass
        return False

    def enumerate_subdomains(self):
        """Enhanced subdomain enumeration using multiple techniques."""
        try:
            self.logger.info(f"{Fore.BLUE}Starting subdomain enumeration{Style.RESET_ALL}")
            
            parsed_url = urlparse(self.target_url)
            domain = parsed_url.netloc.split(':')[0]
            
            # Common subdomain prefixes
            common_prefixes = [
                'www', 'admin', 'api', 'dev', 'test', 'staging', 'mail',
                'remote', 'blog', 'webmail', 'portal', 'ns1', 'ns2',
                'smtp', 'secure', 'vpn', 'mx', 'ftp', 'intranet',
                'cdn', 'images', 'img', 'auth', 'cp', 'cloud',
                'api', 'staging', 'dev', 'uat', 'qa', 'internal',
                'services', 'download', 'downloads', 'apps', 'app',
                'mobile', 'm', 'cms', 'assets', 'media', 'static',
                'support', 'help', 'helpdesk', 'web', 'db', 'database',
                'files', 'host', 'hosting', 'server', 'client', 'portal'
            ]
            
            # Use ThreadPoolExecutor for parallel subdomain checking
            with ThreadPoolExecutor(max_workers=10) as executor:
                subdomains_to_check = [f"{prefix}.{domain}" for prefix in common_prefixes]
                executor.map(self.check_subdomain, subdomains_to_check)
            
            # Try to get additional subdomains from SSL certificate
            try:
                import ssl
                import socket
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                with socket.create_connection((domain, 443)) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        cert = ssock.getpeercert(binary_form=True)
                        from cryptography import x509
                        from cryptography.hazmat.backends import default_backend
                        cert = x509.load_der_x509_certificate(cert, default_backend())
                        
                        # Extract subdomains from SAN
                        for extension in cert.extensions:
                            if extension.oid.dotted_string == "2.5.29.17":  # Subject Alternative Name
                                for name in extension.value:
                                    if isinstance(name, x509.DNSName):
                                        self.check_subdomain(name.value)
            except Exception as e:
                self.logger.debug(f"Error getting SSL certificate: {str(e)}")
            
            # Save results
            self.save_results("subdomains.json", list(self.subdomains))
            
            self.logger.info(f"{Fore.GREEN}Subdomain enumeration completed. Found {len(self.subdomains)} subdomains{Style.RESET_ALL}")
            
        except Exception as e:
            self.logger.error(f"{Fore.RED}Error during subdomain enumeration: {str(e)}{Style.RESET_ALL}")

    def analyze_structure(self):
        """Analyze the structure of the web application."""
        try:
            self.logger.info(f"{Fore.BLUE}Starting structure analysis{Style.RESET_ALL}")
            
            for endpoint in self.discovered_endpoints:
                try:
                    response = requests.get(endpoint, timeout=5, verify=False)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find forms
                    forms = soup.find_all('form')
                    for form in forms:
                        form_data = {
                            'url': endpoint,
                            'action': form.get('action', ''),
                            'method': form.get('method', 'get'),
                            'inputs': [
                                {
                                    'name': input.get('name', ''),
                                    'type': input.get('type', 'text'),
                                    'required': input.get('required') is not None,
                                    'id': input.get('id', '')
                                }
                                for input in form.find_all('input')
                            ]
                        }
                        self.forms.append(form_data)
                        
                except Exception as e:
                    self.logger.warning(f"Error analyzing {endpoint}: {str(e)}")
            
            # Save results
            self.save_results("structure.json", {
                'forms': self.forms,
                'total_endpoints': len(self.discovered_endpoints),
                'total_forms': len(self.forms)
            })
            
            self.logger.info(f"{Fore.GREEN}Structure analysis completed. Found {len(self.forms)} forms{Style.RESET_ALL}")
            
        except Exception as e:
            self.logger.error(f"{Fore.RED}Error during structure analysis: {str(e)}{Style.RESET_ALL}")

    def save_results(self, filename, data):
        """Save scan results to a JSON file."""
        try:
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w') as f:
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
    target_url = "https://dsce.edu.in"  # Replace with your target
    scanner = SecurityScanner(target_url)
    scanner.run_scan()

if __name__ == "__main__":
    main()