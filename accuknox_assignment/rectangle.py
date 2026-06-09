class Rectangle:
    """
    A class representing a rectangle initialized with length and width.
    Iterating over an instance yields its length first, followed by its width,
    both structured as dictionaries.
    """

    def __init__(self, length: int, width: int):
        self.length = length
        self.width = width

    def __iter__(self):
        yield {
            "length": self.length
        }
        yield {
            "width": self.width
        }
