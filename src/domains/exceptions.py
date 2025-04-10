class MovementNotFound(Exception):
    def __init__(self, movement_id: str):
        super().__init__(f"Movement with id '{movement_id}' not found.")


class WarehouseOrProductNotFound(Exception):
    def __init__(self, warehouse_id: str, product_id: str):
        super().__init__(
            f"Warehouse with id '{warehouse_id}' or product with id '{product_id}' not found."
        )


class ProductMovementValidationError(Exception): ...


class ExtraMovementError(Exception):
    def __init__(self, message_id: str):
        super().__init__(
            f"There are already two messages with the same movement. This message with id '{message_id}' is redundant."
        )
