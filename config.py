import os
from dotenv import load_dotenv

load_dotenv()

# Configuração da Base de Dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'firma'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# Configurações da Aplicação
APP_TITLE = "Sistema de Gestão - Ferragens e Serralharia"
APP_ICON = "🔧"