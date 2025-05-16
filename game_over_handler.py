"""game_over_handler.py - Handles endgame scenarios"""
__version__ = '05/22/2025'
__author__ = 'Kayla Cao'

from hand_evaluator import HandEvaluator

class GameOverHandler:
    def __init__(self):
        # Track side pots and eligible players
        self.pots = []  # List of (amount, eligible_players) tuples
        self.main_pot = 0
        self.hand_evaluator = HandEvaluator()

    def reset(self):
        """Reset all pots"""
        self.pots = []
        self.main_pot = 0

    @staticmethod
    def handle_fold(folding_player, other_player, current_pot):
        """Handle when a player folds"""
        # Award the pot to the other player
        other_player.balance += current_pot

        # Reset bets
        folding_player.current_bet = 0
        other_player.current_bet = 0

        # Return the winner and a message
        return other_player, f"{str(folding_player)} folds. {str(other_player)} wins ${current_pot}"

    def handle_all_in(self, players, current_pot):
        """Handle all-in situations and create side pots as needed"""
        # Sort players by their current bet (lowest first)
        sorted_players = sorted([p for p in players if not p.is_folded],
                                key=lambda p: p.current_bet)

        # If no players or only one player, no side pots needed
        if len(sorted_players) <= 1:
            return current_pot

        # Start with the lowest bet
        previous_bet = 0
        remaining_pot = current_pot

        # Process each player's bet to create side pots
        for i, player in enumerate(sorted_players):
            # Skip players who haven't bet
            if player.current_bet == 0:
                continue

            # Calculate the bet difference from previous level
            bet_diff = player.current_bet - previous_bet

            # If there's a difference and we have more than one player
            if bet_diff > 0 and i > 0:
                # Calculate pot size for this level
                pot_size = bet_diff * i

                # Create a side pot with eligible players
                eligible_players = sorted_players[i:]
                self.pots.append((pot_size, eligible_players))

                # Reduce the main pot
                remaining_pot -= pot_size

            # Update previous bet level
            previous_bet = player.current_bet

        # The remaining amount is the main pot (all players eligible)
        self.main_pot = remaining_pot

        return remaining_pot

    def determine_winner(self, player1, player2, community_cards):
        """Determine the winner based on hand strength"""
        # Check for folded players first
        if player1.is_folded:
            return player2, f"{str(player2)} wins (opponent folded)"
        elif player2.is_folded:
            return player1, f"{str(player1)} wins (opponent folded)"

        # Evaluate both hands
        hand1 = self.hand_evaluator.evaluate_hand(player1.hand.cards, community_cards.hand.cards)
        hand2 = self.hand_evaluator.evaluate_hand(player2.hand.cards, community_cards.hand.cards)

        # Get hand names for display
        hand1_name = self.hand_evaluator.get_hand_name(hand1[0])
        hand2_name = self.hand_evaluator.get_hand_name(hand2[0])

        # Compare hands
        result = self.hand_evaluator.compare_hands(hand1, hand2)

        if result == 1:
            return player1, f" wins with {hand1_name}"
        elif result == 2:
            return player2, f" wins with {hand2_name}"
        else:
            # Split pot for ties
            return None, f"Tie game with {hand1_name}. Split pot."

    def handle_showdown(self, player1, player2, community_cards, current_pot):
        """Handle the showdown at the end of the hand"""
        # Determine winner
        winner, message = self.determine_winner(player1, player2, community_cards)

        # Award pot
        if winner:
            winner.balance += current_pot
        else:
            # Split pot for ties
            split_amount = current_pot // 2
            remainder = current_pot % 2

            player1.balance += split_amount
            player2.balance += split_amount

            # Give the remainder to player1 (arbitrary)
            if remainder > 0:
                player1.balance += remainder

        # Reset bets
        player1.current_bet = 0
        player2.current_bet = 0

        return winner, message

    def distribute_winnings(self, player1, player2, community_cards):
        """Distribute winnings from all pots based on hand strength"""
        winnings = {player1: 0, player2: 0}
        result_message = ""

        # Process each side pot from smallest to largest
        for pot_amount, eligible_players in self.pots:
            # Skip if both players folded
            if player1.is_folded and player2.is_folded:
                continue

            # If one player folded, give pot to the other
            if player1.is_folded and player2 in eligible_players:
                winnings[player2] += pot_amount
                result_message += f"Side pot ${pot_amount}: Player 2 wins (Player 1 folded)\n"
                continue

            if player2.is_folded and player1 in eligible_players:
                winnings[player1] += pot_amount
                result_message += f"Side pot ${pot_amount}: Player 1 wins (Player 2 folded)\n"
                continue

            # Both players still in, determine winner
            eligible_p1 = player1 in eligible_players and not player1.is_folded
            eligible_p2 = player2 in eligible_players and not player2.is_folded

            if eligible_p1 and eligible_p2:
                # Evaluate both hands
                hand1 = self.hand_evaluator.evaluate_hand(player1.hand.cards, community_cards.hand.cards)
                hand2 = self.hand_evaluator.evaluate_hand(player2.hand.cards, community_cards.hand.cards)

                # Get hand names
                hand1_name = self.hand_evaluator.get_hand_name(hand1[0])
                hand2_name = self.hand_evaluator.get_hand_name(hand2[0])

                # Compare hands
                result = self.hand_evaluator.compare_hands(hand1, hand2)

                if result == 1:
                    winnings[player1] += pot_amount
                    result_message += f"Side pot ${pot_amount}: Player 1 wins with {hand1_name}\n"
                elif result == 2:
                    winnings[player2] += pot_amount
                    result_message += f"Side pot ${pot_amount}: Player 2 wins with {hand2_name}\n"
                else:
                    # Split pot for ties
                    split_amount = pot_amount // 2
                    remainder = pot_amount % 2

                    winnings[player1] += split_amount
                    winnings[player2] += split_amount

                    # Give the remainder to player1 (arbitrary)
                    if remainder > 0:
                        winnings[player1] += remainder

                    result_message += f"Side pot ${pot_amount}: Tie with {hand1_name}. Split pot.\n"
            elif eligible_p1:
                winnings[player1] += pot_amount
                result_message += f"Side pot ${pot_amount}: Player 1 wins (Player 2 not eligible)\n"
            elif eligible_p2:
                winnings[player2] += pot_amount
                result_message += f"Side pot ${pot_amount}: Player 2 wins (Player 1 not eligible)\n"

        # Process the main pot
        if self.main_pot > 0:
            # Skip if both players folded
            if not (player1.is_folded and player2.is_folded):
                # If one player folded, give pot to the other
                if player1.is_folded:
                    winnings[player2] += self.main_pot
                    result_message += f"Main pot ${self.main_pot}: Player 2 wins (Player 1 folded)\n"
                elif player2.is_folded:
                    winnings[player1] += self.main_pot
                    result_message += f"Main pot ${self.main_pot}: Player 1 wins (Player 2 folded)\n"
                else:
                    # Both players still in, determine winner
                    hand1 = self.hand_evaluator.evaluate_hand(player1.hand.cards, community_cards.hand.cards)
                    hand2 = self.hand_evaluator.evaluate_hand(player2.hand.cards, community_cards.hand.cards)

                    # Get hand names
                    hand1_name = self.hand_evaluator.get_hand_name(hand1[0])
                    hand2_name = self.hand_evaluator.get_hand_name(hand2[0])

                    # Compare hands
                    result = self.hand_evaluator.compare_hands(hand1, hand2)

                    if result == 1:
                        winnings[player1] += self.main_pot
                        result_message += f"Main pot ${self.main_pot}: Player 1 wins with {hand1_name}\n"
                    elif result == 2:
                        winnings[player2] += self.main_pot
                        result_message += f"Main pot ${self.main_pot}: Player 2 wins with {hand2_name}\n"
                    else:
                        # Split pot for ties
                        split_amount = self.main_pot // 2
                        remainder = self.main_pot % 2

                        winnings[player1] += split_amount
                        winnings[player2] += split_amount

                        # Give the remainder to player1 (arbitrary)
                        if remainder > 0:
                            winnings[player1] += remainder

                        result_message += f"Main pot ${self.main_pot}: Tie with {hand1_name}. Split pot.\n"

        # Update player balances
        player1.balance += winnings[player1]
        player2.balance += winnings[player2]

        # Reset bets
        player1.current_bet = 0
        player2.current_bet = 0

        return result_message