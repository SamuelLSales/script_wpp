import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

class MockEvolutionAPI(BaseHTTPRequestHandler):
    def do_POST(self):
        # Verifica se o endpoint é de envio de mensagem de texto
        # Endpoint esperado: /message/sendText/{instance}
        if "/message/sendText/" in self.path:
            content_length = int(self.headers['content-length'])
            post_data = self.rfile.read(content_length)
            
            # Cabeçalhos enviados
            api_key = self.headers.get('apikey', 'Não enviada')
            
            try:
                payload = json.loads(post_data.decode('utf-8'))
                number = payload.get('number')
                text = payload.get('text')
                
                print("\n" + "="*50)
                print("   [SIMULADOR EVOLUTION API] REQUISIÇÃO RECEBIDA   ")
                print("="*50)
                print(f"Instância na Rota:  {self.path.split('/')[-1]}")
                print(f"API Key (apikey):   {api_key}")
                print(f"Número de Destino:  {number}")
                print(f"Mensagem Enviada:   {text}")
                print("="*50 + "\n")
                
                # Resposta de Sucesso (Status 201)
                self.send_response(201)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                response = {
                    "status": "SUCCESS",
                    "message": "Mensagem enviada com sucesso (Simulado no Mock Server)"
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f"Erro ao processar JSON: {e}".encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Rota nao encontrada no simulador.")

def run(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, MockEvolutionAPI)
    print(f"Simulador da Evolution API rodando localmente em http://localhost:{port}")
    print("Pressione Ctrl+C para encerrar o simulador.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nSimulador encerrado.")
        sys.exit(0)

if __name__ == '__main__':
    run()
