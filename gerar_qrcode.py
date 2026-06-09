import os
import time
import requests
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    # Configurações do .env
    api_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
    api_key = os.getenv("EVOLUTION_API_KEY", "chave_teste_123")
    instance_name = os.getenv("EVOLUTION_INSTANCE", "instancia_teste")
    
    print("=" * 60)
    print("   GERADOR DE QR CODE - EVOLUTION API")
    print("=" * 60)
    print(f"API URL: {api_url}")
    print(f"Instância: {instance_name}")
    print(f"API Key: {api_key}")
    print("-" * 60)
    
    # 1. Tentar criar a instância
    create_url = f"{api_url.rstrip('/')}/instance/create"
    headers = {
        "Content-Type": "application/json",
        "apikey": api_key
    }
    payload = {
        "instanceName": instance_name,
        "token": api_key,
        "qrcode": True
    }
    
    print("1. Criando ou verificando instância...")
    try:
        response = requests.post(create_url, json=payload, headers=headers, timeout=15)
        if response.status_code in (200, 201):
            print("Instância criada com sucesso!")
        elif response.status_code == 400 or "already exists" in response.text:
            print("A instância já existe ou já está criada. Continuando...")
        else:
            print(f"Aviso ao criar instância (Código {response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar na Evolution API: {e}")
        print("Certifique-se de que a API está rodando e a URL está correta.")
        return

    # 2. Obter o QR Code para conexão
    connect_url = f"{api_url.rstrip('/')}/instance/connect/{instance_name}"
    print("\n2. Solicitando QR Code para conexão...")
    time.sleep(2)  # Aguarda a inicialização
    
    try:
        response = requests.get(connect_url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # O QR code pode vir em formato base64 no JSON
            qrcode_data = data.get("base64") or data.get("code")
            
            if qrcode_data:
                # Se for base64 completo (data:image/png;base64,...)
                if "base64," in qrcode_data:
                    qrcode_data = qrcode_data.split("base64,")[1]
                
                import base64
                img_data = base64.b64decode(qrcode_data)
                with open("qrcode.png", "wb") as f:
                    f.write(img_data)
                
                print("\n" + "=" * 60)
                print(" Sucesso! O arquivo 'qrcode.png' foi salvo na pasta do projeto.")
                print(" Abra a imagem e escaneie o QR Code usando seu WhatsApp (Aparelhos Conectados).")
                print("=" * 60)
            else:
                print("A API retornou sucesso, mas não enviou o QR Code em base64. Verifique o status da conexão.")
                print("Resposta da API:", data)
        else:
            print(f"Erro ao obter QR Code (Código {response.status_code}): {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Erro de rede ao conectar para obter o QR Code: {e}")

if __name__ == "__main__":
    main()
