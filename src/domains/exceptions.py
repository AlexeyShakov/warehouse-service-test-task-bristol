movement_not_found_err_msg = "Movement with id '{}' not found."
warehouse_or_product_not_found_err_msg = (
    "Warehouse with id '{}' or product with id '{}' not found."
)
arrival_time_is_less_than_departure_err_msg = (
    "Arrival time must be greater than departure time. The message id '{}'"
)
movement_with_same_event_err_msg = (
    "Trying to add movement with event that already exists. The message id '{}'"
)
amount_of_movement_reached_err_msg = "There are already two messages with the same movement. This message with id '{}' is redundant."
exceeded_product_quantity_to_take_err_msg = (
    "You are trying to send more product with id '{}' from the warehouse with id '{}'\
                than there are.The current balance is {}. Message id '{}'"
)


class MovementNotFound(Exception):
    def __init__(self, movement_id: str):
        super().__init__(movement_not_found_err_msg.format(movement_id))


class WarehouseOrProductNotFound(Exception):
    def __init__(self, warehouse_id: str, product_id: str):
        super().__init__(
            warehouse_or_product_not_found_err_msg.format(warehouse_id, product_id)
        )


class ProductMovementValidationError(Exception): ...
