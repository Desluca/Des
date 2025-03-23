import telebot
import os
import tempfile
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
                # Ottieni risposta testuale dall'AI
                text_response = self.agent.ask(message.text)
                
                # Invia risposta testuale
                text_msg = self.bot.reply_to(message, text_response)
                
                # Genera e invia risposta audio
                self.send_voice_response(message.chat.id, text_response)
                
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
                
                # Trascrivi l'audio usando Whisper di OpenAI
                with open(temp_ogg_path, "rb") as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                
                transcribed_text = transcript.text
                
                # Invia la trascrizione all'agente e ottieni la risposta testuale
                text_response = self.agent.ask(transcribed_text)
                self.bot.reply_to(message, text_response)
                
                # Genera e invia risposta audio
                self.send_voice_response(message.chat.id, text_response)
                
                # Pulizia dei file temporanei
                os.remove(temp_ogg_path)
                
            except Exception as e:
                self.bot.reply_to(message, f"Si è verificato un errore nell'elaborazione del messaggio vocale: {str(e)}")
    
    def send_voice_response(self, chat_id, text):
        try:

            refined_prompt = (
                "Riassumi la seguente risposta in modo breve e chiaro. "
                "Aggiungi un tocco di sarcasmo ogni tanto, ma senza esagerare.\n\n"
                f"Risposta: {text}"
            )

            # Genera una risposta più breve e sarcastica (a volte)
            chat_response = self.openai_client.chat.completions.create(
               model="gpt-4-turbo",  # Usa un modello ottimizzato
               messages=[{"role": "user", "content": refined_prompt}],
               max_tokens=100,  # Limita la lunghezza della risposta
               temperature=0.7   # Aggiunge un po' di variabilità e creatività
           )
            # Crea un file temporaneo per l'audio
            temp_audio_path = tempfile.mktemp(suffix='.mp3')
            
            # Genera audio con OpenAI TTS
            audio_response = self.openai_client.audio.speech.create(
                model="tts-1",     # Modello base, usa "tts-1-hd" per qualità superiore
                voice="Coral",     # Opzioni: alloy, echo, fable, onyx, nova, shimmer
                input=text
            )
            
            # Salva l'audio su un file temporaneo
            audio_response.stream_to_file(temp_audio_path)
            
            # Invia il file audio a Telegram
            with open(temp_audio_path, 'rb') as audio_file:
                self.bot.send_voice(chat_id, audio_file)
            
            # Pulisci il file temporaneo
            os.remove(temp_audio_path)
            
        except Exception as e:
            self.bot.send_message(chat_id, f"Errore nella generazione audio: {str(e)}")
    
    def run(self):
        print("🤖 Bot in esecuzione con supporto per messaggi vocali e TTS...")
        self.bot.polling()