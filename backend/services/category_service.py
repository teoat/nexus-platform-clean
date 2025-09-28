"""
Category Service - Placeholder implementation
"""


class CategoryService:
    def get_categories(self, db, user_id):
        # Placeholder - return empty list
        return []

    def create_category(self, db, user_id, category_data):
        # Placeholder - raise not implemented
        raise NotImplementedError("Category service not implemented")

    def get_category(self, db, user_id, category_id):
        # Placeholder - return None
        return None

    def update_category(self, db, user_id, category_id, category_data):
        # Placeholder - raise not implemented
        raise NotImplementedError("Category service not implemented")

    def delete_category(self, db, user_id, category_id):
        # Placeholder - raise not implemented
        raise NotImplementedError("Category service not implemented")


# Create service instance
category_service = CategoryService()
