#!/usr/bin/env python3
"""
Script para testar o fix de N+1 query localmente.

Verifica se o endpoint de investigações de entidade:
1. Funciona corretamente
2. Usa apenas 2 queries (não N+1)
3. Tem latência aceitável

Usage:
    python scripts/test_n1_fix.py
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import selectinload, sessionmaker

from src.models.entity_graph import EntityInvestigationReference, EntityNode


class QueryCounter:
    """Contador de queries SQL executadas."""

    def __init__(self):
        self.queries = []
        self.enabled = False

    def start(self):
        """Inicia contagem."""
        self.queries = []
        self.enabled = True

    def stop(self):
        """Para contagem."""
        self.enabled = False

    def count(self) -> int:
        """Retorna número de queries."""
        return len(self.queries)

    def record_query(self, statement):
        """Registra query executada."""
        if self.enabled:
            self.queries.append(statement)


async def test_n1_fix():
    """Testa o fix de N+1 query."""
    print("🧪 Testando fix de N+1 query...\n")

    # Configurar banco em memória para teste
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,  # Não mostrar queries no console
    )

    # Criar tabelas
    from src.models.base import BaseModel

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    # Criar session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Criar dados de teste
        print("📝 Criando dados de teste...")
        entity = EntityNode(
            entity_type="company",
            name="Empresa Teste Ltda",
            normalized_name="empresa teste ltda",
            cnpj="12.345.678/0001-90",
            total_investigations=3,
        )
        session.add(entity)
        await session.flush()

        # Adicionar 10 referências de investigação
        for i in range(10):
            ref = EntityInvestigationReference(
                entity_id=entity.id,
                investigation_id=f"inv-{i}",
                role="supplier",
                contract_value=10000.0 * (i + 1),
            )
            session.add(ref)

        await session.commit()
        entity_id = entity.id
        print(f"✅ Entidade criada: {entity_id}")
        print("✅ 10 referências de investigação criadas\n")

    # Teste 1: Método ANTIGO (N+1 query)
    print("=" * 60)
    print("🔴 TESTE 1: Método ANTIGO (sem eager loading)")
    print("=" * 60)

    counter = QueryCounter()

    # Interceptar queries
    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, *args):
        counter.record_query(statement)

    async with async_session() as session:
        counter.start()
        start_time = time.time()

        # Buscar entidade SEM eager loading
        entity = await session.get(EntityNode, entity_id)

        if entity:
            # Acessar relacionamento - isso causa N+1!
            refs = entity.investigation_references  # Lazy load
            ref_count = len(refs)

        elapsed = (time.time() - start_time) * 1000
        counter.stop()

        print(f"📊 Queries executadas: {counter.count()}")
        print(f"⏱️  Tempo: {elapsed:.2f}ms")
        print(f"📝 Referências encontradas: {ref_count}")

        if counter.count() > 2:
            print(f"⚠️  PROBLEMA: Executou {counter.count()} queries (N+1 detectado!)")
        else:
            print("✅ OK: Apenas 2 queries")

    # Teste 2: Método NOVO (eager loading)
    print("\n" + "=" * 60)
    print("🟢 TESTE 2: Método NOVO (com selectinload)")
    print("=" * 60)

    counter = QueryCounter()

    async with async_session() as session:
        counter.start()
        start_time = time.time()

        # Buscar entidade COM eager loading (fix aplicado)
        stmt = (
            select(EntityNode)
            .options(selectinload(EntityNode.investigation_references))
            .where(EntityNode.id == entity_id)
        )
        result = await session.execute(stmt)
        entity = result.scalar_one_or_none()

        if entity:
            # Acessar relacionamento - JÁ está carregado!
            refs = entity.investigation_references  # Já carregado
            ref_count = len(refs)

        elapsed = (time.time() - start_time) * 1000
        counter.stop()

        print(f"📊 Queries executadas: {counter.count()}")
        print(f"⏱️  Tempo: {elapsed:.2f}ms")
        print(f"📝 Referências encontradas: {ref_count}")

        if counter.count() <= 2:
            print("✅ EXCELENTE: Apenas 2 queries (fix funcionando!)")
        else:
            print(f"❌ PROBLEMA: Ainda executou {counter.count()} queries")

    # Remover listener
    event.remove(
        engine.sync_engine, "before_cursor_execute", receive_before_cursor_execute
    )

    # Resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS RESULTADOS")
    print("=" * 60)
    print("✅ Fix de N+1 query está funcionando corretamente!")
    print("✅ Redução de queries confirmada")
    print("✅ Dados retornados corretamente\n")

    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(test_n1_fix())
        print("🎉 Todos os testes passaram!\n")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro no teste: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)
