"""hand_evaluator.py - Evaluates poker hands and determines winners"""
__version__ = '05/22/2025'
__author__ = 'Kayla Cao'

class HandEvaluator:
    # Hand rankings from highest to lowest
    ROYAL_FLUSH = 9
    STRAIGHT_FLUSH = 8
    FOUR_OF_A_KIND = 7
    FULL_HOUSE = 6
    FLUSH = 5
    STRAIGHT = 4
    THREE_OF_A_KIND = 3
    TWO_PAIR = 2
    ONE_PAIR = 1
    HIGH_CARD = 0

    @staticmethod #no self variables
    def evaluate_hand(player_cards, community_cards):
        """Evaluate the best 5-card hand from player's 2 cards and community cards"""
        print(f"Player cards: {len(player_cards)}")
        print(f"Community cards: {len(community_cards)}")

        # Combine player cards and community cards
        all_cards = player_cards + community_cards

        # Debugging: print all card values
        print("All cards:")
        for card in all_cards:
            print(f"{card.name}")

        # Convert face cards to numeric values for easier comparison
        card_values = []
        for card in all_cards:
            if card.raw_value == "Jack":
                value = 11
            elif card.raw_value == "Queen":
                value = 12
            elif card.raw_value == "King":
                value = 13
            elif card.raw_value == "Ace":
                value = 14  # Ace high (can also be 1 for straights)
            else:
                value = card.raw_value

            card_values.append((value, card.suit))

        # Sort cards by value (highest first)
        card_values.sort(reverse=True, key=lambda x: x[0])

        # Check for each hand type from highest to lowest
        if HandEvaluator._is_royal_flush(card_values):
            return HandEvaluator.ROYAL_FLUSH, []

        straight_flush = HandEvaluator._is_straight_flush(card_values)
        if straight_flush[0]:
            return HandEvaluator.STRAIGHT_FLUSH, straight_flush[1]

        four_kind = HandEvaluator._is_four_of_a_kind(card_values)
        if four_kind[0]:
            return HandEvaluator.FOUR_OF_A_KIND, four_kind[1]

        full_house = HandEvaluator._is_full_house(card_values)
        if full_house[0]:
            return HandEvaluator.FULL_HOUSE, full_house[1]

        flush = HandEvaluator._is_flush(card_values)
        if flush[0]:
            return HandEvaluator.FLUSH, flush[1]

        straight = HandEvaluator._is_straight(card_values)
        if straight[0]:
            return HandEvaluator.STRAIGHT, straight[1]

        three_kind = HandEvaluator._is_three_of_a_kind(card_values)
        if three_kind[0]:
            return HandEvaluator.THREE_OF_A_KIND, three_kind[1]

        two_pair = HandEvaluator._is_two_pair(card_values)
        if two_pair[0]:
            return HandEvaluator.TWO_PAIR, two_pair[1]

        one_pair = HandEvaluator._is_one_pair(card_values)
        if one_pair[0]:
            return HandEvaluator.ONE_PAIR, one_pair[1]

        # If no other hand, return high card
        return HandEvaluator.HIGH_CARD, [card_values[0][0]]

    @staticmethod
    def _is_royal_flush(cards):
        """Check for royal flush (A, K, Q, J, 10 of same suit)"""
        # Group cards by suit
        suits = {}
        for value, suit in cards:
            if suit not in suits:
                suits[suit] = []
            suits[suit].append(value)

        # Check each suit group for royal flush
        for suit, values in suits.items():
            if len(values) >= 5:  # Need at least 5 cards of same suit
                values.sort(reverse=True)  # Sort descending
                if values[:5] == [14, 13, 12, 11, 10]:  # A, K, Q, J, 10
                    return True
        return False

    @staticmethod
    def _is_straight_flush(cards):
        """Check for straight flush (5 sequential cards of same suit)"""
        # Group cards by suit
        suits = {}
        for value, suit in cards:
            if suit not in suits:
                suits[suit] = []
            suits[suit].append((value, suit))

        # Check each suit group for straight flush
        for suit, suit_cards in suits.items():
            if len(suit_cards) >= 5:
                # Call _is_straight with just the cards of this suit
                straight_result = HandEvaluator._is_straight(suit_cards)
                if straight_result[0]:
                    return straight_result

        return False, []

    @staticmethod
    def _is_four_of_a_kind(cards):
        """Check for four of a kind"""
        # Count occurrences of each value
        value_counts = {}
        for value, _ in cards:
            if value not in value_counts:
                value_counts[value] = 0
            value_counts[value] += 1

        # Check for four of a kind
        for value, count in value_counts.items():
            if count == 4:
                # Find the highest kicker
                kickers = [v for v, _ in cards if v != value]
                return True, [value, max(kickers)]

        return False, []

    @staticmethod
    def _is_full_house(cards):
        """Check for full house (three of a kind + pair)"""
        # First, check for three of a kind
        three_kind_result = HandEvaluator._is_three_of_a_kind(cards)

        if three_kind_result[0]:
            # If three of a kind exists, look for a pair
            three_value = three_kind_result[1][0]

            # Create a new list of cards excluding the three of a kind
            remaining_cards = [(v, s) for v, s in cards if v != three_value]

            # Check for a pair in the remaining cards
            pair_result = HandEvaluator._is_one_pair(remaining_cards)

            if pair_result[0]:
                return True, [three_value, pair_result[1][0]]

        return False, []

    @staticmethod
    def _is_flush(cards):
        """Check for flush (5 cards of same suit)"""
        # Group cards by suit
        suits = {}
        for value, suit in cards:
            if suit not in suits:
                suits[suit] = []
            suits[suit].append(value)

        # Check each suit group for flush
        for suit, values in suits.items():
            if len(values) >= 5:  # Need at least 5 cards of same suit
                values.sort(reverse=True)  # Sort descending
                return True, values[:5]  # Return top 5 cards

        return False, []

    @staticmethod
    def _is_straight(cards):
        """Check for straight (5 sequential cards)"""
        # Remove duplicates and sort
        values = sorted(set([value for value, _ in cards]), reverse=True)

        # Check for A-5 straight (special case with ace at bottom)
        if 14 in values and 2 in values and 3 in values and 4 in values and 5 in values:
            return True, [5]  # 5-high straight

        # Check for regular straight
        for i in range(len(values) - 4):
            if values[i] - values[i + 4] == 4:  # 5 sequential cards
                return True, [values[i]]  # Return high card

        return False, []

    @staticmethod
    def _is_three_of_a_kind(cards):
        """Check for three of a kind"""
        # Count occurrences of each value
        value_counts = {}
        for value, _ in cards:
            if value not in value_counts:
                value_counts[value] = 0
            value_counts[value] += 1

        # Check for three of a kind
        for value, count in value_counts.items():
            if count == 3:
                # Find the two highest kickers
                kickers = sorted([v for v, _ in cards if v != value], reverse=True)
                return True, [value, kickers[0], kickers[1]]

        return False, []

    @staticmethod
    def _is_two_pair(cards):
        """Check for two pair"""
        # Count occurrences of each value
        value_counts = {}
        for value, _ in cards:
            if value not in value_counts:
                value_counts[value] = 0
            value_counts[value] += 1

        # Find pairs
        pairs = []
        for value, count in value_counts.items():
            if count >= 2:
                pairs.append(value)

        if len(pairs) >= 2:
            # Sort pairs by value (highest first)
            pairs.sort(reverse=True)
            # Find the highest kicker
            kickers = [v for v, _ in cards if v != pairs[0] and v != pairs[1]]
            return True, [pairs[0], pairs[1], max(kickers)]

        return False, []

    @staticmethod
    def _is_one_pair(cards):
        """Check for one pair"""
        # Count occurrences of each value
        value_counts = {}
        #makes a dictionary, if the number isn't in value_counts, store it, and add 1 to how many of that number there are
        for value, _ in cards:
            if value not in value_counts:
                value_counts[value] = 0
            value_counts[value] += 1

        # Check for pair
        for value, count in value_counts.items():
            if count == 2:
                # Find the three highest kickers
                kickers = sorted([v for v, _ in cards if v != value], reverse=True)
                return True, [value, kickers[0], kickers[1], kickers[2]]

        return False, []

    @staticmethod
    def compare_hands(hand1, hand2):
        """Compare two hands and return the winner (1 for hand1, 2 for hand2, 0 for tie)"""
        # Compare hand types first
        if hand1[0] > hand2[0]:
            return 1
        elif hand1[0] < hand2[0]:
            return 2

        # If hand types are the same, compare tiebreakers
        for i in range(min(len(hand1[1]), len(hand2[1]))):
            if hand1[1][i] > hand2[1][i]:
                return 1
            elif hand1[1][i] < hand2[1][i]:
                return 2

        # If all tiebreakers are equal, it's a tie
        return 0

    @staticmethod
    def get_hand_name(hand_type):
        """Return the name of a hand type"""
        names = {
            HandEvaluator.ROYAL_FLUSH: "Royal Flush",
            HandEvaluator.STRAIGHT_FLUSH: "Straight Flush",
            HandEvaluator.FOUR_OF_A_KIND: "Four of a Kind",
            HandEvaluator.FULL_HOUSE: "Full House",
            HandEvaluator.FLUSH: "Flush",
            HandEvaluator.STRAIGHT: "Straight",
            HandEvaluator.THREE_OF_A_KIND: "Three of a Kind",
            HandEvaluator.TWO_PAIR: "Two Pair",
            HandEvaluator.ONE_PAIR: "Pair",
            HandEvaluator.HIGH_CARD: "High Card"
        }
        return names.get(hand_type, "Unknown Hand")