"""
APIs Governamentais Brasileiras - Exemplos de Uso
Projeto: Cidadão.AI
Data: Outubro 2025

Exemplos práticos de integração com as principais APIs gov.br
"""

import time
from dataclasses import dataclass
from functools import wraps
from typing import Optional

import requests

# =============================================================================
# CONFIGURAÇÕES E CONSTANTES
# =============================================================================


@dataclass
class APIConfig:
    """Configuração base para APIs governamentais"""

    base_url: str
    auth_type: Optional[str] = None
    api_key: Optional[str] = None
    rate_limit: Optional[int] = None  # requests per minute
    timeout: int = 30


# Configurações das principais APIs
CONFIGS = {
    "transparencia": APIConfig(
        base_url="https://api.portaldatransparencia.gov.br/api-de-dados",
        auth_type="api_key",
        api_key="YOUR_API_KEY_HERE",  # Solicitar em: portaldatransparencia.gov.br/api-de-dados
        rate_limit=90,
        timeout=30,
    ),
    "camara": APIConfig(
        base_url="https://dadosabertos.camara.leg.br/api/v2", auth_type=None, timeout=30
    ),
    "senado": APIConfig(
        base_url="https://legis.senado.leg.br/dadosabertos", auth_type=None, timeout=30
    ),
    "ibge": APIConfig(
        base_url="https://servicodados.ibge.gov.br/api", auth_type=None, timeout=30
    ),
    "datajud": APIConfig(
        base_url="https://api-publica.datajud.cnj.jus.br",
        auth_type="api_key",
        api_key="cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==",  # Chave pública atual
        timeout=30,
    ),
    "tcu": APIConfig(
        base_url="https://contas.tcu.gov.br/ords", auth_type=None, timeout=30
    ),
    "siconfi": APIConfig(
        base_url="https://apidatalake.tesouro.gov.br",
        auth_type=None,
        timeout=60,  # queries mais pesadas
    ),
}


# =============================================================================
# DECORATORS E UTILITIES
# =============================================================================


def rate_limit(calls_per_minute: int):
    """Rate limiter simples"""
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret

        return wrapper

    return decorator


