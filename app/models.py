"""
Pydantic models for OpenEnv compliance.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Customer(BaseModel):
    """Customer entity."""
    customer_id: str
    name: str
    email: str
    tier: str  # Bronze, Silver, Gold
    phone: str
    created_at: str


class Order(BaseModel):
    """Order entity."""
    order_id: str
    customer_id: str
    product: str
    amount: float
    status: str  # Pending, Completed, Cancelled
    created_at: str


class SupportTicket(BaseModel):
    """Support ticket entity."""
    ticket_id: str
    customer_id: str
    subject: str
    priority: str  # Low, Medium, High
    status: str  # Open, Closed
    created_at: str


class SearchCustomersAction(BaseModel):
    """Action to search customers."""
    tool: str = Field(default="search_customers", frozen=True)
    arguments: Dict[str, Any] = Field(
        description="Filter arguments: customer_id, name, email, tier, phone"
    )


class SearchOrdersAction(BaseModel):
    """Action to search orders."""
    tool: str = Field(default="search_orders", frozen=True)
    arguments: Dict[str, Any] = Field(
        description="Filter arguments: order_id, customer_id, product, status"
    )


class SearchTicketsAction(BaseModel):
    """Action to search support tickets."""
    tool: str = Field(default="search_tickets", frozen=True)
    arguments: Dict[str, Any] = Field(
        description="Filter arguments: ticket_id, customer_id, priority, status"
    )


class SubmitAnswerAction(BaseModel):
    """Action to submit final answer."""
    tool: str = Field(default="submit_answer", frozen=True)
    arguments: Dict[str, Any] = Field(
        description="Final answer: customer_ids list"
    )


class Action(BaseModel):
    """Union of all possible actions."""
    tool: str
    arguments: Dict[str, Any]

    model_config = {"extra": "forbid"}


class Observation(BaseModel):
    """Observation returned by environment."""
    task_id: str
    task_description: str
    step_count: int
    max_steps: int
    available_tools: List[str]
    last_action_result: Optional[Dict[str, Any]] = None
    tables_summary: Dict[str, Any]
    done: bool
    message: str
    memory_cache: Optional[Dict[str, List[Dict[str, Any]]]] = Field(default_factory=dict, description="Cached entities from previous queries")
    step_summaries: List[str] = Field(default_factory=list, description="Compact summaries of executed steps")


class Reward(BaseModel):
    """Reward signal."""
    value: float = Field(ge=-10.0, le=10.0)
    components: Dict[str, float] = Field(default_factory=dict)
    message: str


class State(BaseModel):
    """Environment state."""
    current_task_id: str
    step_count: int
    max_steps: int
    history: List[Dict[str, Any]] = Field(default_factory=list)
    done: bool
    final_answer: Optional[Dict[str, Any]] = None
    retrieved_entities: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict, description="Cache of retrieved entities")
    step_summaries: List[str] = Field(default_factory=list, description="Summaries of each step for memory reuse")


class Info(BaseModel):
    """Additional info."""
    task_id: str
    episode_reward: float
    intermediate_results: Dict[str, Any] = Field(default_factory=dict)


class Task(BaseModel):
    """Task definition."""
    task_id: str
    difficulty: str  # easy, medium, hard
    description: str
    ground_truth: Dict[str, Any]
    max_steps: int
    action_schema: Dict[str, Any]
    grader: Optional[callable] = Field(default=None, exclude=True, description="Grader function for this task")
    
    model_config = {"arbitrary_types_allowed": True}
