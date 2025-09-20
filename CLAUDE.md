# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Author**: Anderson Henrique da Silva  
**Last Updated**: 2025-09-20 07:28:07 -03 (São Paulo, Brazil)

## Project Overview

Cidadão.AI Backend is an **enterprise-grade multi-agent AI system** for Brazilian government transparency analysis. It specializes in detecting anomalies, irregular patterns, and potential fraud in public contracts, expenses, and government data using advanced AI techniques including spectral analysis, machine learning, and explainable AI.

### Key Capabilities
- **Anomaly Detection**: Price anomalies, vendor concentration, temporal patterns using Z-score, Isolation Forest, spectral analysis (FFT)
- **Multi-Agent System**: 17 specialized AI agents with Brazilian cultural identities (8 fully operational, 7 in development)
- **Portal da Transparência Integration**: Real data with API key, demo data without
- **Enterprise Security**: JWT authentication, OAuth2, audit logging, rate limiting, circuit breakers
- **Performance**: Cache hit rate >90%, agent response <2s, API latency P95 <200ms, throughput >10k req/s

### Recent Enhancements (Sprint 2-5)
- **Performance Optimizations**: orjson (3x faster JSON), Brotli compression, advanced caching, connection pooling
- **Scalability**: Agent pooling, parallel processing, batch APIs, GraphQL, WebSocket batching
- **Event Architecture**: CQRS pattern, Redis Streams, async task queues, message prioritization
- **Observability**: OpenTelemetry tracing, Prometheus metrics, structured logging, Grafana dashboards
- **Resilience**: Circuit breakers, bulkheads, health checks, SLA/SLO monitoring, chaos engineering

## Commit Guidelines

### Technical Commit Standards
- Technical commits ONLY in international English
- Commit message formats:
  - `feat(module): Short descriptive message`
  - `fix(component): Specific issue resolution`
  - `refactor(area): Improvement without changing functionality`
  - `perf(optimization): Performance enhancement`
  - `test(coverage): Add/update tests`
  - `docs(readme): Documentation update`

### Commit Metadata
- Always use technical commit messages
- Never include:
  - Personal notes
  - Emojis (except standard commit type emojis)
  - Redundant information
- Recommended commit message generation tools:
  - Conventional Commits
  - Commitizen
  - GitHub Copilot CLI

### Approved Commit Patterns
- Commits that explain technical changes precisely
- Clear, concise, and professional language
- Focus on WHAT and WHY of the change
- Include optional scope for better context

## Development Commands

[... rest of the existing content remains unchanged ...]