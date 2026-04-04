"""
Enhanced reward system with business-aware metrics.

This module implements a sophisticated reward function that aligns with
real CRM business metrics:
- Customer lifetime value (LTV) weighting
- False positive cost (targeting wrong customers is expensive)
- Efficiency bonus (faster solutions more valuable)
- Confidence scoring (high precision vs. recall trade-offs)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import math


@dataclass
class CustomerValue:
    """Customer value metrics for reward calculation."""
    customer_id: str
    tier: str  # "Bronze", "Silver", "Gold"
    lifetime_value: float  # Estimated LTV
    churn_risk: float  # 0.0-1.0
    purchase_frequency: int  # Orders made
    days_since_signup: int  # Account age


class BusinessAwareRewardCalculator:
    """
    Calculates rewards that align with real CRM business metrics.
    
    Components:
    1. Valid Schema (+0.5) - Proper API usage
    2. Query Narrowing (+0.3) - Good filtering
    3. Task Completion (+3.0 × accuracy) - Answer correctness
    4. Business Value Bonus (+0.0 to +1.0) - LTV of found customers
    5. False Positive Cost (-0.1 × count) - Cost of wrong customers
    6. Efficiency Bonus (+0.0 to +0.5) - Fast solutions
    7. Confidence Score (+0.0 to +0.2) - High precision indicator
    8. Repeated Query (-0.5) - Redundant actions
    """
    
    # Business metrics
    TIER_LTV_WEIGHT = {
        "Bronze": 0.5,   # Bronze customers worth less
        "Silver": 1.0,   # Silver baseline
        "Gold": 2.0      # Gold customers worth 2x
    }
    
    CHURN_RISK_MULTIPLIER = 1.5  # High-risk customers more valuable if retained
    
    def __init__(self):
        """Initialize calculator."""
        self.query_history: List[str] = []
        self.episode_step_count: int = 0
        self.max_episode_steps: int = 15
    
    def reset(self) -> None:
        """Reset for new episode."""
        self.query_history = []
        self.episode_step_count = 0
    
    def calculate_business_value_bonus(
        self,
        predicted_customers: List[CustomerValue],
        correct_customers: List[CustomerValue]
    ) -> float:
        """
        Calculate reward based on business value of found customers.
        
        More valuable to find:
        - Gold tier customers
        - High-risk churn customers (retention is critical)
        - Recently active customers
        
        Args:
            predicted_customers: Customers the agent found
            correct_customers: Customers that were correct answers
            
        Returns:
            Business value bonus (0.0 to 1.0)
        """
        if not predicted_customers:
            return 0.0
        
        # Calculate weighted value
        predicted_value = self._calculate_portfolio_value(predicted_customers)
        correct_value = self._calculate_portfolio_value(correct_customers)
        
        if correct_value == 0:
            return 0.0
        
        # Value match ratio (0.0-1.0)
        value_ratio = min(1.0, predicted_value / correct_value)
        
        # Bonus scales from 0.0 to 1.0
        bonus = 0.0
        
        # Perfect value match
        if value_ratio > 0.9:
            bonus = 1.0
        # Good value match
        elif value_ratio > 0.7:
            bonus = 0.7
        # Partial value match
        elif value_ratio > 0.5:
            bonus = 0.4
        # Poor value match
        else:
            bonus = 0.1 * value_ratio
        
        return bonus
    
    def _calculate_portfolio_value(
        self,
        customers: List[CustomerValue]
    ) -> float:
        """
        Calculate total portfolio value with business weighting.
        
        Args:
            customers: List of customer value objects
            
        Returns:
            Weighted total value
        """
        total_value = 0.0
        
        for customer in customers:
            # Base LTV
            ltv = customer.lifetime_value
            
            # Tier multiplier
            tier_weight = self.TIER_LTV_WEIGHT.get(customer.tier, 1.0)
            
            # Churn risk multiplier (high-risk customers more valuable to retain)
            churn_mult = 1.0 + (customer.churn_risk * self.CHURN_RISK_MULTIPLIER)
            
            # Account age factor (older accounts slightly less valuable)
            age_factor = min(1.0, customer.days_since_signup / 365.0)
            
            # Total weighted value
            weighted_ltv = ltv * tier_weight * churn_mult * age_factor
            total_value += weighted_ltv
        
        return total_value
    
    def calculate_false_positive_cost(
        self,
        false_positive_count: int,
        total_predicted: int
    ) -> float:
        """
        Calculate cost of false positives.
        
        False positives (wrong customers) are expensive in CRM:
        - Wasted marketing spend
        - Poor customer experience
        - Damaged brand trust
        
        Args:
            false_positive_count: Number of incorrect predictions
            total_predicted: Total predictions made
            
        Returns:
            Negative reward (penalty)
        """
        if total_predicted == 0:
            return 0.0
        
        # False positive rate
        fp_rate = false_positive_count / total_predicted
        
        # Cost scales from 0.0 to -1.0
        if fp_rate > 0.5:
            # More than 50% wrong = severe penalty
            cost = -1.0
        elif fp_rate > 0.3:
            # 30-50% wrong = moderate penalty
            cost = -0.5 * fp_rate
        else:
            # <30% wrong = minor penalty per item
            cost = -0.1 * false_positive_count
        
        return cost
    
    def calculate_efficiency_bonus(
        self,
        current_step: int,
        max_steps: int,
        accuracy: float
    ) -> float:
        """
        Reward fast, accurate solutions.
        
        Agents that solve quickly should be rewarded more.
        
        Args:
            current_step: Current step number
            max_steps: Maximum allowed steps
            accuracy: Task accuracy (0.0-1.0)
            
        Returns:
            Efficiency bonus (0.0 to 0.5)
        """
        # Steps remaining ratio
        steps_used = current_step
        steps_remaining = max_steps - current_step
        efficiency_ratio = steps_remaining / max_steps
        
        # Reward faster solutions more
        if efficiency_ratio > 0.7:
            # Used <30% of steps
            bonus = 0.5
        elif efficiency_ratio > 0.5:
            # Used 30-50% of steps
            bonus = 0.3
        elif efficiency_ratio > 0.3:
            # Used 50-70% of steps
            bonus = 0.15
        else:
            # Used >70% of steps
            bonus = 0.05
        
        # Scale by accuracy (accurate + fast = best)
        bonus *= accuracy
        
        return bonus
    
    def calculate_confidence_score(
        self,
        predicted_count: int,
        accuracy: float
    ) -> float:
        """
        Calculate confidence score (precision vs recall trade-off).
        
        High precision (few predictions) + high accuracy = confident agent
        
        Args:
            predicted_count: Number of predictions made
            accuracy: Accuracy of predictions
            
        Returns:
            Confidence bonus (0.0 to 0.2)
        """
        if predicted_count == 0:
            return 0.0
        
        # Confidence = (accuracy × specificity)
        # Reward high accuracy with few predictions
        
        if predicted_count <= 5 and accuracy > 0.9:
            # Very specific, very accurate
            confidence = 0.2
        elif predicted_count <= 10 and accuracy > 0.8:
            # Specific, accurate
            confidence = 0.15
        elif predicted_count <= 15 and accuracy > 0.7:
            # Reasonable precision
            confidence = 0.1
        else:
            # Lower precision
            confidence = 0.05 * accuracy
        
        return confidence
    
    def calculate(
        self,
        action: Dict[str, Any],
        action_result: Dict[str, Any],
        done: bool,
        task_ground_truth: Dict[str, Any],
        step_count: int,
        max_steps: int,
        predicted_customers: Optional[List[CustomerValue]] = None,
        correct_customers: Optional[List[CustomerValue]] = None,
        memory_hit: bool = False,
    ) -> Dict[str, float]:
        """
        Calculate comprehensive reward with business metrics.
        
        Args:
            action: Action taken
            action_result: Result of action
            done: Whether episode ended
            task_ground_truth: Ground truth answer
            step_count: Current step
            max_steps: Maximum steps
            predicted_customers: Customer values for predictions
            correct_customers: Customer values for correct answers
            memory_hit: Whether used cached results
            
        Returns:
            Dictionary of reward components and total
        """
        components = {}
        total_reward = 0.0
        
        tool = action.get("tool", "")
        
        # 1. Schema validation
        if tool in ["search_customers", "search_orders", "search_tickets", "submit_answer"]:
            components["valid_schema"] = 0.5
            total_reward += 0.5
        else:
            components["invalid_schema"] = -2.0
            return components
        
        # 2. Result narrowing
        result_data = action_result.get("data", [])
        result_size = len(result_data) if isinstance(result_data, list) else 0
        
        if 1 <= result_size <= 50:
            components["narrowing_bonus"] = 0.3
            total_reward += 0.3
        elif result_size == 0:
            components["empty_result"] = -0.2
            total_reward -= 0.2
        
        # 3. Repeated query detection
        query_key = f"{tool}:{str(sorted(action.get('arguments', {}).items()))}"
        if query_key not in self.query_history:
            self.query_history.append(query_key)
        else:
            components["repeated_query"] = -0.5
            total_reward -= 0.5
        
        # 4. Memory reuse
        if memory_hit:
            components["memory_reuse"] = 0.4
            total_reward += 0.4
        
        # 5-7. Submit answer specific rewards
        if tool == "submit_answer" and done:
            predicted = action.get("arguments", {}).get("customer_ids", [])
            ground_truth_ids = task_ground_truth.get("customer_ids", [])
            
            # Accuracy
            correct_set = set(predicted) & set(ground_truth_ids)
            gt_set = set(ground_truth_ids)
            accuracy = len(correct_set) / len(gt_set) if gt_set else 0.0
            
            task_reward = 3.0 * accuracy
            components["task_accuracy"] = task_reward
            total_reward += task_reward
            
            # False positive cost
            if predicted:
                false_positives = len(set(predicted) - gt_set)
                fp_cost = self.calculate_false_positive_cost(
                    false_positives,
                    len(predicted)
                )
                components["false_positive_cost"] = fp_cost
                total_reward += fp_cost
            
            # Business value bonus
            if predicted_customers and correct_customers:
                value_bonus = self.calculate_business_value_bonus(
                    predicted_customers,
                    correct_customers
                )
                components["business_value"] = value_bonus
                total_reward += value_bonus
            
            # Efficiency bonus
            eff_bonus = self.calculate_efficiency_bonus(step_count, max_steps, accuracy)
            components["efficiency"] = eff_bonus
            total_reward += eff_bonus
            
            # Confidence score
            conf_score = self.calculate_confidence_score(len(predicted), accuracy)
            components["confidence"] = conf_score
            total_reward += conf_score
        
        components["total"] = total_reward
        return components


# Example usage
if __name__ == "__main__":
    calculator = BusinessAwareRewardCalculator()
    
    # Example customers
    gold_customer = CustomerValue(
        customer_id="C001",
        tier="Gold",
        lifetime_value=50000.0,
        churn_risk=0.2,
        purchase_frequency=15,
        days_since_signup=400
    )
    
    silver_customer = CustomerValue(
        customer_id="C002",
        tier="Silver",
        lifetime_value=15000.0,
        churn_risk=0.1,
        purchase_frequency=5,
        days_since_signup=200
    )
    
    # Example action
    action = {"tool": "submit_answer", "arguments": {"customer_ids": ["C001", "C002"]}}
    action_result = {"data": []}
    task_ground_truth = {"customer_ids": ["C001", "C002", "C003"]}
    
    # Calculate rewards
    components = calculator.calculate(
        action=action,
        action_result=action_result,
        done=True,
        task_ground_truth=task_ground_truth,
        step_count=5,
        max_steps=15,
        predicted_customers=[gold_customer, silver_customer],
        correct_customers=[gold_customer, silver_customer],
        memory_hit=False
    )
    
    print("Reward Components:")
    for key, value in components.items():
        print(f"  {key}: {value:.3f}")
    
    print(f"\nTotal Reward: {components['total']:.3f}")
