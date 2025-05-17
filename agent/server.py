from flask import Flask, request, jsonify
from flask_cors import CORS
from orchestrator.agent import execute, run_security_scan
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

@app.route('/scan', methods=['POST'])
def scan():
    try:
        data = request.get_json()
        target_url = data.get('target_url')
        
        if not target_url:
            return jsonify({"error": "No target URL provided"}), 400
            
        # First run security scan
        scan_result = run_security_scan(target_url)
        
        # Then execute curl commands for each endpoint
        if scan_result.get('endpoints'):
            for endpoint in scan_result['endpoints']:
                if 'curl_command' in endpoint:
                    execute_result = execute(endpoint['curl_command'])
                    endpoint['execute_result'] = execute_result
        
        return jsonify(scan_result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/execute', methods=['POST'])
def execute_command():
    try:
        data = request.get_json()
        curl_command = data.get('curl_command')
        
        if not curl_command:
            return jsonify({"error": "No curl command provided"}), 400
            
        result = execute(curl_command)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) 