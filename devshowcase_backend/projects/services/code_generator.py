import json


class CodeGenerator:
    """Generate code samples for API endpoints in multiple languages."""
    
    @staticmethod
    def generate_all_samples(endpoint):
        """Generate code samples for all supported languages."""
        return {
            'javascript': CodeGenerator.generate_javascript(endpoint),
            'python': CodeGenerator.generate_python(endpoint),
            'curl': CodeGenerator.generate_curl(endpoint),
            'php': CodeGenerator.generate_php(endpoint),
            'java': CodeGenerator.generate_java(endpoint),
        }
    
    @staticmethod
    def generate_javascript(endpoint):
        """Generate JavaScript fetch code."""
        method = endpoint.method
        url = endpoint.url
        body = endpoint.sample_body if endpoint.sample_body else {}
        
        # Build headers
        headers = {'Content-Type': 'application/json'}
        if endpoint.auth_required:
            if endpoint.auth_type == 'Bearer':
                headers['Authorization'] = 'Bearer YOUR_TOKEN_HERE'
            elif endpoint.auth_type == 'API Key':
                headers['X-API-Key'] = 'YOUR_API_KEY_HERE'
        
        code = f"// {endpoint.name}\n"
        code += f"const url = '{url}';\n\n"
        
        if method == 'GET':
            code += "const options = {\n"
            code += f"  method: '{method}',\n"
            code += f"  headers: {json.dumps(headers, indent=4).replace('{', '{\n    ').replace('}', '\n  }')}\n"
            code += "};\n\n"
        else:
            code += f"const data = {json.dumps(body, indent=2)};\n\n"
            code += "const options = {\n"
            code += f"  method: '{method}',\n"
            code += f"  headers: {json.dumps(headers, indent=4).replace('{', '{\n    ').replace('}', '\n  }')},\n"
            code += "  body: JSON.stringify(data)\n"
            code += "};\n\n"
        
        code += "fetch(url, options)\n"
        code += "  .then(response => response.json())\n"
        code += "  .then(data => console.log(data))\n"
        code += "  .catch(error => console.error('Error:', error));"
        
        return code
    
    @staticmethod
    def generate_python(endpoint):
        """Generate Python requests code."""
        method = endpoint.method.lower()
        url = endpoint.url
        body = endpoint.sample_body if endpoint.sample_body else {}
        
        code = f"# {endpoint.name}\n"
        code += "import requests\n"
        code += "import json\n\n"
        code += f"url = '{url}'\n"
        
        # Build headers
        headers = {'Content-Type': 'application/json'}
        if endpoint.auth_required:
            if endpoint.auth_type == 'Bearer':
                headers['Authorization'] = 'Bearer YOUR_TOKEN_HERE'
            elif endpoint.auth_type == 'API Key':
                headers['X-API-Key'] = 'YOUR_API_KEY_HERE'
        
        code += f"headers = {json.dumps(headers, indent=4)}\n"
        
        if method == 'get':
            code += f"\nresponse = requests.{method}(url, headers=headers)\n"
        else:
            code += f"data = {json.dumps(body, indent=4)}\n"
            code += f"\nresponse = requests.{method}(url, headers=headers, json=data)\n"
        
        code += "\nif response.status_code == 200:\n"
        code += "    print(response.json())\n"
        code += "else:\n"
        code += "    print(f'Error: {response.status_code}')"
        
        return code
    
    @staticmethod
    def generate_curl(endpoint):
        """Generate cURL command."""
        method = endpoint.method
        url = endpoint.url
        body = endpoint.sample_body if endpoint.sample_body else {}
        
        code = f"# {endpoint.name}\n"
        code += f"curl -X {method} '{url}' \\\n"
        code += "  -H 'Content-Type: application/json' \\\n"
        
        if endpoint.auth_required:
            if endpoint.auth_type == 'Bearer':
                code += "  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \\\n"
            elif endpoint.auth_type == 'API Key':
                code += "  -H 'X-API-Key: YOUR_API_KEY_HERE' \\\n"
        
        if method != 'GET' and body:
            code += f"  -d '{json.dumps(body)}'"
        else:
            code = code.rstrip(' \\\n')
        
        return code
    
    @staticmethod
    def generate_php(endpoint):
        """Generate PHP code."""
        method = endpoint.method
        url = endpoint.url
        body = endpoint.sample_body if endpoint.sample_body else {}
        
        code = f"<?php\n// {endpoint.name}\n\n"
        code += f"$url = '{url}';\n"
        
        # Build headers
        headers = ['Content-Type: application/json']
        if endpoint.auth_required:
            if endpoint.auth_type == 'Bearer':
                headers.append('Authorization: Bearer YOUR_TOKEN_HERE')
            elif endpoint.auth_type == 'API Key':
                headers.append('X-API-Key: YOUR_API_KEY_HERE')
        
        if method != 'GET' and body:
            code += f"$data = json_encode({json.dumps(body)});\n\n"
        
        code += "$ch = curl_init($url);\n"
        code += "curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);\n"
        code += f"curl_setopt($ch, CURLOPT_CUSTOMREQUEST, '{method}');\n"
        code += f"curl_setopt($ch, CURLOPT_HTTPHEADER, {json.dumps(headers)});\n"
        
        if method != 'GET' and body:
            code += "curl_setopt($ch, CURLOPT_POSTFIELDS, $data);\n"
        
        code += "\n$response = curl_exec($ch);\n"
        code += "$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);\n"
        code += "curl_close($ch);\n\n"
        code += "if ($httpCode == 200) {\n"
        code += "    $result = json_decode($response, true);\n"
        code += "    print_r($result);\n"
        code += "} else {\n"
        code += "    echo 'Error: ' . $httpCode;\n"
        code += "}\n?>"
        
        return code
    
    @staticmethod
    def generate_java(endpoint):
        """Generate Java code."""
        method = endpoint.method
        url = endpoint.url
        body = endpoint.sample_body if endpoint.sample_body else {}
        
        code = f"// {endpoint.name}\n"
        code += "import java.net.http.*;\n"
        code += "import java.net.URI;\n"
        code += "import java.io.IOException;\n\n"
        code += "public class ApiClient {\n"
        code += "    public static void main(String[] args) throws IOException, InterruptedException {\n"
        code += f"        String url = \"{url}\";\n\n"
        
        code += "        HttpClient client = HttpClient.newHttpClient();\n"
        code += "        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()\n"
        code += "            .uri(URI.create(url))\n"
        code += "            .header(\"Content-Type\", \"application/json\")\n"
        
        if endpoint.auth_required:
            if endpoint.auth_type == 'Bearer':
                code += "            .header(\"Authorization\", \"Bearer YOUR_TOKEN_HERE\")\n"
            elif endpoint.auth_type == 'API Key':
                code += "            .header(\"X-API-Key\", \"YOUR_API_KEY_HERE\")\n"
        
        if method == 'GET':
            code += "            .GET();\n\n"
        else:
            json_body = json.dumps(body).replace('"', '\\"')
            code += f"            .{method}(HttpRequest.BodyPublishers.ofString(\"{json_body}\"));\n\n"
        
        code += "        HttpRequest request = requestBuilder.build();\n"
        code += "        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());\n\n"
        code += "        System.out.println(\"Status: \" + response.statusCode());\n"
        code += "        System.out.println(\"Response: \" + response.body());\n"
        code += "    }\n"
        code += "}"
        
        return code
