import os
from supabase import create_client
import feedparser
from twilio.rest import Client
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Conexão Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Conexão Twilio
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# Função pra pegar usuários ativos
def get_active_users():
    response = supabase.table("users").select("*").eq("status_pagamento", "active").execute()
    return response.data

# Função pra pegar preferências de categorias de cada usuário
def get_user_categories(user_id):
    response = supabase.table("users_preferred_categories").select("news_category").eq("user_id", user_id).execute()
    return [cat["news_category"] for cat in response.data]

# Função pra buscar notícias recentes por categoria
def get_news_for_categories(categories):
    news_items = []
    for cat_id in categories:
        response = supabase.table("news").select("*").eq("category", cat_id).execute()
        news_items.extend(response.data)
    return news_items

# Função para enviar mensagem via WhatsApp
def send_whatsapp(to, message):
    twilio_client.messages.create(
        from_=TWILIO_WHATSAPP_FROM,
        body=message,
        to=f"whatsapp:{to}"
    )
 
# Função principal de envio diário
def send_daily_news():
    users = get_active_users()
    for user in users:
        categories = get_user_categories(user["id"])
        news_items = get_news_for_categories(categories)
        for news in news_items:
            msg = f"*{news['titulo']}*\n{news['resumo']}\nLeia mais: {news['link']}"
            send_whatsapp(user["whatsapp"], msg)

            # Registrar envio no log
            supabase.table("logs_de_envio").insert({
                "id_usuario": user["id"],
                "id_noticia": news["id"],
                "data_envio": datetime.utcnow(),
                "status_envio": "enviado"
            }).execute()

if __name__ == "__main__":
    send_daily_news()
 