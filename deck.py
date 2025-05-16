"""deck.py"""
__version__ = '05/22/2025'
__author__ = 'Kayla Cao'

import random
from card import Card

class Deck:
    def __init__(self):
        """Initialization"""
        self.cards = []
        self.build()

    def build(self):
        """Create a new 52-card deck"""
        suits = ["Clubs", "Diamonds", "Hearts", "Spades"]
        values = [2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King", "Ace"]  # 11=J, 12=Q, 13=K, 14=A

        self.cards = []
        for suit in suits:
            for val in values:
                self.cards.append(Card(suit, val))

    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)

    def deal(self):
        """Deal one card from the deck"""
        if len(self.cards) > 0:
            return self.cards.pop(0)
        else:
            return None

    def __str__(self):
        """Return the string representation"""
        return f"Deck with {len(self.cards)} cards remaining"