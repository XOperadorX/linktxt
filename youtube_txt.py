import os
os.environ['PATH'] += r';C:\ffmpeg\bin'

from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import whisper
import re

def pegar_id(url):
    m = re.search(r"(?:v=|youtu\.be\/|shorts\/)([0-9A-Za-z_-]{11})", url)
    return m.group(1) if m else None

def baixar_audio(url):
    print("Baixando áudio do YouTube...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    # retorna o arquivo mp3
    for f in os.listdir('.'):
        if f.startswith('temp_audio') and f.endswith('.mp3'):
            return f
    return None

link = input("Cole o link do YouTube: ").strip()
video_id = pegar_id(link)

if not video_id:
    print("Link inválido!")
    exit()

texto_final = ""

# TENTATIVA 1: Legenda do YouTube (rápido e grátis)
try:
    print("Tentando pegar legenda do YouTube...")
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'pt-BR', 'en'])
    texto_final = " ".join([t['text'] for t in transcript])
    print("✅ Peguei pela legenda do YouTube!")
except Exception as e:
    print(f"Sem legenda pronta ({e}), vou transcrever com IA...")
    
    # TENTATIVA 2: IA Whisper (funciona em 100%)
    audio_file = baixar_audio(link)
    if audio_file:
        print("Transcrevendo com Whisper (pode demorar 1-2 min)...")
        model = whisper.load_model("medium") # small/medium/large, medium é bom pra PT-BR
        result = model.transcribe(audio_file, language="pt")
        texto_final = result["text"]
        os.remove(audio_file)
        if os.path.exists("temp_audio.mp3"):
            os.remove("temp_audio.mp3")

# Salva
if texto_final:
    with open("transcricao.txt", "w", encoding="utf-8") as f:
        f.write(texto_final)
    print("\n--- TRANSCRIÇÃO ---\n")
    print(texto_final[:1000])
    print(f"\n✅ Salvo em: {os.path.abspath('transcricao.txt')}")
else:
    print("❌ Não consegui transcrever.")