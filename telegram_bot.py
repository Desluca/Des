import telebot
import os
import tempfile
from pydub import AudioSegment
import speech_recognition as sr
from openai import OpenAI

class TelegramBot:
    def __init__(self, token, agent, openai_api_key):
        self.bot = telebot.TeleBot(token)
        self.agent = agent
        self.openai_client = OpenAI(api_key=openai_api_key)
        
        # Handler per i messaggi di testo
        @self.bot.message_handler(content_types=['text']) 
        def handle_text(message):
            try:
                response = self.agent.ask(message.text)
                self.bot.reply_to(message, response)
            except Exception as e:
                self.bot.reply_to(message, f"Si è verificato un errore: {str(e)}")
        
        # Handler per i messaggi vocali
        @self.bot.message_handler(content_types=['voice'])
        def handle_voice(message):
            try:
                
                # Scarica il file audio
                file_info = self.bot.get_file(message.voice.file_id)
                downloaded_file = self.bot.download_file(file_info.file_path)
                
                # Salva temporaneamente il file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
                    temp_file.write(downloaded_file)
                    temp_ogg_path = temp_file.name
                
                # Converti OGG in WAV per il riconoscimento vocale
                temp_wav_path = temp_ogg_path.replace('.ogg', '.wav')
                audio = AudioSegment.from_ogg(temp_ogg_path)
                audio.export(temp_wav_path, format="wav")
                
                # Trascrivi l'audio usando Whisper di OpenAI
                with open(temp_wav_path, "rb") as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                
                transcribed_text = transcript.text
                
                # Invia la trascrizione all'agente e ottieni la risposta
                response = self.agent.ask(transcribed_text)
                self.bot.reply_to(message, response)
                
                # Pulizia dei file temporanei
                os.remove(temp_ogg_path)
                os.remove(temp_wav_path)
                
            except Exception as e:
                self.bot.reply_to(message, f"Si è verificato un errore nell'elaborazione del messaggio vocale: {str(e)}")
    
    def run(self):
        print("🤖 Bot in esecuzione con supporto per messaggi vocali...")
        self.bot.polling()