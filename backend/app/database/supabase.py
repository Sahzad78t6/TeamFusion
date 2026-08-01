import os
from supabase import create_client, Client
from app.config.config import settings

# Initialize Supabase client
supabase_url = settings.SUPABASE_URL
supabase_key = settings.SUPABASE_KEY

supabase: Client = create_client(supabase_url, supabase_key)


def get_supabase_client() -> Client:
    """
    Get configured Supabase client instance.
    """
    return supabase
