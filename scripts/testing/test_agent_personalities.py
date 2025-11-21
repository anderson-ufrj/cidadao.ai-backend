#!/usr/bin/env python3
"""
Test Agent Personalities - Verify that agents respond with their character personalities.
"""

import asyncio
import json
from datetime import datetime

import httpx
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Configuration
BASE_URL = "https://cidadao-api-production.up.railway.app"

# Agent test cases with expected personality traits
AGENT_TESTS = [
    {
        "name": "zumbi",
        "query": "Olá, quem é você?",
        "personality_keywords": [
            "Palmares",
            "resistência",
            "luta",
            "liberdade",
            "quilombo",
        ],
        "description": "Zumbi dos Palmares - Líder quilombola",
    },
    {
        "name": "anita",
        "query": "Me fale sobre você",
        "personality_keywords": [
            "Garibaldi",
            "república",
            "revolução",
            "guerreira",
            "Laguna",
        ],
        "description": "Anita Garibaldi - Revolucionária",
    },
    {
        "name": "tiradentes",
        "query": "Qual sua missão?",
        "personality_keywords": [
            "Inconfidência",
            "independência",
            "Minas",
            "justiça",
            "liberdade",
        ],
        "description": "Tiradentes - Mártir da Independência",
    },
    {
        "name": "bonifacio",
        "query": "O que você faz?",
        "personality_keywords": [
            "Patriarca",
            "independência",
            "lei",
            "constituição",
            "Brasil",
        ],
        "description": "José Bonifácio - Patriarca da Independência",
    },
    {
        "name": "maria-quiteria",
        "query": "Conte sobre você",
        "personality_keywords": [
            "soldado",
            "Bahia",
            "independência",
            "coragem",
            "mulher",
        ],
        "description": "Maria Quitéria - Primeira mulher soldado",
    },
    {
        "name": "machado",
        "query": "Quem é você?",
        "personality_keywords": [
            "Assis",
            "literatura",
            "ironia",
            "Academia",
            "realismo",
        ],
        "description": "Machado de Assis - Escritor",
    },
    {
        "name": "dandara",
        "query": "Qual sua história?",
        "personality_keywords": [
            "Palmares",
            "guerreira",
            "capoeira",
            "resistência",
            "quilombo",
        ],
        "description": "Dandara - Guerreira de Palmares",
    },
    {
        "name": "lampiao",
        "query": "Me conta sua história",
        "personality_keywords": ["cangaço", "sertão", "Nordeste", "capitão", "justiça"],
        "description": "Lampião - Rei do Cangaço",
    },
    {
        "name": "oscar",
        "query": "O que você constrói?",
        "personality_keywords": [
            "arquitetura",
            "Brasília",
            "curvas",
            "concreto",
            "modernismo",
        ],
        "description": "Oscar Niemeyer - Arquiteto",
    },
    {
        "name": "drummond",
        "query": "Recite um verso",
        "personality_keywords": ["Itabira", "poeta", "verso", "mineiro", "pedra"],
        "description": "Carlos Drummond - Poeta",
    },
    {
        "name": "obaluaie",
        "query": "Qual seu poder?",
        "personality_keywords": ["cura", "saúde", "orixá", "doença", "proteção"],
        "description": "Obaluaê - Orixá da cura",
    },
    {
        "name": "oxossi",
        "query": "O que você caça?",
        "personality_keywords": [
            "caçador",
            "floresta",
            "flecha",
            "orixá",
            "conhecimento",
        ],
        "description": "Oxóssi - Orixá caçador",
    },
    {
        "name": "ceuci",
        "query": "O que você prevê?",
        "personality_keywords": ["mãe", "lua", "indígena", "proteção", "natureza"],
        "description": "Ceuci - Deusa indígena",
    },
    {
        "name": "abaporu",
        "query": "Qual sua função?",
        "personality_keywords": [
            "antropofagia",
            "modernismo",
            "Tarsila",
            "cultura",
            "brasileiro",
        ],
        "description": "Abaporu - Símbolo antropofágico",
    },
    {
        "name": "ayrton-senna",
        "query": "Qual sua velocidade?",
        "personality_keywords": [
            "Fórmula",
            "velocidade",
            "campeão",
            "Brasil",
            "piloto",
        ],
        "description": "Ayrton Senna - Piloto de F1",
    },
    {
        "name": "nana",
        "query": "O que você guarda?",
        "personality_keywords": ["ancestral", "memória", "sabedoria", "orixá", "mãe"],
        "description": "Nanã - Orixá ancestral",
    },
]


