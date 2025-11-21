"""
Portal da Transparência Service Wrapper
Redirects to improved implementation while maintaining backward compatibility
"""

from src.services.portal_transparencia_service_improved import (
    ImprovedPortalTransparenciaService,
    get_improved_portal_service,
)

# For backward compatibility, alias the improved service
PortalTransparenciaService = ImprovedPortalTransparenciaService

# Create singleton instance (works without cache if Redis unavailable)
portal_transparencia = get_improved_portal_service()

__all__ = ["PortalTransparenciaService", "portal_transparencia"]
