import os
from LLM_Brain_local import AI_Agent
from telegram_bot import TelegramBot
from dotenv import load_dotenv

# Carica le variabili dal file .env
load_dotenv()

# Legge i token dalle variabili d'ambiente
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Verifica che i token siano stati caricati correttamente
if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("I token non sono stati trovati nel file .env")

# Inizializza l'agente AI
agent = AI_Agent(OPENAI_API_KEY)

# Inizializza il bot di Telegram con supporto audio
telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN, agent, OPENAI_API_KEY)

# Avvia il bot
if __name__ == "__main__":
    telegram_bot.run()