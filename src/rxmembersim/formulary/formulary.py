"""Formulary model."""
from typing import Optional

from pydantic import BaseModel


class FormularyStatus(BaseModel):
    """Result of formulary lookup."""

    ndc: str
    covered: bool = True
    tier: int = 1
    requires_pa: bool = False
    requires_step_therapy: bool = False
    quantity_limit: Optional[int] = None
    quantity_limit_days: Optional[int] = None
    copay: Optional[float] = None
    coinsurance: Optional[float] = None
    message: Optional[str] = None


class Formulary(BaseModel):
    """Drug formulary definition."""

    formulary_id: str
    name: str
    effective_date: str
    # In a real implementation, this would have drug coverage rules
    default_tier: int = 2
    default_copay: float = 30.0

    def check_coverage(self, ndc: str) -> FormularyStatus:
        """Check if drug is covered and get tier/copay info."""
        # Simplified implementation - in reality would look up drug in formulary database
        return FormularyStatus(
            ndc=ndc,
            covered=True,
            tier=self.default_tier,
            copay=self.default_copay,
        )
