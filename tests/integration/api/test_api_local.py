import pytest

#!/usr/bin/env python3
"""
Script de teste local para a API de Transparência
Testa se tudo está funcionando antes do deploy
"""

import asyncio
import os
from datetime import datetime

import httpx

# Cores para output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_status(message: str, status: str = "info"):
    """Print colorido de status"""
    if status == "success":
        print(f"{GREEN}✅ {message}{RESET}")
    elif status == "error":
        print(f"{RED}❌ {message}{RESET}")
    elif status == "warning":
        print(f"{YELLOW}⚠️  {message}{RESET}")
    else:
        print(f"{BLUE}ℹ️  {message}{RESET}")


@pytest.mark.asyncio
async def test_api_connection():
    """Testa conexão com a API"""
    print_status("Testando conexão com API do Portal da Transparência...", "info")

    api_key = os.getenv("TRANSPARENCY_API_KEY")

    if not api_key:
        print_status("TRANSPARENCY_API_KEY não configurada no ambiente", "error")
        print_status("Configure a variável de ambiente antes de continuar", "warning")
        return False

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"chave-api-dados": api_key, "Content-Type": "application/json"}

            # Teste simples - buscar contratos do ano atual
            params = {"ano": datetime.now().year, "pagina": 1, "tamanhoPagina": 1}

            response = await client.get(
                "https://api.portaldatransparencia.gov.br/api-de-dados/contratos",
                params=params,
                headers=headers,
            )

            if response.status_code == 200:
                print_status("Conexão com API bem-sucedida!", "success")
                data = response.json()
                print_status(f"Resposta recebida: {len(str(data))} caracteres", "info")
                return True
            elif response.status_code == 401:
                print_status("API Key inválida ou não autorizada", "error")
                return False
            else:
                print_status(f"Erro na API: Status {response.status_code}", "error")
                print(f"Resposta: {response.text}")
                return False

    except Exception as e:
        print_status(f"Erro de conexão: {str(e)}", "error")
        return False


def test_backend_dependencies():
    """Testa se as dependências do backend estão instaladas"""
    print_status("Verificando dependências do backend...", "info")

    try:
        import fastapi
        import uvicorn

        print_status("FastAPI backend dependencies available", "success")
        return True
    except ImportError:
        print_status("Backend dependencies não estão instaladas", "error")
        print_status("Execute: pip install fastapi uvicorn", "warning")
        return False


def test_dependencies():
    """Testa todas as dependências"""
    print_status("Verificando dependências...", "info")

    deps = {
        "httpx": "httpx",
        "pydantic": "pydantic",
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "dotenv": "python-dotenv",
    }

    all_ok = True

    for name, package in deps.items():
        try:
            __import__(name)
            print_status(f"{name} ✓", "success")
        except ImportError:
            print_status(f"{name} ✗ - instale com: pip install {package}", "error")
            all_ok = False

    return all_ok


