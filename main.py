import os
import json
import time
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from dotenv import load_dotenv

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scheduler.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WppScheduler")

STATE_FILE = "state.json"

# Variáveis globais carregadas do .env
EVOLUTION_API_URL = ""
EVOLUTION_API_KEY = ""
EVOLUTION_INSTANCE = ""
RECIPIENT_NUMBER = ""
MESSAGE_TEXT = ""

def get_last_sent_date():
    """Retorna a última data de envio registrada no arquivo state.json."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                return state.get("last_sent_date")
        except Exception as e:
            logger.error(f"Erro ao ler arquivo de estado (state.json): {e}")
    return None

def update_last_sent_date(date_str):
    """Atualiza a última data de envio registrada no arquivo state.json."""
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"last_sent_date": date_str}, f, indent=4)
        logger.info(f"Estado atualizado com a data de envio: {date_str}")
    except Exception as e:
        logger.error(f"Erro ao atualizar arquivo de estado: {e}")

def send_message():
    """Envia a mensagem de texto configurada através da Evolution API."""
    url = f"{EVOLUTION_API_URL.rstrip('/')}/message/sendText/{EVOLUTION_INSTANCE}"
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }
    
    # Remove qualquer caractere que não seja número (ex: +)
    number = "".join(filter(str.isdigit, RECIPIENT_NUMBER))
    
    payload = {
        "number": number,
        "text": MESSAGE_TEXT,
        "delay": 1200
    }
    
    logger.info(f"Tentando enviar mensagem para {number}...")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code in (200, 201):
            logger.info(f"Mensagem enviada com sucesso! Resposta: {response.text}")
            return True
        else:
            logger.error(f"Falha ao enviar mensagem. Status Code: {response.status_code}, Resposta: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de conexão/rede com a Evolution API: {e}")
        return False

def main():
    # Carrega as variáveis do arquivo .env
    load_dotenv()
    
    global EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE, RECIPIENT_NUMBER, MESSAGE_TEXT
    
    EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
    EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
    EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE")
    RECIPIENT_NUMBER = os.getenv("RECIPIENT_NUMBER")
    MESSAGE_TEXT = os.getenv("MESSAGE_TEXT", "Mensagem diária automática.")
    scheduled_time_str = os.getenv("SCHEDULED_TIME", "10:00")
    timezone_str = os.getenv("TIMEZONE", "America/Sao_Paulo")
    
    # Validação dos parâmetros essenciais
    if not all([EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE, RECIPIENT_NUMBER]):
        logger.critical("Erro: Por favor, preencha as credenciais e configurações obrigatórias no arquivo .env!")
        return
        
    # Configuração de Timezone
    try:
        tz = ZoneInfo(timezone_str)
        logger.info(f"Fuso horário configurado: {timezone_str}")
    except Exception as e:
        logger.error(f"Fuso horário '{timezone_str}' inválido. Utilizando 'America/Sao_Paulo' como padrão. Erro: {e}")
        tz = ZoneInfo("America/Sao_Paulo")
        
    # Validação do formato do horário agendado
    try:
        scheduled_time = datetime.strptime(scheduled_time_str, "%H:%M").time()
        logger.info(f"Horário agendado para o envio diário: {scheduled_time_str}")
    except ValueError:
        logger.critical(f"Horário de agendamento '{scheduled_time_str}' inválido! Use o formato HH:MM (ex: 10:00).")
        return
        
    logger.info("Agendador de mensagens WhatsApp iniciado com sucesso. Aguardando horário programado...")
    
    while True:
        try:
            # Obter a data e hora atual no fuso horário programado
            now = datetime.now(tz)
            current_date_str = now.strftime("%Y-%m-%d")
            current_time = now.time()
            
            last_sent_date = get_last_sent_date()
            
            # Condição de Envio:
            # 1. Se a hora atual já passou ou é o horário agendado
            # 2. Se a última data enviada é diferente da data de hoje
            if current_time >= scheduled_time and last_sent_date != current_date_str:
                success = send_message()
                if success:
                    update_last_sent_date(current_date_str)
                else:
                    logger.warning("Falha no envio. Aguardando 5 minutos antes de tentar novamente hoje.")
                    time.sleep(300) # Aguarda 5 minutos para evitar spam/flooding de erros
                    continue
                    
        except Exception as e:
            logger.error(f"Erro inesperado no loop do agendador: {e}")
            
        # Verifica a hora a cada 15 segundos
        time.sleep(15)

if __name__ == "__main__":
    main()