def retry_on_failure(max_retries: int = 3, backoff: float = 2.0):
    """Retry com exponential backoff"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.RequestException:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = backoff**attempt
                    print(f"Tentativa {attempt + 1} falhou. Aguardando {wait_time}s...")
                    time.sleep(wait_time)

        return wrapper

    return decorator


# =============================================================================
# PORTAL DA TRANSPARÊNCIA FEDERAL
# =============================================================================


class TransparenciaAPI:
    """Cliente para API do Portal da Transparência"""

    def __init__(self, api_key: str):
        self.config = CONFIGS["transparencia"]
        self.config.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"chave-api-dados": api_key})

    @rate_limit(90)  # 90 req/min
    @retry_on_failure(3)
    def _request(self, endpoint: str, params: dict = None) -> dict:
        """Request base com rate limiting e retry"""
        url = f"{self.config.base_url}{endpoint}"
        response = self.session.get(url, params=params, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def despesas_por_orgao(self, ano: int, mes: int, pagina: int = 1) -> list[dict]:
        """Busca despesas do governo por órgão"""
        params = {"mesAno": f"{ano}{mes:02d}", "pagina": pagina}
        return self._request("/despesas/por-orgao", params)

    def contratos(self, cnpj_contratada: str) -> list[dict]:
        """Busca contratos de uma empresa com o governo"""
        return self._request(f"/contratos/{cnpj_contratada}")

    def servidores_por_orgao(self, codigo_orgao: str, pagina: int = 1) -> list[dict]:
        """Lista servidores de um órgão"""
        params = {"pagina": pagina}
        return self._request(f"/servidores/{codigo_orgao}", params)

    def ceis(self, cnpj: str = None, nome: str = None) -> list[dict]:
        """Consulta Cadastro de Empresas Inidôneas e Suspensas"""
        params = {}
        if cnpj:
            params["cnpjSancionado"] = cnpj
        if nome:
            params["nomeSancionado"] = nome
        return self._request("/ceis", params)


# =============================================================================
# CÂMARA DOS DEPUTADOS
# =============================================================================


class CamaraAPI:
    """Cliente para API de Dados Abertos da Câmara"""

    def __init__(self):
        self.config = CONFIGS["camara"]
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    @retry_on_failure(3)
    def _request(self, endpoint: str, params: dict = None) -> dict:
        url = f"{self.config.base_url}{endpoint}"
        response = self.session.get(url, params=params, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def deputados(
        self, nome: str = None, partido: str = None, uf: str = None
    ) -> list[dict]:
        """Lista deputados com filtros opcionais"""
        params = {}
        if nome:
            params["nome"] = nome
        if partido:
            params["siglaPartido"] = partido
        if uf:
            params["siglaUf"] = uf

        result = self._request("/deputados", params)
        return result.get("dados", [])

    def despesas_deputado(
        self, id_deputado: int, ano: int = None, mes: int = None
    ) -> list[dict]:
        """Busca despesas de um deputado (cota parlamentar)"""
        params = {"ordem": "ASC", "ordenarPor": "dataDocumento"}
        if ano:
            params["ano"] = ano
        if mes:
            params["mes"] = mes

        result = self._request(f"/deputados/{id_deputado}/despesas", params)
        return result.get("dados", [])

    def proposicoes(
        self, tema: str = None, autor: str = None, ano: int = None
    ) -> list[dict]:
        """Busca proposições (projetos de lei)"""
        params = {"ordem": "DESC", "ordenarPor": "id"}
        if tema:
            params["keywords"] = tema
        if autor:
            params["siglaTipo"] = autor
        if ano:
            params["ano"] = ano

        result = self._request("/proposicoes", params)
        return result.get("dados", [])

    def votacoes(self, id_proposicao: int) -> list[dict]:
        """Busca votações de uma proposição"""
        result = self._request(f"/proposicoes/{id_proposicao}/votacoes")
        return result.get("dados", [])


# =============================================================================
# CNJ - DATAJUD
# =============================================================================


class DataJudAPI:
    """Cliente para API Pública do DataJud"""

    def __init__(self, api_key: str):
        self.config = CONFIGS["datajud"]
        self.config.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"APIKey {api_key}", "Content-Type": "application/json"}
        )

    @retry_on_failure(3)
    def buscar_processos(self, tribunal: str, query: dict, size: int = 10) -> dict:
        """
        Busca processos no DataJud

        Args:
            tribunal: Sigla do tribunal (ex: 'tjsp', 'trf4', 'tjdft')
            query: Query Elasticsearch
            size: Número de resultados
        """
        url = f"{self.config.base_url}/api_publica_{tribunal}/_search"

        body = {"query": query, "size": size}

        response = self.session.post(url, json=body, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def processos_por_classe(
        self, tribunal: str, classe: str, limit: int = 100
    ) -> list[dict]:
        """Busca processos por classe processual"""
        query = {"match": {"classe.nome": classe}}
        result = self.buscar_processos(tribunal, query, size=limit)
        return result.get("hits", {}).get("hits", [])

    def processos_por_assunto(
        self, tribunal: str, assunto: str, limit: int = 100
    ) -> list[dict]:
        """Busca processos por assunto"""
        query = {"match": {"assuntos.nome": assunto}}
        result = self.buscar_processos(tribunal, query, size=limit)
        return result.get("hits", {}).get("hits", [])


# =============================================================================
# IBGE
# =============================================================================


class IBGEAPI:
    """Cliente para APIs do IBGE"""

    def __init__(self):
        self.config = CONFIGS["ibge"]
        self.session = requests.Session()

    @retry_on_failure(3)
    def _request(self, path: str, params: dict = None) -> any:
        url = f"{self.config.base_url}{path}"
        response = self.session.get(url, params=params, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def municipios(self, uf: str = None) -> list[dict]:
        """Lista municípios, opcionalmente filtrados por UF"""
        if uf:
            return self._request(f"/v1/localidades/estados/{uf}/municipios")
        return self._request("/v1/localidades/municipios")

    def municipio_por_nome(self, nome: str) -> list[dict]:
        """Busca município por nome"""
        municipios = self.municipios()
        return [m for m in municipios if nome.lower() in m["nome"].lower()]

    def agregados_sidra(
        self,
        tabela: int,
        variaveis: list[int],
        localidades: str = "N3[all]",  # todos municípios
        periodos: str = "-1",
    ) -> list[dict]:
        """
        Consulta tabela do SIDRA

        Args:
            tabela: Código da tabela
            variaveis: Lista de códigos de variáveis
            localidades: String de localidades (N1=Brasil, N3=Municípios, etc)
            periodos: Períodos (-1 = mais recente, -6 = últimos 6, etc)
        """
        vars_str = "|".join(map(str, variaveis))
        path = f"/v3/agregados/{tabela}/periodos/{periodos}/variaveis/{vars_str}"
        params = {"localidades": localidades}
        return self._request(path, params)


# =============================================================================
# TCU
# =============================================================================


class TCUAPI:
    """Cliente para webservices do TCU"""

    def __init__(self):
        self.config = CONFIGS["tcu"]
        self.session = requests.Session()

    @retry_on_failure(3)
    def _request(self, path: str, params: dict = None) -> any:
        url = f"{self.config.base_url}{path}"
        response = self.session.get(url, params=params, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def inabilitados(self, cpf: str = None) -> list[dict]:
        """Busca inabilitados para exercício de cargo público"""
        if cpf:
            # Remove formatação do CPF
            cpf_limpo = "".join(filter(str.isdigit, cpf))
            return self._request(f"/condenacao/consulta/inabilitados/{cpf_limpo}")
        return self._request("/condenacao/consulta/inabilitados")

    def acordaos(self, numero_processo: str = None) -> list[dict]:
        """Busca acórdãos do TCU"""
        if numero_processo:
            return self._request(f"/api/publica/scn/acordaos/{numero_processo}")
        return self._request("/api/publica/scn/acordaos")


# =============================================================================
# EXEMPLOS DE USO
# =============================================================================


def exemplo_transparencia():
    """Exemplo: Buscar contratos de uma empresa"""
    print("\n=== Portal da Transparência ===")

    api = TransparenciaAPI("YOUR_API_KEY")

    # Buscar contratos
    cnpj = "00000000000191"  # Banco do Brasil
    contratos = api.contratos(cnpj)

    print(f"Encontrados {len(contratos)} contratos")
    if contratos:
        primeiro = contratos[0]
        print(f"Exemplo: {primeiro.get('objeto', 'N/A')}")
        print(f"Valor: R$ {primeiro.get('valorInicial', 0):,.2f}")


def exemplo_camara():
    """Exemplo: Buscar despesas de um deputado"""
    print("\n=== Câmara dos Deputados ===")

    api = CamaraAPI()

    # Buscar deputados de SP do PT
    deputados = api.deputados(partido="PT", uf="SP")
    print(f"Encontrados {len(deputados)} deputados PT-SP")

    if deputados:
        dep = deputados[0]
        print(f"\nAnalisando: {dep['nome']}")

        # Buscar despesas de 2024
        despesas = api.despesas_deputado(dep["id"], ano=2024)
        total = sum(d.get("valorDocumento", 0) for d in despesas)
        print(f"Total gasto em 2024: R$ {total:,.2f}")

        # Top 5 categorias
        por_tipo = {}
        for d in despesas:
            tipo = d.get("tipoDespesa", "Outro")
            por_tipo[tipo] = por_tipo.get(tipo, 0) + d.get("valorDocumento", 0)

        print("\nTop 5 categorias:")
        for tipo, valor in sorted(por_tipo.items(), key=lambda x: -x[1])[:5]:
            print(f"  {tipo}: R$ {valor:,.2f}")


def exemplo_datajud():
    """Exemplo: Buscar processos sobre transparência"""
    print("\n=== DataJud (CNJ) ===")

    api = DataJudAPI("cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==")

    # Buscar processos sobre "transparência pública" no TJDFT
    processos = api.processos_por_assunto("tjdft", "transparência pública", limit=10)

    print(f"Encontrados {len(processos)} processos sobre transparência")
    if processos:
        primeiro = processos[0]["_source"]
        print("\nExemplo:")
        print(f"Número: {primeiro.get('numeroProcesso', 'N/A')}")
        print(f"Classe: {primeiro.get('classe', {}).get('nome', 'N/A')}")


def exemplo_ibge():
    """Exemplo: Buscar dados demográficos"""
    print("\n=== IBGE ===")

    api = IBGEAPI()

    # Buscar municípios de Minas Gerais
    municipios_mg = api.municipios("MG")
    print(f"Minas Gerais tem {len(municipios_mg)} municípios")

    # Buscar população estimada (tabela 6579)
    # Variável 9324 = população residente estimada
    dados = api.agregados_sidra(
        tabela=6579,
        variaveis=[9324],
        localidades="N6[3106200]",  # Belo Horizonte
        periodos="-1",
    )

    if dados and dados[0]["resultados"]:
        pop = dados[0]["resultados"][0]["series"][0]["serie"]
        ano = list(pop.keys())[0]
        valor = list(pop.values())[0]
        print(f"População BH ({ano}): {int(valor):,}")


def exemplo_tcu():
    """Exemplo: Verificar se CPF está inabilitado"""
    print("\n=== TCU ===")

    api = TCUAPI()

    # Buscar inabilitados (todos)
    inabilitados = api.inabilitados()
    print(f"Total de inabilitados: {len(inabilitados)}")

    if inabilitados:
        exemplo = inabilitados[0]
        print("\nExemplo:")
        print(f"Nome: {exemplo.get('nome', 'N/A')}")
        print(f"CPF: {exemplo.get('cpf', 'N/A')}")
        print(f"Processo: {exemplo.get('processo', 'N/A')}")


# =============================================================================
# AGREGADOR DE MÚLTIPLAS FONTES
# =============================================================================


class TransparenciaAggregator:
    """
    Agregador que combina múltiplas APIs para análises integradas
    Útil para o Cidadão.AI
    """

    def __init__(self, transparencia_key: str, datajud_key: str):
        self.transparencia = TransparenciaAPI(transparencia_key)
        self.camara = CamaraAPI()
        self.datajud = DataJudAPI(datajud_key)
        self.ibge = IBGEAPI()
        self.tcu = TCUAPI()

    def perfil_empresa(self, cnpj: str) -> dict:
        """Cria perfil completo de empresa a partir de múltiplas fontes"""
        perfil = {"cnpj": cnpj}

        # Contratos com governo federal
        try:
            perfil["contratos_federais"] = self.transparencia.contratos(cnpj)
        except Exception as e:
            print(f"Erro ao buscar contratos: {e}")
            perfil["contratos_federais"] = []

        # Verificar se está em listas de sanções
        try:
            perfil["sancionada_ceis"] = bool(self.transparencia.ceis(cnpj=cnpj))
        except Exception as e:
            print(f"Erro ao verificar CEIS: {e}")
            perfil["sancionada_ceis"] = False

        return perfil

    def analise_municipio(self, codigo_ibge: str) -> dict:
        """Análise integrada de um município"""
        analise = {"codigo_ibge": codigo_ibge}

        # Dados demográficos do IBGE
        # (implementar consultas SIDRA específicas)

        # Dados fiscais do SICONFI
        # (requer implementação do adapter SICONFI)

        return analise


# =============================================================================
# MAIN - RODAR TODOS OS EXEMPLOS
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("APIs Governamentais Brasileiras - Exemplos de Uso")
    print("Projeto Cidadão.AI")
    print("=" * 60)

    # Atenção: Substitua as chaves de API pelos valores reais

    # exemplo_transparencia()  # Requer API key
    exemplo_camara()
    # exemplo_datajud()  # Usa chave pública
    exemplo_ibge()
    exemplo_tcu()

    print("\n" + "=" * 60)
    print("Para usar o Portal da Transparência:")
    print("1. Acesse: https://portaldatransparencia.gov.br/api-de-dados")
    print("2. Clique em 'Cadastrar Nova Chave'")
    print("3. Insira seu email e aguarde o envio da chave")
    print("=" * 60)