def check_env_vars():
    """Verifica variáveis de ambiente"""
    print_status("Verificando variáveis de ambiente...", "info")

    vars_status = {
        "TRANSPARENCY_API_KEY": os.getenv("TRANSPARENCY_API_KEY"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
    }

    for var, value in vars_status.items():
        if value:
            print_status(f"{var}: Configurada ({len(value)} caracteres)", "success")
        else:
            if var == "TRANSPARENCY_API_KEY":
                print_status(f"{var}: NÃO configurada (obrigatória)", "error")
            else:
                print_status(f"{var}: Não configurada (opcional)", "warning")

    return bool(vars_status["TRANSPARENCY_API_KEY"])


@pytest.mark.asyncio
async def test_sample_query():
    """Faz uma consulta de exemplo"""
    print_status("Fazendo consulta de exemplo...", "info")

    # Importar a função simplificada
    try:
        from app_transparency_api import SimplifiedTransparencyAPI

        api_key = os.getenv("TRANSPARENCY_API_KEY")
        if not api_key:
            print_status("Pule este teste - API key não configurada", "warning")
            return

        async with SimplifiedTransparencyAPI(api_key) as api:
            # Buscar contratos do MEC
            filters = {"ano": 2024, "orgao": "26000", "pagina": 1, "tamanho": 5}  # MEC

            result = await api.search_contracts(filters)

            if result["success"]:
                print_status("Consulta bem-sucedida!", "success")
                data = result["data"]

                if isinstance(data, list):
                    print_status(f"Encontrados {len(data)} contratos", "info")
                elif isinstance(data, dict) and "data" in data:
                    print_status(f"Encontrados {len(data['data'])} contratos", "info")
            else:
                print_status(f"Erro na consulta: {result['error']}", "error")

    except Exception as e:
        print_status(f"Erro ao executar consulta: {str(e)}", "error")


def create_env_template():
    """Cria arquivo .env de exemplo"""
    print_status("Criando arquivo .env.example...", "info")

    template = """# Cidadão.AI - Variáveis de Ambiente
# Copie este arquivo para .env e preencha com suas chaves

# OBRIGATÓRIO - API do Portal da Transparência
# Obtenha em: https://portaldatransparencia.gov.br/api-de-dados
TRANSPARENCY_API_KEY=sua_chave_aqui

# OPCIONAL - Groq AI para análises
# Obtenha em: https://console.groq.com
GROQ_API_KEY=

# OPCIONAL - Outras configurações
# PORT=7860
# DEBUG=False
"""

    with open(".env.example", "w") as f:
        f.write(template)

    print_status(".env.example criado com sucesso", "success")


async def main():
    """Executa todos os testes"""
    print(f"\n{BLUE}{'='*50}{RESET}")
    print(f"{BLUE}🇧🇷 Cidadão.AI - Teste de API de Transparência{RESET}")
    print(f"{BLUE}{'='*50}{RESET}\n")

    # 1. Verificar dependências
    print(f"\n{YELLOW}1. VERIFICANDO DEPENDÊNCIAS{RESET}\n")
    deps_ok = test_dependencies()

    if not deps_ok:
        print_status("\nInstale as dependências faltantes antes de continuar", "error")
        print_status("Use: pip install -r requirements_hf_api.txt", "warning")
        return

    # 2. Verificar variáveis de ambiente
    print(f"\n{YELLOW}2. VERIFICANDO VARIÁVEIS DE AMBIENTE{RESET}\n")
    env_ok = check_env_vars()

    if not env_ok:
        create_env_template()
        print_status("\nConfigure as variáveis de ambiente antes de continuar", "error")
        print_status("1. Copie .env.example para .env", "warning")
        print_status("2. Adicione sua TRANSPARENCY_API_KEY", "warning")
        return

    # 3. Testar conexão com API
    print(f"\n{YELLOW}3. TESTANDO CONEXÃO COM API{RESET}\n")
    api_ok = await test_api_connection()

    if not api_ok:
        print_status("\nVerifique sua API key e conexão com internet", "error")
        return

    # 4. Testar Backend Dependencies
    print(f"\n{YELLOW}4. TESTANDO DEPENDÊNCIAS BACKEND{RESET}\n")
    backend_ok = test_backend_dependencies()

    # 5. Fazer consulta de exemplo
    if api_ok:
        print(f"\n{YELLOW}5. FAZENDO CONSULTA DE EXEMPLO{RESET}\n")
        await test_sample_query()

    # Resumo final
    print(f"\n{BLUE}{'='*50}{RESET}")
    print(f"{BLUE}RESUMO DOS TESTES{RESET}")
    print(f"{BLUE}{'='*50}{RESET}\n")

    all_tests = deps_ok and env_ok and api_ok and backend_ok

    if all_tests:
        print_status("Todos os testes passaram! ✨", "success")
        print_status("Backend está pronto para deployment!", "success")
        print_status("\nPróximos passos:", "info")
        print("1. Configure variáveis de ambiente no servidor")
        print("2. Execute com: uvicorn app:app --host 0.0.0.0 --port 8000")
        print("3. Ou use Docker: docker-compose up")
        print("4. Acesse a documentação em /docs")
    else:
        print_status("Alguns testes falharam", "error")
        print_status("Corrija os problemas antes do deployment", "warning")

    print(f"\n{BLUE}{'='*50}{RESET}\n")


if __name__ == "__main__":
    # Carregar .env se existir
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        print_status(
            "python-dotenv não instalado - variáveis de ambiente do sistema serão usadas",
            "warning",
        )

    # Executar testes
    asyncio.run(main())
