"""hand.py"""
__version__ = '05/22/2025'
__author__ = 'Kayla Cao'

class Hand:
    def __init__(self):
        """Initialization"""
        self.cards = []

    def add_card(self, card):
        """Add a card to the hand"""
        self.cards.append(card)

    def __str__(self):
        """String representation of the hand"""
        return ", ".join(str(card) for card in self.cards)