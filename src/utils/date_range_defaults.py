"""
Smart date range defaults for transparency API queries
Provides intelligent default date ranges when user doesn't specify dates
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple


class DateRangeDefaults:
    """Provides intelligent date range defaults based on query type"""

    @staticmethod
    def get_contracts_range() -> Tuple[str, str]:
        """
        Get default date range for contracts queries.

        Returns last 30 days (Portal API has better data coverage for recent contracts)

        Returns:
            Tuple of (start_date, end_date) in DD/MM/YYYY format
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return (
            start_date.strftime("%d/%m/%Y"),
            end_date.strftime("%d/%m/%Y"),
        )

    @staticmethod
    def get_expenses_range() -> Tuple[str, str]:
        """
        Get default date range for expenses queries.

        Returns current fiscal year (January 1st to today)

        Returns:
            Tuple of (start_date, end_date) in DD/MM/YYYY format
        """
        end_date = datetime.now()
        start_date = datetime(end_date.year, 1, 1)  # January 1st of current year
        return (
            start_date.strftime("%d/%m/%Y"),
            end_date.strftime("%d/%m/%Y"),
        )

    @staticmethod
    def get_biddings_range() -> Tuple[str, str]:
        """
        Get default date range for biddings queries.

        Returns last 6 months (bidding processes take time to complete)

        Returns:
            Tuple of (start_date, end_date) in DD/MM/YYYY format
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)  # ~6 months
        return (
            start_date.strftime("%d/%m/%Y"),
            end_date.strftime("%d/%m/%Y"),
        )

    @staticmethod
    def get_servants_range() -> Tuple[str, str]:
        """
        Get default date range for civil servants queries.

        Returns current month (servant data is usually current/recent)

        Returns:
            Tuple of (start_date, end_date) in DD/MM/YYYY format
        """
        end_date = datetime.now()
        start_date = datetime(
            end_date.year, end_date.month, 1
        )  # First day of current month
        return (
            start_date.strftime("%d/%m/%Y"),
            end_date.strftime("%d/%m/%Y"),
        )

    @staticmethod
    def get_range_for_query_type(query_type: str) -> Tuple[str, str]:
        """
        Get appropriate date range based on query type.

        Args:
            query_type: Type of query (contratos, despesas, licitacoes, servidores)

        Returns:
            Tuple of (start_date, end_date) in DD/MM/YYYY format
        """
        query_type = query_type.lower()

        if "contrato" in query_type:
            return DateRangeDefaults.get_contracts_range()
        elif "despesa" in query_type or "gasto" in query_type:
            return DateRangeDefaults.get_expenses_range()
        elif "licitac" in query_type or "edital" in query_type:
            return DateRangeDefaults.get_biddings_range()
        elif "servidor" in query_type or "funciona" in query_type:
            return DateRangeDefaults.get_servants_range()
        else:
            # Default: last 30 days
            return DateRangeDefaults.get_contracts_range()

    @staticmethod
    def apply_defaults_if_missing(
        data_inicio: Optional[str],
        data_fim: Optional[str],
        query_type: str = "contratos",
    ) -> Tuple[str, str]:
        """
        Apply default date range if dates are missing.

        Args:
            data_inicio: Start date (DD/MM/YYYY) or None
            data_fim: End date (DD/MM/YYYY) or None
            query_type: Type of query for smart defaults

        Returns:
            Tuple of (start_date, end_date) with defaults applied if needed
        """
        # If both dates provided, return as-is
        if data_inicio and data_fim:
            return (data_inicio, data_fim)

        # If both missing, use defaults for query type
        if not data_inicio and not data_fim:
            return DateRangeDefaults.get_range_for_query_type(query_type)

        # If only start date provided, end date is today
        if data_inicio and not data_fim:
            return (data_inicio, datetime.now().strftime("%d/%m/%Y"))

        # If only end date provided, start date is 30 days before
        if data_fim and not data_inicio:
            end_dt = datetime.strptime(data_fim, "%d/%m/%Y")
            start_dt = end_dt - timedelta(days=30)
            return (start_dt.strftime("%d/%m/%Y"), data_fim)

        # Fallback (should never reach here)
        return DateRangeDefaults.get_contracts_range()


# Global helper function
def get_default_date_range(query_type: str = "contratos") -> Tuple[str, str]:
    """
    Get default date range for a query type.

    Convenience function for quick access to defaults.

    Args:
        query_type: Type of query (contratos, despesas, licitacoes, servidores)

    Returns:
        Tuple of (start_date, end_date) in DD/MM/YYYY format

    Examples:
        >>> get_default_date_range("contratos")
        ('24/09/2025', '24/10/2025')  # Last 30 days

        >>> get_default_date_range("despesas")
        ('01/01/2025', '24/10/2025')  # Current fiscal year
    """
    return DateRangeDefaults.get_range_for_query_type(query_type)
