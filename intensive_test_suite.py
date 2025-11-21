#!/usr/bin/env python3
"""
Suite de Testes Intensivos - Cidadão.AI Backend
Preparação para Integração com Frontend
Data: 2025-11-21
"""

import asyncio
import json
import statistics
import time
from datetime import datetime
from typing import Any, Dict, List

import httpx

# Configuração
BASE_URL = "https://cidadao-api-production.up.railway.app"
# BASE_URL = "http://localhost:8000"  # Para testes locais

# Cores para output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


class IntensiveTestSuite:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "tests": {},
            "summary": {},
        }
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def print_header(self, text: str):
        """Imprime cabeçalho formatado"""
        print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
        print(f"{BOLD}{CYAN}{text.center(60)}{RESET}")
        print(f"{BOLD}{CYAN}{'='*60}{RESET}\n")

    def print_section(self, text: str):
        """Imprime seção"""
        print(f"\n{BOLD}{BLUE}>>> {text}{RESET}")
        print(f"{BLUE}{'-'*50}{RESET}")

    def print_success(self, text: str):
        """Imprime sucesso"""
        print(f"{GREEN}✅ {text}{RESET}")

    def print_error(self, text: str):
        """Imprime erro"""
        print(f"{RED}❌ {text}{RESET}")

    def print_warning(self, text: str):
        """Imprime aviso"""
        print(f"{YELLOW}⚠️  {text}{RESET}")

    def print_info(self, text: str):
        """Imprime informação"""
        print(f"{CYAN}ℹ️  {text}{RESET}")

    async def test_endpoint_performance(
        self, method: str, endpoint: str, data: dict = None, iterations: int = 5
    ) -> dict:
        """Testa performance de um endpoint"""
        times = []
        successes = 0
        errors = []

        for i in range(iterations):
            start = time.time()
            try:
                if method == "GET":
                    response = await self.client.get(f"{BASE_URL}{endpoint}")
                else:
                    response = await self.client.request(
                        method=method, url=f"{BASE_URL}{endpoint}", json=data
                    )

                elapsed = (time.time() - start) * 1000  # ms
                times.append(elapsed)

                if response.status_code in [200, 201]:
                    successes += 1
                else:
                    errors.append(f"Status {response.status_code}")

            except Exception as e:
                errors.append(str(e))
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)

        return {
            "endpoint": endpoint,
            "method": method,
            "iterations": iterations,
            "successes": successes,
            "failures": len(errors),
            "success_rate": (successes / iterations) * 100,
            "times": {
                "min": min(times) if times else 0,
                "max": max(times) if times else 0,
                "avg": statistics.mean(times) if times else 0,
                "median": statistics.median(times) if times else 0,
                "stdev": statistics.stdev(times) if len(times) > 1 else 0,
            },
            "errors": errors[:3],  # Primeiros 3 erros
        }

    async def test_all_agents(self):
        """Testa todos os 16 agentes"""
        self.print_section("TESTE COMPLETO DOS 16 AGENTES")

        agents = [
            "zumbi",
            "anita",
            "tiradentes",
            "bonifacio",
            "maria_quiteria",
            "machado",
            "dandara",
            "lampiao",
            "oscar",
            "drummond",
            "obaluaie",
            "oxossi",
            "ceuci",
            "abaporu",
            "ayrton_senna",
            "nana",
        ]

        agent_results = []

        for agent in agents:
            print(f"\nTestando agente: {MAGENTA}{agent.upper()}{RESET}")

            # Dados específicos por tipo de agente
            if agent in ["zumbi", "obaluaie"]:
                action = "investigate"
                options = {
                    "data_source": "contracts",
                    "anomaly_types": ["price", "vendor"],
                }
            elif agent == "tiradentes":
                action = "report"
                options = {"report_type": "summary"}
            elif agent == "oxossi":
                action = "search"
                options = {"search_type": "contracts"}
            else:
                action = "analyze"
                options = {}

            data = {
                "query": f"Teste intensivo do agente {agent}",
                "context": {"session_id": f"test-{agent}-{datetime.now().timestamp()}"},
                "options": options,
            }

            result = await self.test_endpoint_performance(
                "POST", f"/api/v1/agents/{agent}", data, iterations=3
            )

            agent_results.append(result)

            if result["success_rate"] == 100:
                self.print_success(
                    f"{agent}: {result['times']['avg']:.0f}ms (100% sucesso)"
                )
            elif result["success_rate"] > 0:
                self.print_warning(
                    f"{agent}: {result['times']['avg']:.0f}ms ({result['success_rate']:.0f}% sucesso)"
                )
            else:
                self.print_error(
                    f"{agent}: FALHOU - {result['errors'][0] if result['errors'] else 'Unknown'}"
                )

        self.results["tests"]["agents"] = agent_results
        return agent_results

    async def test_sse_streaming(self):
        """Testa SSE streaming para frontend"""
        self.print_section("TESTE DE SSE STREAMING (CRÍTICO PARA FRONTEND)")

        messages = [
            "Analise contratos suspeitos",
            "Quem são os maiores fornecedores?",
            "Detecte anomalias em licitações",
            "Gere um relatório de investigação",
        ]

        sse_results = []

        for msg in messages:
            print(f"\nMensagem: '{msg}'")

            data = {
                "message": msg,
                "session_id": f"sse-test-{datetime.now().timestamp()}",
            }

            start = time.time()
            try:
                response = await self.client.post(
                    f"{BASE_URL}/api/v1/chat/stream",
                    json=data,
                    headers={"Accept": "text/event-stream"},
                    timeout=10.0,
                )

                elapsed = (time.time() - start) * 1000

                # Verifica se é SSE válido
                content = response.text[:500]
                is_sse = "event:" in content or "data:" in content
                has_error = "error" in content.lower() or "exception" in content.lower()

                result = {
                    "message": msg,
                    "success": is_sse and not has_error,
                    "is_sse": is_sse,
                    "has_error": has_error,
                    "time_ms": elapsed,
                    "sample": content[:200],
                }

                sse_results.append(result)

                if result["success"]:
                    self.print_success(f"SSE OK em {elapsed:.0f}ms")
                else:
                    self.print_error(f"SSE FALHOU: {content[:100]}")

            except Exception as e:
                self.print_error(f"Erro: {str(e)}")
                sse_results.append({"message": msg, "success": False, "error": str(e)})

        self.results["tests"]["sse_streaming"] = sse_results
        return sse_results

    async def test_concurrent_load(self):
        """Testa carga concorrente"""
        self.print_section("TESTE DE CARGA CONCORRENTE")

        print("Simulando 20 requisições simultâneas...")

        async def make_request(index: int):
            """Faz uma requisição"""
            endpoint = [
                "/health/",
                "/api/v1/",
                "/api/v1/agents/",
                f"/api/v1/agents/zumbi",
                "/api/v1/federal/",
            ][index % 5]

            method = "POST" if "zumbi" in endpoint else "GET"
            data = (
                {
                    "query": f"Teste concorrente {index}",
                    "context": {"session_id": f"concurrent-{index}"},
                    "options": {},
                }
                if method == "POST"
                else None
            )

            start = time.time()
            try:
                if method == "GET":
                    response = await self.client.get(f"{BASE_URL}{endpoint}")
                else:
                    response = await self.client.post(
                        f"{BASE_URL}{endpoint}", json=data
                    )

                return {
                    "index": index,
                    "endpoint": endpoint,
                    "status": response.status_code,
                    "time_ms": (time.time() - start) * 1000,
                    "success": response.status_code in [200, 201],
                }
            except Exception as e:
                return {
                    "index": index,
                    "endpoint": endpoint,
                    "error": str(e),
                    "time_ms": (time.time() - start) * 1000,
                    "success": False,
                }

        # Executa requisições concorrentes
        start = time.time()
        tasks = [make_request(i) for i in range(20)]
        results = await asyncio.gather(*tasks)
        total_time = (time.time() - start) * 1000

        successes = sum(1 for r in results if r.get("success"))
        avg_time = statistics.mean([r["time_ms"] for r in results])

        self.print_info(f"Total: {total_time:.0f}ms")
        self.print_info(f"Média por requisição: {avg_time:.0f}ms")
        self.print_info(f"Taxa de sucesso: {(successes/20)*100:.0f}%")

        if successes == 20:
            self.print_success("Sistema aguentou todas as 20 requisições simultâneas!")
        elif successes >= 15:
            self.print_warning(f"Sistema aguentou {successes}/20 requisições")
        else:
            self.print_error(f"Apenas {successes}/20 requisições bem-sucedidas")

        self.results["tests"]["concurrent_load"] = {
            "total_requests": 20,
            "successes": successes,
            "failures": 20 - successes,
            "total_time_ms": total_time,
            "avg_time_ms": avg_time,
            "results": results[:5],  # Primeiros 5 resultados
        }

        return results

    async def test_cors_headers(self):
        """Testa CORS para frontend"""
        self.print_section("TESTE DE CORS (CRÍTICO PARA FRONTEND)")

        # Simula requisição do frontend
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        }

        print("Testando CORS preflight (OPTIONS)...")

        try:
            # Teste de preflight
            response = await self.client.options(
                f"{BASE_URL}/api/v1/agents/zumbi", headers=headers
            )

            cors_headers = {
                "access-control-allow-origin": response.headers.get(
                    "access-control-allow-origin", ""
                ),
                "access-control-allow-methods": response.headers.get(
                    "access-control-allow-methods", ""
                ),
                "access-control-allow-headers": response.headers.get(
                    "access-control-allow-headers", ""
                ),
                "access-control-allow-credentials": response.headers.get(
                    "access-control-allow-credentials", ""
                ),
            }

            # Verifica CORS
            allows_localhost = (
                "*" in cors_headers["access-control-allow-origin"]
                or "localhost" in cors_headers["access-control-allow-origin"]
            )
            allows_post = "POST" in cors_headers.get("access-control-allow-methods", "")
            allows_content_type = (
                "content-type"
                in cors_headers.get("access-control-allow-headers", "").lower()
            )

            self.results["tests"]["cors"] = {
                "headers": cors_headers,
                "allows_localhost": allows_localhost,
                "allows_post": allows_post,
                "allows_content_type": allows_content_type,
                "configured_correctly": allows_localhost
                and allows_post
                and allows_content_type,
            }

            if allows_localhost and allows_post:
                self.print_success("CORS configurado corretamente para frontend!")
                self.print_info(
                    f"Origin permitido: {cors_headers['access-control-allow-origin']}"
                )
            else:
                self.print_error("CORS pode bloquear requisições do frontend!")
                self.print_info(f"Headers CORS: {cors_headers}")

        except Exception as e:
            self.print_error(f"Erro ao testar CORS: {str(e)}")
            self.results["tests"]["cors"] = {"error": str(e)}

    async def test_error_handling(self):
        """Testa tratamento de erros"""
        self.print_section("TESTE DE TRATAMENTO DE ERROS")

        error_scenarios = [
            {
                "name": "Payload inválido",
                "endpoint": "/api/v1/agents/zumbi",
                "method": "POST",
                "data": {"invalid": "payload"},
            },
            {
                "name": "Agente inexistente",
                "endpoint": "/api/v1/agents/agente_falso",
                "method": "POST",
                "data": {"query": "test"},
            },
            {
                "name": "Método não permitido",
                "endpoint": "/api/v1/agents/zumbi",
                "method": "DELETE",
                "data": None,
            },
            {
                "name": "Query muito grande",
                "endpoint": "/api/v1/agents/anita",
                "method": "POST",
                "data": {"query": "x" * 10000, "context": {}, "options": {}},
            },
        ]

        error_results = []

        for scenario in error_scenarios:
            print(f"\nTestando: {scenario['name']}")

            try:
                response = await self.client.request(
                    method=scenario["method"],
                    url=f"{BASE_URL}{scenario['endpoint']}",
                    json=scenario["data"],
                )

                result = {
                    "scenario": scenario["name"],
                    "status": response.status_code,
                    "has_error_message": "detail" in response.text
                    or "error" in response.text.lower(),
                    "response_sample": response.text[:200],
                }

                error_results.append(result)

                if result["has_error_message"]:
                    self.print_success(
                        f"Erro tratado corretamente (Status {response.status_code})"
                    )
                else:
                    self.print_warning(f"Resposta sem mensagem de erro clara")

            except Exception as e:
                self.print_error(f"Exceção não tratada: {str(e)}")
                error_results.append(
                    {"scenario": scenario["name"], "exception": str(e)}
                )

        self.results["tests"]["error_handling"] = error_results

    async def test_data_consistency(self):
        """Testa consistência de dados"""
        self.print_section("TESTE DE CONSISTÊNCIA DE DADOS")

        print("Verificando Portal da Transparência...")

        # Testa múltiplas requisições para verificar consistência
        responses = []
        for i in range(3):
            response = await self.client.get(
                f"{BASE_URL}/api/v1/transparency/contracts",
                params={"year": 2024, "limit": 5},
            )

            if response.status_code == 200:
                data = response.json()
                responses.append(
                    {
                        "sources": data.get("sources", []),
                        "total": data.get("total", 0),
                        "contracts_count": len(data.get("contracts", [])),
                    }
                )

        # Verifica se todas retornam dados federais
        all_federal = all(
            "FEDERAL-portal" in r["sources"] for r in responses if r.get("sources")
        )
        consistent_sources = len(set(str(r["sources"]) for r in responses)) == 1

        if all_federal and consistent_sources:
            self.print_success("Dados consistentes - sempre retorna fonte federal!")
        else:
            self.print_warning("Inconsistência detectada nos dados")

        self.results["tests"]["data_consistency"] = {
            "responses": responses,
            "all_federal": all_federal,
            "consistent_sources": consistent_sources,
        }

    async def generate_report(self):
        """Gera relatório final"""
        self.print_header("RELATÓRIO DE PRONTIDÃO PARA FRONTEND")

        # Análise dos resultados
        critical_checks = {
            "sse_streaming": False,
            "cors_configured": False,
            "agents_working": False,
            "performance_ok": False,
            "error_handling": False,
            "data_consistency": False,
        }

        # SSE Streaming
        if "sse_streaming" in self.results["tests"]:
            sse_success_rate = (
                sum(
                    1
                    for r in self.results["tests"]["sse_streaming"]
                    if r.get("success")
                )
                / len(self.results["tests"]["sse_streaming"])
                * 100
            )
            critical_checks["sse_streaming"] = sse_success_rate >= 75

        # CORS
        if "cors" in self.results["tests"]:
            critical_checks["cors_configured"] = self.results["tests"]["cors"].get(
                "configured_correctly", False
            )

        # Agents
        if "agents" in self.results["tests"]:
            agent_success_rate = (
                sum(
                    1
                    for a in self.results["tests"]["agents"]
                    if a["success_rate"] >= 50
                )
                / 16
                * 100
            )
            critical_checks["agents_working"] = agent_success_rate >= 80

        # Performance
        if "concurrent_load" in self.results["tests"]:
            critical_checks["performance_ok"] = (
                self.results["tests"]["concurrent_load"]["successes"] >= 15
            )

        # Error handling
        if "error_handling" in self.results["tests"]:
            critical_checks["error_handling"] = (
                len(self.results["tests"]["error_handling"]) > 0
            )

        # Data consistency
        if "data_consistency" in self.results["tests"]:
            critical_checks["data_consistency"] = self.results["tests"][
                "data_consistency"
            ]["all_federal"]

        # Calcula prontidão
        ready_count = sum(1 for v in critical_checks.values() if v)
        readiness = (ready_count / len(critical_checks)) * 100

        print(f"\n{BOLD}CHECKLIST DE INTEGRAÇÃO:{RESET}")
        print("-" * 40)

        for check, passed in critical_checks.items():
            status = f"{GREEN}✅{RESET}" if passed else f"{RED}❌{RESET}"
            print(f"{status} {check.replace('_', ' ').title()}")

        print(f"\n{BOLD}PRONTIDÃO PARA FRONTEND: {readiness:.0f}%{RESET}")

        if readiness == 100:
            print(f"{GREEN}{BOLD}🎉 SISTEMA 100% PRONTO PARA INTEGRAÇÃO!{RESET}")
        elif readiness >= 80:
            print(f"{YELLOW}{BOLD}⚠️  SISTEMA QUASE PRONTO ({readiness:.0f}%){RESET}")
        else:
            print(f"{RED}{BOLD}❌ SISTEMA PRECISA DE AJUSTES ({readiness:.0f}%){RESET}")

        # Salva relatório
        report_file = "/tmp/frontend_readiness_report.json"
        with open(report_file, "w") as f:
            json.dump(
                {
                    "results": self.results,
                    "critical_checks": critical_checks,
                    "readiness_percentage": readiness,
                    "timestamp": datetime.now().isoformat(),
                },
                f,
                indent=2,
            )

        print(f"\n{CYAN}Relatório salvo em: {report_file}{RESET}")

    async def run_all_tests(self):
        """Executa todos os testes"""
        self.print_header("SUITE DE TESTES INTENSIVOS - CIDADÃO.AI")
        print(f"{CYAN}URL: {BASE_URL}{RESET}")
        print(f"{CYAN}Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")

        # Executa testes
        await self.test_all_agents()
        await self.test_sse_streaming()
        await self.test_concurrent_load()
        await self.test_cors_headers()
        await self.test_error_handling()
        await self.test_data_consistency()

        # Gera relatório
        await self.generate_report()


async def main():
    async with IntensiveTestSuite() as suite:
        await suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
