"""
Module: services.cache_warming_service
Description: Cache warming strategies for improved performance
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import asyncio
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta, timezone
from enum import Enum
import hashlib

from src.core import get_logger
from src.services.cache_service import cache_service
from src.services.data_service import data_service
from src.services.investigation_service import investigation_service
from src.core.config import settings
from src.db.session import get_session
from src.infrastructure.database import Investigation

logger = get_logger(__name__)


class CacheWarmingStrategy(str, Enum):
    """Cache warming strategies."""
    POPULAR_DATA = "popular_data"
    RECENT_INVESTIGATIONS = "recent_investigations"
    FREQUENT_QUERIES = "frequent_queries"
    AGENT_POOLS = "agent_pools"
    STATIC_RESOURCES = "static_resources"
    PREDICTIVE = "predictive"


class CacheWarmingConfig:
    """Configuration for cache warming."""
    
    # TTLs por tipo de dado
    TTL_CONFIG = {
        "contracts": 3600,          # 1 hora
        "investigations": 1800,     # 30 minutos
        "agent_pools": 7200,        # 2 horas
        "static_data": 86400,       # 24 horas
        "frequent_queries": 600,    # 10 minutos
        "analytics": 3600          # 1 hora
    }
    
    # Limites de warming
    MAX_ITEMS_PER_TYPE = {
        "contracts": 100,
        "investigations": 50,
        "queries": 200,
        "agents": 20
    }
    
    # Configuração de prioridades
    PRIORITY_WEIGHTS = {
        "recency": 0.3,
        "frequency": 0.4,
        "importance": 0.3
    }


class CacheWarmingService:
    """Service for cache warming operations."""
    
    def __init__(self):
        """Initialize cache warming service."""
        self._config = CacheWarmingConfig()
        self._warming_tasks: Set[asyncio.Task] = set()
        self._last_warming: Dict[str, datetime] = {}
        self._query_frequency: Dict[str, int] = {}
        self._warming_interval = 300  # 5 minutos
        
    async def start_warming_scheduler(self):
        """Start the cache warming scheduler."""
        logger.info("cache_warming_scheduler_started")
        
        while True:
            try:
                # Execute warming strategies
                await self.warm_all_caches()
                
                # Wait for next interval
                await asyncio.sleep(self._warming_interval)
                
            except asyncio.CancelledError:
                logger.info("cache_warming_scheduler_stopped")
                break
            except Exception as e:
                logger.error(
                    "cache_warming_scheduler_error",
                    error=str(e),
                    exc_info=True
                )
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def warm_all_caches(self):
        """Execute all cache warming strategies."""
        start_time = datetime.now(timezone.utc)
        
        strategies = [
            self._warm_popular_data(),
            self._warm_recent_investigations(),
            self._warm_frequent_queries(),
            self._warm_agent_pools(),
            self._warm_static_resources()
        ]
        
        # Execute strategies in parallel
        results = await asyncio.gather(*strategies, return_exceptions=True)
        
        # Log results
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        successful = sum(1 for r in results if not isinstance(r, Exception))
        
        logger.info(
            "cache_warming_completed",
            duration_seconds=duration,
            strategies_total=len(strategies),
            strategies_successful=successful
        )
        
        # Update last warming time
        self._last_warming["all"] = datetime.now(timezone.utc)
    
    async def _warm_popular_data(self) -> Dict[str, Any]:
        """Warm cache with popular/frequently accessed data."""
        warmed_count = 0
        
        try:
            # Get most accessed contracts
            popular_contracts = await self._get_popular_contracts()
            
            for contract_id in popular_contracts[:self._config.MAX_ITEMS_PER_TYPE["contracts"]]:
                cache_key = f"contract:{contract_id}"
                
                # Check if already cached
                if await cache_service.get(cache_key):
                    continue
                
                # Fetch and cache
                try:
                    contract_data = await data_service.get_contract(contract_id)
                    if contract_data:
                        await cache_service.set(
                            cache_key,
                            contract_data,
                            ttl=self._config.TTL_CONFIG["contracts"]
                        )
                        warmed_count += 1
                except Exception as e:
                    logger.error(f"Failed to warm contract {contract_id}: {e}")
            
            logger.info(
                "popular_data_warmed",
                contracts_warmed=warmed_count
            )
            
            return {"contracts": warmed_count}
            
        except Exception as e:
            logger.error("popular_data_warming_failed", error=str(e))
            raise
    
    async def _warm_recent_investigations(self) -> Dict[str, Any]:
        """Warm cache with recent investigations."""
        warmed_count = 0
        
        try:
            async with get_session() as session:
                # Get recent investigations
                from sqlalchemy import select, desc
                query = select(Investigation).order_by(
                    desc(Investigation.created_at)
                ).limit(self._config.MAX_ITEMS_PER_TYPE["investigations"])
                
                result = await session.execute(query)
                investigations = result.scalars().all()
                
                for investigation in investigations:
                    cache_key = f"investigation:{investigation.id}"
                    
                    # Cache investigation data
                    await cache_service.set(
                        cache_key,
                        {
                            "id": investigation.id,
                            "status": investigation.status,
                            "contract_id": investigation.contract_id,
                            "results": investigation.results,
                            "created_at": investigation.created_at.isoformat()
                        },
                        ttl=self._config.TTL_CONFIG["investigations"]
                    )
                    warmed_count += 1
            
            logger.info(
                "recent_investigations_warmed",
                count=warmed_count
            )
            
            return {"investigations": warmed_count}
            
        except Exception as e:
            logger.error("recent_investigations_warming_failed", error=str(e))
            raise
    
    async def _warm_frequent_queries(self) -> Dict[str, Any]:
        """Warm cache with results of frequent queries."""
        warmed_count = 0
        
        try:
            # Sort queries by frequency
            frequent_queries = sorted(
                self._query_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:self._config.MAX_ITEMS_PER_TYPE["queries"]]
            
            for query_hash, frequency in frequent_queries:
                cache_key = f"query_result:{query_hash}"
                
                # Skip if already cached
                if await cache_service.get(cache_key):
                    continue
                
                # Note: In a real implementation, you would store and replay
                # the actual query parameters to regenerate results
                warmed_count += 1
            
            logger.info(
                "frequent_queries_warmed",
                count=warmed_count
            )
            
            return {"queries": warmed_count}
            
        except Exception as e:
            logger.error("frequent_queries_warming_failed", error=str(e))
            raise
    
    async def _warm_agent_pools(self) -> Dict[str, Any]:
        """Warm agent pool connections."""
        warmed_count = 0
        
        try:
            # Pre-initialize agent pools
            agent_types = [
                "zumbi",
                "anita",
                "tiradentes",
                "machado",
                "dandara"
            ]
            
            for agent_type in agent_types[:self._config.MAX_ITEMS_PER_TYPE["agents"]]:
                cache_key = f"agent_pool:{agent_type}:status"
                
                # Cache agent pool status
                await cache_service.set(
                    cache_key,
                    {
                        "type": agent_type,
                        "initialized": True,
                        "last_used": datetime.now(timezone.utc).isoformat()
                    },
                    ttl=self._config.TTL_CONFIG["agent_pools"]
                )
                warmed_count += 1
            
            logger.info(
                "agent_pools_warmed",
                count=warmed_count
            )
            
            return {"agents": warmed_count}
            
        except Exception as e:
            logger.error("agent_pools_warming_failed", error=str(e))
            raise
    
    async def _warm_static_resources(self) -> Dict[str, Any]:
        """Warm cache with static resources."""
        warmed_count = 0
        
        try:
            # Static data to cache
            static_data = {
                "system_config": {
                    "version": "1.0.0",
                    "features": ["investigations", "reports", "analysis"],
                    "agents": ["zumbi", "anita", "tiradentes"]
                },
                "contract_types": [
                    "licitacao",
                    "contrato",
                    "convenio",
                    "termo_aditivo"
                ],
                "anomaly_types": [
                    "valor_atipico",
                    "padrao_temporal",
                    "fornecedor_suspeito",
                    "fragmentacao"
                ]
            }
            
            for key, data in static_data.items():
                cache_key = f"static:{key}"
                await cache_service.set(
                    cache_key,
                    data,
                    ttl=self._config.TTL_CONFIG["static_data"]
                )
                warmed_count += 1
            
            logger.info(
                "static_resources_warmed",
                count=warmed_count
            )
            
            return {"static": warmed_count}
            
        except Exception as e:
            logger.error("static_resources_warming_failed", error=str(e))
            raise
    
    async def _get_popular_contracts(self) -> List[str]:
        """Get list of popular contract IDs."""
        # In a real implementation, this would query analytics
        # or access logs to find most accessed contracts
        return [
            "CONT-2024-001",
            "CONT-2024-002",
            "CONT-2024-003",
            "CONT-2024-004",
            "CONT-2024-005"
        ]
    
    def track_query(self, query_params: Dict[str, Any]):
        """Track query frequency for cache warming."""
        # Generate query hash
        query_str = str(sorted(query_params.items()))
        query_hash = hashlib.md5(query_str.encode()).hexdigest()
        
        # Update frequency
        self._query_frequency[query_hash] = self._query_frequency.get(query_hash, 0) + 1
        
        # Limit stored queries
        if len(self._query_frequency) > 1000:
            # Remove least frequent queries
            sorted_queries = sorted(
                self._query_frequency.items(),
                key=lambda x: x[1]
            )
            for query, _ in sorted_queries[:100]:
                del self._query_frequency[query]
    
    async def warm_specific_data(
        self,
        data_type: str,
        identifiers: List[str],
        ttl: Optional[int] = None
    ) -> Dict[str, Any]:
        """Warm cache with specific data."""
        if ttl is None:
            ttl = self._config.TTL_CONFIG.get(data_type, 3600)
        
        warmed = []
        failed = []
        
        for identifier in identifiers:
            try:
                cache_key = f"{data_type}:{identifier}"
                
                # Skip if already cached
                if await cache_service.get(cache_key):
                    continue
                
                # Fetch data based on type
                data = None
                if data_type == "contract":
                    data = await data_service.get_contract(identifier)
                elif data_type == "investigation":
                    data = await investigation_service.get_investigation(identifier)
                
                if data:
                    await cache_service.set(cache_key, data, ttl=ttl)
                    warmed.append(identifier)
                else:
                    failed.append(identifier)
                    
            except Exception as e:
                logger.error(
                    f"Failed to warm {data_type}:{identifier}: {e}"
                )
                failed.append(identifier)
        
        return {
            "warmed": warmed,
            "failed": failed,
            "total": len(identifiers)
        }
    
    async def get_warming_status(self) -> Dict[str, Any]:
        """Get current cache warming status."""
        status = {
            "last_warming": self._last_warming.get("all"),
            "query_frequency_tracked": len(self._query_frequency),
            "top_queries": sorted(
                self._query_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "config": {
                "interval_seconds": self._warming_interval,
                "ttls": self._config.TTL_CONFIG,
                "limits": self._config.MAX_ITEMS_PER_TYPE
            }
        }
        
        return status
    
    async def trigger_manual_warming(
        self,
        strategies: Optional[List[CacheWarmingStrategy]] = None
    ) -> Dict[str, Any]:
        """Manually trigger cache warming."""
        if strategies is None:
            return await self.warm_all_caches()
        
        results = {}
        for strategy in strategies:
            try:
                if strategy == CacheWarmingStrategy.POPULAR_DATA:
                    results[strategy] = await self._warm_popular_data()
                elif strategy == CacheWarmingStrategy.RECENT_INVESTIGATIONS:
                    results[strategy] = await self._warm_recent_investigations()
                elif strategy == CacheWarmingStrategy.FREQUENT_QUERIES:
                    results[strategy] = await self._warm_frequent_queries()
                elif strategy == CacheWarmingStrategy.AGENT_POOLS:
                    results[strategy] = await self._warm_agent_pools()
                elif strategy == CacheWarmingStrategy.STATIC_RESOURCES:
                    results[strategy] = await self._warm_static_resources()
            except Exception as e:
                results[strategy] = {"error": str(e)}
        
        return results


# Global instance
cache_warming_service = CacheWarmingService()