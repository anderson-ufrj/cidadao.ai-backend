#!/usr/bin/env python3
"""
Test Railway PostgreSQL Connection and Investigations Table
"""
import sys

import psycopg2

# Railway PostgreSQL connection
DATABASE_URL = "postgresql://postgres:***REDACTED-PG-PASSWORD***@centerbeam.proxy.rlwy.net:38094/railway"


def main():
    print("\n" + "=" * 80)
    print("TESTE: Conexão PostgreSQL Railway + Tabela Investigations")
    print("=" * 80)
    print()

    try:
        # Connect
        print("🔌 Conectando ao Railway PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("✅ Conectado!")
        print()

        # Check investigations table
        print("🔍 Verificando tabela investigations...")
        cursor.execute(
            """
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name = 'investigations'
        """
        )
        table_exists = cursor.fetchone()[0]

        if table_exists:
            print("✅ Tabela 'investigations' existe!")
        else:
            print("❌ Tabela 'investigations' NÃO existe!")
            return 1
        print()

        # Get table structure
        print("📋 Estrutura da tabela:")
        cursor.execute(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'investigations'
            ORDER BY ordinal_position
            LIMIT 10
        """
        )
        columns = cursor.fetchall()
        for col_name, col_type, nullable in columns:
            null_str = "NULL" if nullable == "YES" else "NOT NULL"
            print(f"   - {col_name:30} {col_type:20} {null_str}")
        print(f"   ... ({len(columns)} campos mostrados)")
        print()

        # Count records
        print("📊 Contagem de registros:")
        cursor.execute("SELECT COUNT(*) FROM investigations")
        total = cursor.fetchone()[0]
        print(f"   Total: {total} investigações")
        print()

        # Show recent investigations
        if total > 0:
            print("🔍 Últimas 5 investigações:")
            cursor.execute(
                """
                SELECT id, user_id, status, total_records_analyzed, anomalies_found, created_at
                FROM investigations
                ORDER BY created_at DESC
                LIMIT 5
            """
            )
            investigations = cursor.fetchall()
            for inv_id, user_id, status, records, anomalies, created in investigations:
                print(
                    f"   - {inv_id[:8]}... | {user_id[:15]:15} | {status:10} | {records:4} records | {anomalies:2} anomalies | {created}"
                )
            print()

        # Test INSERT (create a test investigation)
        print("🧪 Testando INSERT...")
        test_id = "test-railway-db-00001"
        cursor.execute(
            """
            INSERT INTO investigations (
                id, user_id, session_id, query, data_source, status
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            RETURNING id
        """,
            (
                test_id,
                "test-user-railway",
                "test-session-001",
                "Teste de conexão Railway",
                "test",
                "completed",
            ),
        )

        if cursor.rowcount > 0:
            print(f"✅ INSERT bem-sucedido! ID: {test_id}")
        else:
            print(f"⚠️  Registro já existe (normal se executou antes)")
        conn.commit()
        print()

        # Test SELECT
        print("🧪 Testando SELECT...")
        cursor.execute(
            """
            SELECT id, user_id, query, status
            FROM investigations
            WHERE id = %s
        """,
            (test_id,),
        )
        result = cursor.fetchone()

        if result:
            print(f"✅ SELECT bem-sucedido!")
            print(f"   ID: {result[0]}")
            print(f"   User: {result[1]}")
            print(f"   Query: {result[2]}")
            print(f"   Status: {result[3]}")
        else:
            print(f"❌ SELECT falhou - registro não encontrado")
            return 1
        print()

        # Cleanup test record
        print("🧹 Limpando registro de teste...")
        cursor.execute("DELETE FROM investigations WHERE id = %s", (test_id,))
        conn.commit()
        print(f"✅ Registro de teste removido")
        print()

        cursor.close()
        conn.close()

        print("=" * 80)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 80)
        print()
        print("Conclusão:")
        print("- PostgreSQL Railway está acessível")
        print("- Tabela 'investigations' existe e está funcional")
        print("- INSERT e SELECT funcionando perfeitamente")
        print()
        print("✅ O problema do R$ 0.00 DEVERIA estar resolvido em produção!")
        print()

        return 0

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ TESTE FALHOU!")
        print("=" * 80)
        print()
        print(f"Erro: {e}")
        print()
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
