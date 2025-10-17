import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_users():
    """Pega todos os usuários ativos"""
    response = supabase.table("users").select("*").execute()
    return response.data

def get_unsent_news(user):
    """Pega notícias não enviadas pro usuário e que batem com as preferências"""
    user_id = user["id"]

    # Pegando categorias preferidas
    categories_resp = supabase.table("users_preferred_categories").select("news_category").eq("user_id", user_id).execute()
    categories = [c["news_category"] for c in categories_resp.data]

    # Pegando notícias que ainda não foram enviadas
    news_resp = supabase.table("news").select("*").in_("category", categories).execute()
    news_list = news_resp.data

    # Filtrar as notícias que já foram enviadas
    logs_resp = supabase.table("logs_de_envio").select("id_noticia").eq("id_usuario", user_id).execute()
    sent_ids = [l["id_noticia"] for l in logs_resp.data]

    unsent_news = [n for n in news_list if n["id"] not in sent_ids]

    return unsent_news

def log_news_sent(user_id, news_id, status="enviado"):
    """Registra no log que a notícia foi enviada"""
    supabase.table("logs_de_envio").insert({
        "id_usuario": user_id,
        "id_noticia": news_id,
        "data_envio": datetime.utcnow().isoformat(),
        "status_envio": status
    }).execute()

def send_news(user, news):
    """Simula envio de notícia (aqui depois integraremos WhatsApp)"""
    print(f"Enviando notícia '{news['titulo']}' para {user['first_name']} ({user['whatsapp']})")
    log_news_sent(user["id"], news["id"])

def main():
    users = get_users()
    for user in users:
        unsent_news = get_unsent_news(user)
        for news in unsent_news:
            send_news(user, news)

if __name__ == "__main__":
    main()
