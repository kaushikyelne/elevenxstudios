from typing import Any, Dict
from app.tools.base import AgentTool


class GetTransactionsTool(AgentTool):
    @property
    def name(self) -> str:
        return "get_transactions"

    @property
    def description(self) -> str:
        return "Fetch a list of recent financial transactions for the user. Use this when the user asks about their spending, balance, or history."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days of history to fetch (default: 30)",
                },
                "category": {
                    "type": "string",
                    "description": "Filter by category (e.g., 'Food', 'Rent', 'Travel')",
                },
            },
        }

    async def execute(self, days: int = 30, category: str = None) -> Any:
        # Mocking data for now. In a real scenario, this would call the transaction-service.
        transactions = [
            {"id": "1", "amount": 120.50, "category": "Food", "description": "Grocery Store", "date": "2024-03-15"},
            {"id": "2", "amount": 12.00, "category": "Transport", "description": "Uber", "date": "2024-03-16"},
            {"id": "3", "amount": 2500.00, "category": "Rent", "description": "Monthly Rent", "date": "2024-03-01"},
            {"id": "4", "amount": 45.00, "category": "Food", "description": "Coffee Shop", "date": "2024-03-17"},
        ]
        
        if category:
            transactions = [tx for tx in transactions if tx["category"].lower() == category.lower()]
            
        return {"transactions": transactions[:days]}
