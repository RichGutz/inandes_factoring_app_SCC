# src/data/supabase_client.py

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional

# --- Singleton instance --- 
_supabase_client_instance: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Initializes and returns a singleton Supabase client instance.

    Loads credentials from the .env file in the project root.
    Raises an exception if credentials are not found.
    """
    global _supabase_client_instance
    if _supabase_client_instance is None:
        # Construct the path to the .env file in the project root
        # __file__ -> src/data/supabase_client.py
        # os.path.dirname(__file__) -> src/data
        # os.path.join(..., '..', '..') -> project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        dotenv_path = os.path.join(project_root, '.env')

        if not os.path.exists(dotenv_path):
            raise FileNotFoundError(f"Critical Error: .env file not found at {dotenv_path}. Please create it with SUPABASE_URL and SUPABASE_KEY.")

        load_dotenv(dotenv_path=dotenv_path)

        SUPABASE_URL = os.environ.get("SUPABASE_URL")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Error: SUPABASE_URL and SUPABASE_KEY must be defined in the .env file.")
        
        print("Initializing Supabase client...")
        _supabase_client_instance = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase client initialized.")

    return _supabase_client_instance
