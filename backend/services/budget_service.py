"""
Budget Service - Placeholder implementation
"""


class BudgetService:
    def get_budgets(self, db, user_id, category_id=None):
        # Placeholder - return empty list
        return []

    def create_budget(self, db, user_id, budget_data):
        # Placeholder - raise not implemented
        raise NotImplementedError("Budget service not implemented")

    def get_budget(self, db, user_id, budget_id):
        # Placeholder - return None
        return None

    def update_budget(self, db, user_id, budget_id, budget_data):
        # Placeholder - raise not implemented
        raise NotImplementedError("Budget service not implemented")

    def delete_budget(self, db, user_id, budget_id):
        # Placeholder - raise not implemented
        raise NotImplementedError("Budget service not implemented")


# Create service instance
budget_service = BudgetService()
