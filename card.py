"""card.py - includes operator overloads"""
__version__ = '05/22/2025'
__author__ = 'Kayla Cao'

class Card:
    def __init__(self, suit, val):
        """Initialization"""
        self.suit = suit
        self.raw_value = val  # Store the original value (2-14)

        # Set the display name
        self.name = str(val) + " of " + suit

    def get_image_filename(self):
        """Return the filename for this card's image"""
        if self.raw_value == "Jack":
            value_str = "jack"
        elif self.raw_value == "Queen":
            value_str = "queen"
        elif self.raw_value == "King":
            value_str = "king"
        elif self.raw_value == "Ace":
            value_str = "ace"
        else:
            value_str = str(self.raw_value)

        return f"{value_str}_of_{self.suit.lower()}.png"

    def __str__(self):
        """Return the string representation of this card"""
        return self.name