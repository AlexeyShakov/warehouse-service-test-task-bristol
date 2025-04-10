class MovementNotFound(Exception):
    def __init__(self, movement_id: str):
        super().__init__(f"Movement with id '{movement_id}' not found.")
        self.movement_id = movement_id


class WarehouseOrProductNotFound(Exception):
    def __init__(self, warehouse_id: str, product_id: str):
        super().__init__(
            f"Warehouse with id '{warehouse_id}' or product with id '{product_id}' not found."
        )
        self.warehouse_id = warehouse_id
        self.product_id = product_id
