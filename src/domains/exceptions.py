class MovementNotFound(Exception):
    def __init__(self, movement_id: str):
        super().__init__(f"Movement with id '{movement_id}' not found.")
        self.movement_id = movement_id
