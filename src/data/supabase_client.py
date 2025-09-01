# src/data/supabase_client.py

import os
import streamlit as st
from supabase import create_client, Client
from typing import Optional

# --- Singleton instance --- 
_supabase_client_instance: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Initializes and returns a singleton Supabase client instance
    using credentials from Streamlit's secrets management.
    """
    global _supabase_client_instance
    if _supabase_client_instance is None:
        # Check if Supabase credentials are in st.secrets
        if "supabase" not in st.secrets or "url" not in st.secrets.supabase or "key" not in st.secrets.supabase:
            raise ValueError("Supabase credentials not found in Streamlit Secrets. Please add a [supabase] section with 'url' and 'key' to your secrets.")

        SUPABASE_URL = st.secrets.supabase.url
        SUPABASE_KEY = st.secrets.supabase.key

        print("Initializing Supabase client from st.secrets...")
        _supabase_client_instance = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase client initialized.")

    return _supabase_client_instance