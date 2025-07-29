""""
Book sequence generator for unique book IDs.
This class generates sequential book IDs starting from a specified number.
It can be used to ensure each book has a unique identifier.
"""

class BookSequence:
    def __init__(self, start_id: int = 1):
        self.current_id = start_id

    def get_next_id(self, step: int = 1) -> int:
        book_id = self.current_id
        self.current_id += step
        return book_id