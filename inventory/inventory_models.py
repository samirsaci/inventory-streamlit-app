from typing import Optional, Literal
from pydantic import BaseModel, Field


class InventoryParams(BaseModel):
    """Base economic & demand parameters (deterministic daily demand)."""
    D: float = Field(2000, gt=0, description="Annual demand (units/year)")
    T_total: int = Field(365, ge=1, description="Days in horizon (usually 365)")
    LD: int = Field(0, ge=0, description="Lead time (days)")
    T: int = Field(10, ge=1, description="Cycle time (days)")
    Q: float = Field(0, ge=0, description="Order quantity (units)")
    initial_ioh: float = Field(0, description="Initial inventory on hand")
    sigma: float = Field(0, ge=0, description="Standard deviation of daily demand (units/day)")