async def test_agent_personality(agent: dict) -> dict:
    """Test a single agent for personality traits."""
    print(
        f"\n{Fore.CYAN}Testing {agent['name'].upper()}: {agent['description']}{Style.RESET_ALL}"
    )

    url = f"{BASE_URL}/api/v1/agents/{agent['name']}"
    payload = {"query": agent["query"], "context": {}, "options": {}}

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()
                result_text = json.dumps(data, ensure_ascii=False).lower()

                # Check for personality keywords
                found_keywords = []
                for keyword in agent["personality_keywords"]:
                    if keyword.lower() in result_text:
                        found_keywords.append(keyword)

                personality_score = len(found_keywords) / len(
                    agent["personality_keywords"]
                )

                # Print result
                if personality_score > 0.3:  # At least 30% of keywords found
                    print(f"{Fore.GREEN}✅ Personality detected!{Style.RESET_ALL}")
                    print(f"   Found keywords: {', '.join(found_keywords)}")
                else:
                    print(f"{Fore.YELLOW}⚠️ Weak personality response{Style.RESET_ALL}")
                    print(
                        f"   Found only: {', '.join(found_keywords) if found_keywords else 'none'}"
                    )

                # Print sample of response
                if "result" in data and isinstance(data["result"], dict):
                    if "message" in data["result"]:
                        sample = data["result"]["message"][:200]
                        print(f'   Response: "{sample}..."')

                return {
                    "agent": agent["name"],
                    "status": "success",
                    "personality_score": personality_score,
                    "found_keywords": found_keywords,
                }
            else:
                print(
                    f"{Fore.RED}❌ Failed with status {response.status_code}{Style.RESET_ALL}"
                )
                return {
                    "agent": agent["name"],
                    "status": "error",
                    "error": f"Status {response.status_code}",
                }

        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
            return {
                "agent": agent["name"],
                "status": "error",
                "error": str(e),
            }


async def main():
    """Run personality tests for all agents."""
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}    TESTE DE PERSONALIDADES DOS AGENTES{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"\nURL: {BASE_URL}")
    print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test all agents
    results = []
    for agent in AGENT_TESTS:
        result = await test_agent_personality(agent)
        results.append(result)
        await asyncio.sleep(0.5)  # Small delay between requests

    # Summary
    print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}    RESUMO{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")

    successful = [r for r in results if r["status"] == "success"]
    strong_personality = [r for r in successful if r.get("personality_score", 0) > 0.3]

    print(f"\nAgentes testados: {len(results)}")
    print(f"Funcionando: {len(successful)} ({len(successful)*100//len(results)}%)")
    print(
        f"Com personalidade forte: {len(strong_personality)} ({len(strong_personality)*100//len(results)}%)"
    )

    # List failing agents
    failing = [r for r in results if r["status"] == "error"]
    if failing:
        print(f"\n{Fore.RED}Agentes com erro:{Style.RESET_ALL}")
        for f in failing:
            print(f"  - {f['agent']}: {f['error']}")

    # List weak personality agents
    weak = [r for r in successful if r.get("personality_score", 0) <= 0.3]
    if weak:
        print(f"\n{Fore.YELLOW}Agentes com personalidade fraca:{Style.RESET_ALL}")
        for w in weak:
            print(
                f"  - {w['agent']}: {int(w['personality_score']*100)}% dos traços detectados"
            )


if __name__ == "__main__":
    asyncio.run(main())
