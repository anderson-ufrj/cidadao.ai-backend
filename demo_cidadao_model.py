#!/usr/bin/env python3
"""
🤖 CidadãoGPT - Demonstração Interativa

Script de demonstração do modelo especializado em transparência pública.
Inspirado no Kimi K2, mas focado em análise governamental brasileira.
"""

import asyncio
import json
import sys
from pathlib import Path
import logging
from typing import Dict, Any
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Importar componentes do modelo
try:
    from src.ml.cidadao_model import create_cidadao_model, CidadaoGPTForTransparency
    from src.ml.model_api import CidadaoGPTManager, TransparencyAnalysisRequest
    from src.ml.transparency_benchmark import run_transparency_benchmark, BenchmarkConfig
    from src.ml.training_pipeline import create_training_pipeline, TrainingConfig
    from src.ml.data_pipeline import run_data_pipeline, DataPipelineConfig
except ImportError as e:
    logger.error(f"❌ Erro ao importar módulos: {e}")
    logger.error("💡 Certifique-se de que está no diretório raiz do projeto")
    sys.exit(1)


class CidadaoGPTDemo:
    """Demonstração interativa do CidadãoGPT"""
    
    def __init__(self):
        self.model = None
        self.manager = None
        self.demo_data = self._load_demo_data()
        
    def _load_demo_data(self) -> Dict[str, Any]:
        """Carregar dados de demonstração"""
        
        return {
            "contratos_exemplo": [
                {
                    "id": "normal_001",
                    "titulo": "📋 Contrato Normal - Aquisição de Material de Escritório",
                    "texto": """Pregão eletrônico nº 001/2024 para aquisição de material de escritório 
                    no valor de R$ 75.000,00. Fornecedor: Papelaria Central LTDA, CNPJ regular, 
                    processo licitatório conduzido conforme Lei 14.133/2021, com ampla participação 
                    e documentação completa.""",
                    "esperado": "Normal - Baixo Risco"
                },
                {
                    "id": "suspeito_001", 
                    "titulo": "⚠️ Contrato Suspeito - Obra com Prazo Apertado",
                    "texto": """Contratação de obra de pavimentação no valor de R$ 5.000.000,00 
                    com prazo de licitação reduzido para 5 dias. Apenas duas empresas participaram, 
                    sendo uma delas recém-constituída. Processo tem justificativa de urgência 
                    questionável.""",
                    "esperado": "Suspeito - Médio Risco"
                },
                {
                    "id": "anomalo_001",
                    "titulo": "🚨 Contrato Anômalo - Dispensa Irregular",
                    "texto": """Contrato emergencial de R$ 25.000.000,00 para 'consultoria em gestão' 
                    dispensando licitação. Empresa contratada não possui funcionários registrados 
                    e pertence ao cônjuge do secretário responsável. Pagamento integral antecipado 
                    sem garantias.""",
                    "esperado": "Anômalo - Alto Risco"
                },
                {
                    "id": "complexo_001",
                    "titulo": "🏗️ Contrato Complexo - Construção Hospitalar",
                    "texto": """Concorrência pública para construção de hospital no valor de 
                    R$ 150.000.000,00. Projeto básico incompleto, histórico de aditivos contratuais 
                    excessivos em obras similares do mesmo órgão. Empresa vencedora tem capacidade 
                    técnica questionável para projeto desta magnitude.""",
                    "esperado": "Alto Risco Financeiro"
                }
            ],
            
            "cenarios_chat": [
                {
                    "pergunta": "O que é um superfaturamento e como identificá-lo?",
                    "contexto": "Educacional"
                },
                {
                    "pergunta": "Analise este contrato: Aquisição de equipamentos por R$ 10 milhões sem licitação.",
                    "contexto": "Análise direta"
                },
                {
                    "pergunta": "Quais são os principais indicadores de corrupção em licitações?",
                    "contexto": "Consultoria"
                }
            ]
        }

    async def run_demo(self):
        """Executar demonstração completa"""
        
        print("\n" + "="*70)
        print("🤖 CIDADÃOGPT - DEMONSTRAÇÃO INTERATIVA")
        print("Modelo de IA Especializado em Transparência Pública Brasileira")
        print("Inspirado no Kimi K2, otimizado para análise governamental")
        print("="*70)
        
        await self._init_model()
        
        while True:
            try:
                choice = self._show_main_menu()
                
                if choice == "1":
                    await self._demo_analysis()
                elif choice == "2":
                    await self._demo_chat()
                elif choice == "3":
                    await self._demo_batch_analysis()
                elif choice == "4":
                    await self._demo_benchmark()
                elif choice == "5":
                    await self._demo_training()
                elif choice == "6":
                    self._show_model_info()
                elif choice == "0":
                    print("\n👋 Obrigado por usar o CidadãoGPT!")
                    break
                else:
                    print("❌ Opção inválida. Tente novamente.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Demonstração interrompida. Até logo!")
                break
            except Exception as e:
                logger.error(f"❌ Erro na demonstração: {e}")
                print(f"❌ Erro: {e}")

    async def _init_model(self):
        """Inicializar modelo"""
        
        print("\n🔄 Inicializando CidadãoGPT...")
        
        try:
            # Criar modelo
            self.model = create_cidadao_model(
                specialized_tasks=["all"],
                model_size="medium"
            )
            
            # Criar manager
            self.manager = CidadaoGPTManager()
            self.manager.model = self.model
            self.manager.loaded = True
            
            # Contar parâmetros
            total_params = sum(p.numel() for p in self.model.parameters())
            
            print(f"✅ Modelo carregado com sucesso!")
            print(f"📊 Parâmetros: {total_params:,}")
            print(f"🎯 Tarefas especializadas: Anomalias, Risco Financeiro, Conformidade Legal")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo: {e}")
            print(f"❌ Erro: {e}")
            sys.exit(1)

    def _show_main_menu(self) -> str:
        """Mostrar menu principal"""
        
        print("\n" + "="*50)
        print("📋 MENU PRINCIPAL")
        print("="*50)
        print("1. 🔍 Demonstração de Análise de Transparência")
        print("2. 💬 Chat Interativo com CidadãoGPT") 
        print("3. 📊 Análise em Lote")
        print("4. 🏆 Benchmark de Performance")
        print("5. 🎓 Demonstração de Treinamento")
        print("6. ℹ️ Informações do Modelo")
        print("0. 🚪 Sair")
        print("="*50)
        
        return input("🤖 Escolha uma opção: ").strip()

    async def _demo_analysis(self):
        """Demonstração de análise de transparência"""
        
        print("\n" + "="*60)
        print("🔍 DEMONSTRAÇÃO - ANÁLISE DE TRANSPARÊNCIA")
        print("="*60)
        
        print("\n📋 Contratos disponíveis para análise:")
        
        for i, contrato in enumerate(self.demo_data["contratos_exemplo"], 1):
            print(f"{i}. {contrato['titulo']}")
        
        print("5. ✏️ Inserir texto personalizado")
        
        choice = input("\n🤖 Escolha um contrato (1-5): ").strip()
        
        try:
            if choice in ["1", "2", "3", "4"]:
                contrato = self.demo_data["contratos_exemplo"][int(choice) - 1]
                texto = contrato["texto"]
                esperado = contrato["esperado"]
                
                print(f"\n📄 Analisando: {contrato['titulo']}")
                print(f"📝 Resultado esperado: {esperado}")
                
            elif choice == "5":
                texto = input("\n📝 Digite o texto para análise: ").strip()
                if not texto:
                    print("❌ Texto vazio. Voltando ao menu.")
                    return
                esperado = "Não definido"
                
            else:
                print("❌ Opção inválida.")
                return
            
            # Executar análise
            print("\n🔄 Executando análise...")
            start_time = time.time()
            
            request = TransparencyAnalysisRequest(
                text=texto,
                analysis_type="complete",
                include_explanation=True
            )
            
            result = await self.manager.analyze_transparency(request)
            
            processing_time = time.time() - start_time
            
            # Mostrar resultados
            self._display_analysis_results(result, processing_time, esperado)
            
        except Exception as e:
            logger.error(f"❌ Erro na análise: {e}")
            print(f"❌ Erro: {e}")

    def _display_analysis_results(self, result, processing_time: float, esperado: str):
        """Exibir resultados da análise"""
        
        print("\n" + "="*60)
        print("📊 RESULTADOS DA ANÁLISE")
        print("="*60)
        
        # Resumo executivo
        summary = result.executive_summary
        print(f"\n🎯 RESUMO EXECUTIVO")
        print(f"   • Nível de Risco: {summary['overall_risk']}")
        print(f"   • Alerta: {summary['alert_level']}")
        print(f"   • Confiança Geral: {result.confidence:.1%}")
        print(f"   • Tempo de Processamento: {processing_time:.2f}s")
        print(f"   • Resultado Esperado: {esperado}")
        
        # Principais descobertas
        if summary.get("main_findings"):
            print(f"\n🔍 PRINCIPAIS DESCOBERTAS:")
            for finding in summary["main_findings"]:
                print(f"   • {finding}")
        
        # Detecção de anomalias
        if result.anomaly_detection:
            anomaly_data = result.anomaly_detection
            print(f"\n🚨 DETECÇÃO DE ANOMALIAS:")
            print(f"   • Amostras analisadas: {anomaly_data['summary']['total_samples']}")
            print(f"   • Anomalias encontradas: {anomaly_data['summary']['anomalous_count']}")
            print(f"   • Casos suspeitos: {anomaly_data['summary']['suspicious_count']}")
            
            if anomaly_data["predictions"]:
                pred = anomaly_data["predictions"][0]
                print(f"   • Classificação: {pred['anomaly_type']}")
                print(f"   • Confiança: {pred['confidence']:.1%}")
        
        # Análise financeira
        if result.financial_analysis:
            financial_data = result.financial_analysis
            print(f"\n💰 ANÁLISE FINANCEIRA:")
            print(f"   • Contratos de alto risco: {financial_data['summary']['high_risk_count']}")
            
            if financial_data["predictions"]:
                pred = financial_data["predictions"][0]
                print(f"   • Nível de risco: {pred['risk_level']}")
                print(f"   • Valor estimado em risco: R$ {pred.get('estimated_value', 0):,.2f}")
        
        # Conformidade legal
        if result.legal_compliance:
            legal_data = result.legal_compliance
            print(f"\n⚖️ CONFORMIDADE LEGAL:")
            compliance_rate = legal_data['summary']['compliance_rate']
            print(f"   • Taxa de conformidade: {compliance_rate:.1%}")
            
            if legal_data["predictions"]:
                pred = legal_data["predictions"][0]
                status = "Conforme" if pred["is_compliant"] else "Não Conforme"
                print(f"   • Status: {status}")
                print(f"   • Confiança: {pred['compliance_confidence']:.1%}")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        for rec in result.recommendations:
            print(f"   • {rec}")
        
        input("\n⏎ Pressione Enter para continuar...")

    async def _demo_chat(self):
        """Demonstração do chat interativo"""
        
        print("\n" + "="*60)
        print("💬 CHAT INTERATIVO COM CIDADÃOGPT")
        print("="*60)
        print("💡 Dica: Digite 'sair' para voltar ao menu principal")
        print("💡 Experimente perguntas sobre transparência, contratos e corrupção")
        
        # Mostrar exemplos
        print("\n📝 Exemplos de perguntas:")
        for i, cenario in enumerate(self.demo_data["cenarios_chat"], 1):
            print(f"{i}. {cenario['pergunta']}")
        
        print("\n" + "="*60)
        
        messages_history = []
        
        while True:
            user_input = input("\n🧑 Você: ").strip()
            
            if user_input.lower() in ['sair', 'exit', 'quit']:
                break
                
            if not user_input:
                continue
            
            messages_history.append({"role": "user", "content": user_input})
            
            try:
                print("🤖 CidadãoGPT: 🔄 Pensando...")
                
                from src.ml.model_api import ChatRequest
                
                chat_request = ChatRequest(
                    messages=messages_history,
                    temperature=0.6,
                    max_tokens=512
                )
                
                response = await self.manager.chat_completion(chat_request)
                
                print(f"\n🤖 CidadãoGPT: {response.message}")
                
                if response.tools_used:
                    print(f"🔧 Ferramentas utilizadas: {', '.join(response.tools_used)}")
                
                if response.sources:
                    print(f"📚 Fontes: {', '.join(response.sources)}")
                
                print(f"📊 Confiança: {response.confidence:.1%}")
                
                messages_history.append({"role": "assistant", "content": response.message})
                
            except Exception as e:
                logger.error(f"❌ Erro no chat: {e}")
                print(f"❌ Erro: {e}")

    async def _demo_batch_analysis(self):
        """Demonstração de análise em lote"""
        
        print("\n" + "="*60)
        print("📊 ANÁLISE EM LOTE")
        print("="*60)
        
        # Preparar textos para análise em lote
        textos_lote = [
            "Pregão eletrônico para material de limpeza no valor de R$ 80.000,00",
            "Contrato emergencial sem licitação para obras no valor de R$ 15.000.000,00",
            "Convênio de cooperação técnica com universidade no valor de R$ 500.000,00",
            "Dispensa de licitação para consultoria com empresa de fachada"
        ]
        
        print("📋 Analisando 4 contratos em lote...")
        
        try:
            from src.ml.model_api import BatchAnalysisRequest
            
            batch_request = BatchAnalysisRequest(
                texts=textos_lote,
                analysis_type="complete",
                format="json"
            )
            
            start_time = time.time()
            results = await self.manager.batch_analyze(batch_request)
            total_time = time.time() - start_time
            
            print(f"\n✅ Análise concluída em {total_time:.2f}s")
            print(f"📊 Velocidade: {len(textos_lote)/total_time:.1f} contratos/segundo")
            
            # Mostrar resultados resumidos
            print("\n📋 RESULTADOS RESUMIDOS:")
            print("-" * 60)
            
            for i, result in enumerate(results, 1):
                summary = result.executive_summary
                print(f"{i}. Risco: {summary['overall_risk']:10} | "
                      f"Alerta: {summary['alert_level']:8} | "
                      f"Confiança: {result.confidence:.1%}")
                print(f"   Texto: {textos_lote[i-1][:50]}...")
                
                if result.recommendations:
                    print(f"   Rec: {result.recommendations[0][:60]}...")
                print()
            
        except Exception as e:
            logger.error(f"❌ Erro na análise em lote: {e}")
            print(f"❌ Erro: {e}")
        
        input("⏎ Pressione Enter para continuar...")

    async def _demo_benchmark(self):
        """Demonstração do benchmark"""
        
        print("\n" + "="*60)
        print("🏆 BENCHMARK DE PERFORMANCE")
        print("="*60)
        
        print("📊 Executando TransparenciaBench-BR...")
        print("⚠️ Nota: Usando dados sintéticos para demonstração")
        
        try:
            config = BenchmarkConfig(
                max_samples_per_task=20,  # Reduzido para demo
                output_dir="./demo_benchmark_results",
                generate_plots=False  # Desabilitar plots para demo
            )
            
            start_time = time.time()
            results = await run_transparency_benchmark(config=config)
            total_time = time.time() - start_time
            
            print(f"\n✅ Benchmark concluído em {total_time:.1f}s")
            
            # Mostrar resultados principais
            print("\n🎯 RESULTADOS PRINCIPAIS:")
            print("-" * 40)
            print(f"📊 Score de Transparência: {results.transparency_score:.1%}")
            print(f"🎯 F1 Score Geral: {results.overall_f1:.1%}")
            print(f"📈 Accuracy Geral: {results.overall_accuracy:.1%}")
            print(f"⏱️ Tempo Médio: {results.average_processing_time:.3f}s")
            
            print("\n🔍 PERFORMANCE POR TAREFA:")
            print("-" * 40)
            for task_name, metrics in results.task_metrics.items():
                task_display = task_name.replace('_', ' ').title()
                print(f"{task_display:20} | F1: {metrics.f1_score:.1%} | Acc: {metrics.accuracy:.1%}")
            
            print("\n🏅 CAPACIDADES ESPECIALIZADAS:")
            print("-" * 40)
            print(f"🚨 Detecção de Corrupção: {results.corruption_detection_ability:.1%}")
            print(f"⚖️ Compreensão Legal: {results.legal_compliance_understanding:.1%}")
            print(f"💰 Avaliação Financeira: {results.financial_risk_assessment:.1%}")
            
            if results.compared_to_baselines:
                print("\n📈 COMPARAÇÃO COM BASELINES:")
                print("-" * 40)
                for baseline, comparison in results.compared_to_baselines.items():
                    improvement = comparison["improvement_percent"]
                    status = "📈" if improvement > 0 else "📉"
                    print(f"{baseline:20} | {status} {improvement:+.1f}%")
            
        except Exception as e:
            logger.error(f"❌ Erro no benchmark: {e}")
            print(f"❌ Erro: {e}")
        
        input("\n⏎ Pressione Enter para continuar...")

    async def _demo_training(self):
        """Demonstração do processo de treinamento"""
        
        print("\n" + "="*60)
        print("🎓 DEMONSTRAÇÃO - PIPELINE DE TREINAMENTO")
        print("="*60)
        print("⚠️ Nota: Esta é uma demonstração dos componentes de treinamento")
        print("   O treinamento real requer dados e recursos computacionais significativos")
        
        print("\n🔧 Componentes do Pipeline:")
        print("1. 📊 Coleta de dados do Portal da Transparência")
        print("2. 🔄 Processamento e anotação automática") 
        print("3. 🎯 Treinamento multi-tarefa especializado")
        print("4. 📈 Avaliação e benchmark")
        
        choice = input("\nDeseja ver a configuração do pipeline? (s/n): ").strip().lower()
        
        if choice == 's':
            print("\n📋 CONFIGURAÇÃO DE TREINAMENTO:")
            print("-" * 40)
            
            # Mostrar configuração de dados
            data_config = DataPipelineConfig(
                max_samples_per_type=1000,
                balance_classes=True,
                output_dir="./data/processed"
            )
            
            print("🗂️ Pipeline de Dados:")
            print(f"   • Amostras por tipo: {data_config.max_samples_per_type:,}")
            print(f"   • Balanceamento: {'Sim' if data_config.balance_classes else 'Não'}")
            print(f"   • Split treino/val/teste: {data_config.train_split:.1%}/{data_config.val_split:.1%}/{data_config.test_split:.1%}")
            
            # Mostrar configuração de treinamento
            train_config = TrainingConfig(
                learning_rate=2e-5,
                batch_size=16,
                num_epochs=10,
                specialized_tasks=["all"]
            )
            
            print("\n🎓 Configuração de Treinamento:")
            print(f"   • Learning rate: {train_config.learning_rate}")
            print(f"   • Batch size: {train_config.batch_size}")
            print(f"   • Épocas: {train_config.num_epochs}")
            print(f"   • Tarefas: {', '.join(train_config.specialized_tasks)}")
            
            print("\n💡 Para executar treinamento real:")
            print("   1. Configure dados reais no Portal da Transparência")
            print("   2. Execute: python -m src.ml.training_pipeline")
            print("   3. Monitore com: tensorboard --logdir ./models/logs")
        
        input("\n⏎ Pressione Enter para continuar...")

    def _show_model_info(self):
        """Mostrar informações do modelo"""
        
        print("\n" + "="*60)
        print("ℹ️ INFORMAÇÕES DO MODELO")
        print("="*60)
        
        if self.model:
            total_params = sum(p.numel() for p in self.model.parameters())
            trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
            
            print("🤖 CIDADÃOGPT - ESPECIFICAÇÕES TÉCNICAS")
            print("-" * 40)
            print(f"📊 Parâmetros totais: {total_params:,}")
            print(f"🎯 Parâmetros treináveis: {trainable_params:,}")
            print(f"💾 Tamanho do modelo: ~{total_params * 4 / 1024**3:.1f} GB (FP32)")
            
            print("\n🔧 ARQUITETURA:")
            print(f"   • Transformer base: {self.model.config.num_hidden_layers} camadas")
            print(f"   • Hidden size: {self.model.config.hidden_size}")
            print(f"   • Attention heads: {self.model.config.num_attention_heads}")
            print(f"   • Context length: 8K tokens")
            
            print("\n🎯 ESPECIALIZAÇÕES:")
            config = self.model.config
            if config.enable_anomaly_detection:
                print("   • ✅ Detecção de anomalias")
            if config.enable_financial_analysis:
                print("   • ✅ Análise de risco financeiro")
            if config.enable_legal_reasoning:
                print("   • ✅ Raciocínio jurídico")
            
            print("\n📊 ESTATÍSTICAS DE USO:")
            stats = self.manager.usage_stats
            print(f"   • Requisições totais: {stats['total_requests']}")
            print(f"   • Detecções de anomalia: {stats['anomaly_detections']}")
            print(f"   • Análises financeiras: {stats['financial_analyses']}")
            print(f"   • Verificações legais: {stats['legal_checks']}")
            print(f"   • Tempo médio: {stats['average_processing_time']:.3f}s")
        
        print("\n💡 COMPARAÇÃO COM OUTROS MODELOS:")
        print("-" * 40)
        print("CidadãoGPT vs GPT-4:")
        print("   • ✅ Especialização em transparência pública")
        print("   • ✅ Compreensão de legislação brasileira")
        print("   • ✅ Detecção específica de corrupção")
        print("   • ✅ Explicações em português")
        print("   • ⚡ Processamento otimizado para contratos")
        
        print("\n🌐 RECURSOS ONLINE:")
        print("   • 📚 Documentação: https://github.com/anderson-ufrj/cidadao.ai")
        print("   • 🤗 Hugging Face: https://huggingface.co/neural-thinker/cidadao-ai")
        print("   • 🎮 Demo Web: Disponível no app.py")
        
        input("\n⏎ Pressione Enter para continuar...")

    def _show_credits(self):
        """Mostrar créditos"""
        
        print("\n" + "="*60)
        print("👨‍💻 CRÉDITOS E INFORMAÇÕES")
        print("="*60)
        print("🤖 CidadãoGPT - Modelo de IA para Transparência Pública")
        print("💡 Inspirado no Kimi K2 (Moonshot AI)")
        print("🇧🇷 Especializado para dados governamentais brasileiros")
        print()
        print("👨‍💻 Desenvolvedor: Anderson Henrique da Silva")
        print("🤖 Assistência IA: Claude Code (Anthropic)")
        print("📊 Dados: Portal da Transparência (Governo Federal)")
        print()
        print("📄 Licença: MIT License")
        print("🌐 GitHub: https://github.com/anderson-ufrj/cidadao.ai")


async def main():
    """Função principal"""
    
    try:
        demo = CidadaoGPTDemo()
        await demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demonstração interrompida. Até logo!")
    except Exception as e:
        logger.error(f"❌ Erro na demonstração: {e}")
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    print("🤖 Iniciando demonstração do CidadãoGPT...")
    asyncio.run(main())