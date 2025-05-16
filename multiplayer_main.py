import os
import sys
import socket
import threading

import pygame

from config import *
from deck import Deck
from hand import Hand
from player import Player
from input_handler import InputHandler
from button import Button
from hand_evaluator import HandEvaluator
from game_over_handler import GameOverHandler
from sounds import SoundManager
from network_manager import NetworkManager
from poker_network_manager import PokerNetworkManager
from card import Card


class MultiplayerPokerGame:
    def __init__(self, is_server=False, server_ip='127.0.0.1'):
        # Pygame initialization
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Heads Down! Multiplayer Poker')

        # Network configuration
        self.is_server = is_server
        self.player_id = 0 if is_server else 1
        self.network_manager = PokerNetworkManager(
            game=self,
            is_server=is_server,
            server_ip=server_ip
        )

        # Game state initialization
        self._initialize_game_components()
        self._create_buttons()

    def _initialize_game_components(self):
        # Card images
        self.card_images = {}
        self._load_card_images()

        # Players and game state
        self.player1 = Player()
        self.player2 = Player()
        self.community_cards = Player()
        self.community_cards.cards_visible = True

        # Game mechanics
        self.pot = 0
        self.hand_evaluator = HandEvaluator()
        self.game_over_handler = GameOverHandler()
        self.sound_manager = SoundManager()

        # Game state tracking
        self.status_message = ''
        self.small_blind = 0
        self.big_blind = 0
        self.current_player = self.player2
        self.current_dealer = self.player2
        self.current_bigblind = self.player1
        self.game_state = STATE_PREFLOP
        self.winner = None

    def _create_buttons(self):
        # Fonts
        self.font = pygame.font.SysFont(None, 36)
        self.button_font = pygame.font.SysFont(None, 24)

        # Buttons
        self.buttons = pygame.sprite.Group(
            Button(50, 550, 80, 40, 'P1 Cards', self.button_font),
            Button(150, 550, 80, 40, 'P2 Cards', self.button_font),
            Button(250, 550, 80, 40, 'Call', self.button_font),
            Button(350, 550, 80, 40, 'Raise', self.button_font),
            Button(450, 550, 80, 40, 'Fold', self.button_font),
            Button(550, 550, 80, 40, 'Check', self.button_font)
        )

    def _load_card_images(self):
        # Copy the card image loading method from your original main.py
        # This method should populate self.card_images with card images
        image_dir = 'img'

        # Try to load card back image
        try:
            back_path = os.path.join(image_dir, 'red_back.png')
            if os.path.exists(back_path):
                self.card_back = pygame.image.load(back_path)
                self.card_back = pygame.transform.scale(self.card_back, (CARD_WIDTH, CARD_HEIGHT))
            else:
                print(f'Warning: Card back image not found at {back_path}')
                self.card_back = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
                self.card_back.fill((0, 0, 128))  # Navy blue
        except pygame.error as e:
            print(f'Error loading card back: {e}')
            self.card_back = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            self.card_back.fill((0, 0, 128))  # Navy blue

    def draw_game(self):
        # Fill background
        self.screen.fill(BACKGROUND_COLOR)

        # Draw player balances
        p1_balance_text = self.font.render(f'Player 1: ${self.player1.balance}', True, TEXT_COLOR)
        p2_balance_text = self.font.render(f'Player 2: ${self.player2.balance}', True, TEXT_COLOR)
        self.screen.blit(p1_balance_text, (50, 50))
        self.screen.blit(p2_balance_text, (50, 320))

        # Draw pot
        pot_text = self.font.render(f'Pot: ${self.pot}', True, TEXT_COLOR)
        self.screen.blit(pot_text, (SCREEN_WIDTH // 2 - 50, 70))

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.render(button.is_hovered(mouse_pos))
            button.draw(self.screen)

        # Draw status message
        if self.status_message:
            status_text = self.font.render(self.status_message, True, (255, 255, 0))
            status_rect = status_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
            self.screen.blit(status_text, status_rect)

    def handle_remote_action(self, action, amount=0, player_id=None):
        """Process actions received from the network"""
        action_map = {
            'fold': self.handle_fold,
            'call': self.handle_call,
            'raise': lambda: self.handle_raise(amount),
            'check': self.handle_check
        }

        if action in action_map:
            action_map[action]()

    def get_network_state(self):
        """Serialize game state for network transmission"""
        return {
            'pot': self.pot,
            'game_state': self.game_state,
            'player1_balance': self.player1.balance,
            'player2_balance': self.player2.balance,
            'player1_bet': self.player1.current_bet,
            'player2_bet': self.player2.current_bet,
            'current_player_id': 0 if self.current_player == self.player1 else 1,
            'community_cards': [card.name for card in self.community_cards.hand.cards]
        }

    def update_from_network(self, state):
        """Update local game state from network data"""
        # Update game state attributes from received state
        for key, value in state.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # Update community cards
        self.community_cards.hand.cards = [
            self.card_from_name(card_name) for card_name in state.get('community_cards', [])
        ]

        # Update current player
        self.current_player = (
            self.player1 if state.get('current_player_id', 0) == 0 else self.player2
        )

    def card_from_name(self, card_name):
        """Convert card name back to Card object"""
        value, _, suit = card_name.partition(' of ')
        return Card(suit, value)

    def run(self):
        """Main game loop with network support"""
        # Start network manager
        self.network_manager.start()

        # Initial game setup
        self.player1.set_balance(self.screen, 'player 1\'s')
        self.player2.set_balance(self.screen, 'player 2\'s')
        self.set_blinds(self.screen)
        self.reset_game()

        # Game loop
        clock = pygame.time.Clock()
        running = True

        while self.network_manager.running and running:
            self.draw_game()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    self._handle_mouse_click(mouse_pos)

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
        sys.exit()

    def _handle_mouse_click(self, mouse_pos):
        """Handle mouse clicks based on game state and player turn"""
        if self.game_state == STATE_GAME_OVER:
            return

        # Check if it's the current player's turn
        if self.current_player == (self.player1 if self.player_id == 0 else self.player2):
            for button in self.buttons:
                if button.is_hovered(mouse_pos):
                    self._process_button_action(button.text)
                    break

    def _process_button_action(self, button_text):
        """Process actions for different buttons"""
        action_map = {
            'P1 Cards': self._toggle_cards,
            'Call': self._handle_call_action,
            'Raise': self._handle_raise_action,
            'Fold': self._handle_fold_action,
            'Check': self._handle_check_action
        }

        if button_text in action_map:
            action_map[button_text]()

    def _toggle_cards(self):
        """Toggle card visibility and send network action"""
        if self.current_player == self.player1:
            self.player1.cards_visible = not self.player1.cards_visible
            self.network_manager.send_action('toggle_cards')

    def _handle_call_action(self):
        """Handle call button action"""
        if self.player1.current_bet > 0 or self.player2.current_bet > 0:
            self.handle_call()
            self.network_manager.send_action('call')

    def _handle_raise_action(self):
        """Handle raise button action"""
        raise_amount = self.current_player.player_bet(self.screen)
        if raise_amount is not None:
            self.handle_raise(raise_amount)
            self.network_manager.send_action('raise', amount=raise_amount)

    def _handle_fold_action(self):
        """Handle fold button action"""
        self.handle_fold()
        self.network_manager.send_action('fold')

    def _handle_check_action(self):
        """Handle check button action"""
        self.handle_check()
        self.network_manager.send_action('check')

    def handle_fold(self):
        """Handles what happens when a player folds"""
        self.current_player.is_folded = True

        other_player = self.player2 if self.current_player == self.player1 else self.player1
        # Use the game over handler to determine winner
        winner, message = self.game_over_handler.handle_fold(self.current_player, other_player, self.pot)

        # Update pot and display message
        self.pot = 0
        self.status_message = message

        # Set game state to game over
        self.game_state = STATE_GAME_OVER
        self.winner = winner

    def handle_call(self):
        """Handle when a player calls"""
        # Hide both players' cards first
        self.player1.cards_visible = False
        self.player2.cards_visible = False

        # play poker chip sound
        self.sound_manager.play_poker_chip()

        other_player = self.player2 if self.current_player == self.player1 else self.player1
        call_amount = other_player.current_bet - self.current_player.current_bet

        # Check if player has enough money to call
        if call_amount > self.current_player.balance:
            # Handle all in situation
            call_amount = self.current_player.balance
            self.current_player.is_all_in = True
            self.status_message = f"Player {1 if self.current_player == self.player1 else 2} is ALL IN!"

        # Add the call amount to the pot
        self.pot += call_amount
        self.current_player.place_bet(other_player.current_bet)

        # Check if BOTH players are now all-in
        if self.player1.is_all_in and self.player2.is_all_in:
            # Deal all remaining community cards
            while len(self.community_cards.hand.cards) < 5:
                self.community_cards.hand.add_card(self.deck.deal())

            # Go directly to showdown
            self.game_state = STATE_SHOWDOWN
            self.handle_showdown()
            return

        # Special handling for preflop
        if self.game_state == STATE_PREFLOP:
            # If current player is the dealer (small blind), switch to big blind
            if self.current_player == self.current_dealer:
                self.current_player = self.current_bigblind
                return

        # Check if both players have acted and bets are equal, or if someone is all-in
        if (self.player1.current_bet == self.player2.current_bet) or \
                self.player1.is_all_in or self.player2.is_all_in:
            # Both players have acted and bets are equal, advance to next phase
            self.advance_game_state()
        else:
            # Switch to the other player's turn
            self.switch_turn()

    def handle_raise(self, amount):
        """Handle when a player raises to a specific amount"""

        self.sound_manager.play_poker_chip()

        other_player = self.player2 if self.current_player == self.player1 else self.player1

        # Track the number of raises in the current betting round
        if not hasattr(self, 'raise_count'):
            self.raise_count = 0

        # Standard rule: Maximum of 3 or 4 total bets (initial bet + 3 raises)
        MAX_RAISES = 3  # Most common house rule

        # Check if maximum raises have been reached
        if self.raise_count >= MAX_RAISES:
            # Set status message for max raises
            self.status_message = "Maximum raises reached in this betting round."
            return False

        # Determine the maximum possible raise based on all-in status
        max_possible_raise = other_player.balance + other_player.current_bet if other_player.is_all_in else self.current_player.balance + self.current_player.current_bet

        # Calculate the amount to add to the pot
        pot_addition = amount - self.current_player.current_bet

        # Validate the raise amount with specific error messages
        if amount <= other_player.current_bet:
            # Raise must be higher than current bet
            self.status_message = f"Raise must be higher than ${other_player.current_bet}"
            return False

        if amount > max_possible_raise:
            # Not enough balance for the raise
            self.status_message = f"Insufficient funds. Max raise is ${max_possible_raise}"
            return False

        # Check if this is an all-in
        if amount >= self.current_player.balance + self.current_player.current_bet:
            amount = self.current_player.balance + self.current_player.current_bet
            self.current_player.is_all_in = True
            self.status_message = f"Player {1 if self.current_player == self.player1 else 2} is ALL IN!"

        # Add to pot and update player's bet
        self.pot += pot_addition
        result = self.current_player.place_bet(amount)

        # Increment raise count
        self.raise_count += 1

        # Switch to the other player's turn
        self.switch_turn()
        return True

    def handle_check(self):
        """Handle when a player checks"""
        # Only allow check if current bets are equal
        if self.player1.current_bet == self.player2.current_bet:
            # Switch to the other player
            self.switch_turn()

            # In preflop, if big blind checks and it's now the dealer's turn, advance to flop
            if self.game_state == STATE_PREFLOP and self.current_player == self.current_dealer:
                print("DEBUG: Advancing from preflop after big blind check")
                # Explicitly deal flop and change game state
                self.flop()
                self.game_state = STATE_FLOP
                # Big blind acts first after the flop
                self.current_player = self.current_bigblind
                # Reset bets
                self.player1.current_bet = 0
                self.player2.current_bet = 0
                return

            # Check if we've returned to the original starting player in other rounds
            if self.current_player == (
                    self.current_dealer if self.game_state == STATE_PREFLOP else self.current_bigblind
            ):
                # Advance to next game state
                self.advance_game_state()

        else:
            # Show error or prevent checking
            self.status_message = "Cannot check when there's an active bet"
            print("Cannot check when there's an active bet")

    def handle_showdown(self):
        """Handle the showdown at the end of the hand"""
        # Make all cards visible for showdown
        self.player1.cards_visible = True
        self.player2.cards_visible = True

        # Use the game over handler to determine winner
        winner, message = self.game_over_handler.handle_showdown(
            self.player1, self.player2, self.community_cards, self.pot
        )

        # Update game state
        self.pot = 0

        # Modify the message to include the specific player
        if winner == self.player1:
            self.status_message = "Player 1 " + message
        elif winner == self.player2:
            self.status_message = "Player 2 " + message
        else:
            self.status_message = message

        # Check if either player is out of money
        if self.player1.balance <= 0 or self.player2.balance <= 0:
            # Game over due to bankruptcy
            if self.player1.balance <= 0:
                self.status_message = "GAME OVER - Player 2 Wins! Press ESC to exit"
                self.game_state = STATE_LOST
            else:
                self.status_message = "GAME OVER - Player 1 Wins! Press ESC to exit"
                self.game_state = STATE_LOST
        else:
            self.game_state = STATE_GAME_OVER

        self.winner = winner

    def advance_game_state(self):
        """Move to the next phase of the game"""
        # Reset raise count when moving to a new betting round
        if hasattr(self, 'raise_count'):
            del self.raise_count

        # Check if both players are all-in or one player is all-in
        if (self.player1.is_all_in and self.player2.current_bet == self.player1.current_bet) or (self.player2.is_all_in and self.player1.current_bet == self.player2.current_bet):
            # Deal all remaining community cards at once
            while len(self.community_cards.hand.cards) < 5:
                self.community_cards.hand.add_card(self.deck.deal())

            # Skip to showdown
            self.game_state = STATE_SHOWDOWN
            self.handle_showdown()
            return

        # Reset bets for the new round
        self.player1.current_bet = 0
        self.player2.current_bet = 0

        if self.game_state == STATE_PREFLOP:
            # Deal the flop
            self.flop()
            self.game_state = STATE_FLOP
            # Big blind acts first after the flop
            self.current_player = self.current_bigblind

        elif self.game_state == STATE_FLOP:
            # Deal the turn
            self.turn()
            self.game_state = STATE_TURN
            # Big blind acts first
            self.current_player = self.current_bigblind

        elif self.game_state == STATE_TURN:
            # Deal the river
            self.river()
            self.game_state = STATE_RIVER
            # Big blind acts first
            self.current_player = self.current_bigblind

        elif self.game_state == STATE_RIVER:
            # Go to showdown
            self.game_state = STATE_SHOWDOWN
            self.handle_showdown()

    def switch_turn(self):
        """Switch to the other player's turn"""
        self.current_player.cards_visible = False  # hide cards first

        # Clear the status message when switching turns
        self.status_message = ""

        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1

    def switch_dealer(self):
        """Switch the dealer to the other player"""

        if self.current_dealer == self.player1:
            self.current_dealer = self.player2
            self.current_bigblind = self.player1
        else:
            self.current_dealer = self.player1
            self.current_bigblind = self.player2

    def reset_game(self):
        """Reset the game to its initial state"""
        # reset bg music to play from beginning
        self.sound_manager.stop_bg_music()
        self.sound_manager.play_bg_music()

        # setup deck
        self.deck = Deck()
        self.deck.shuffle()

        # Reset players
        self.player1.reset_for_new_hand()
        self.player2.reset_for_new_hand()
        self.community_cards.hand = Hand()

        # switching dealers after each round
        self.switch_dealer()

        # Check if players can afford blinds
        if self.current_dealer.balance < self.small_blind or self.current_bigblind.balance < self.big_blind:
            # Game over due to insufficient funds
            if self.current_dealer.balance < self.small_blind:
                self.status_message = "GAME OVER - Dealer cannot afford small blind! Press ESC to exit"
                self.game_state = STATE_LOST
            else:
                self.status_message = "GAME OVER - Big Blind cannot afford big blind! Press ESC to exit"
                self.game_state = STATE_LOST
            return

        # Reset pot
        self.pot = 0

        # Clear status message
        self.status_message = ""

        # Deal initial cards
        self.player1.hand.add_card(self.deck.deal())
        self.player1.hand.add_card(self.deck.deal())
        self.player2.hand.add_card(self.deck.deal())
        self.player2.hand.add_card(self.deck.deal())

        # Set initial game state
        self.game_state = STATE_PREFLOP

        # Put blinds in for the new hand
        self.put_blinds_in()

        # First to act in preflop is the dealer (small blind)
        self.current_player = self.current_dealer

    def set_blinds(self, screen):
        """Set blinds with input"""
        self.small_blind = InputHandler.get_numeric_input(
            screen,
            "Enter Small Blind Amount:",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            min_value=1,
            max_value=min(self.player1.balance, self.player2.balance) // 2  # Reasonable max
        )
        if self.small_blind is not None:
            # setting big blind to twice of small blind
            self.big_blind = self.small_blind * 2

    def put_blinds_in(self):
        """Put blinds in, calculate for bet and pot"""

        # Deduct small blind from dealer
        self.current_dealer.balance -= self.small_blind
        self.current_dealer.current_bet = self.small_blind

        # Deduct big blind from big blind player
        self.current_bigblind.balance -= self.big_blind
        self.current_bigblind.current_bet = self.big_blind

        # Update pot with blinds
        self.pot = self.small_blind + self.big_blind

        # First to act in preflop is the dealer (small blind) (just to be safe)
        self.current_player = self.current_dealer

    def flop(self):
        """Deal 3 cards for flop"""
        self.community_cards.hand.add_card(self.deck.deal())
        self.community_cards.hand.add_card(self.deck.deal())
        self.community_cards.hand.add_card(self.deck.deal())

    def turn(self):
        """Deal 1 card for turn"""
        self.community_cards.hand.add_card(self.deck.deal())

    def river(self):
        """Deal 1 card for river"""
        self.community_cards.hand.add_card(self.deck.deal())


def main():
    """Entry point for multiplayer poker game"""
    print('Multiplayer Poker Setup')
    print('1. Host Game')
    print('2. Join Game')

    choice = input('Select mode (1/2): ')

    game = MultiplayerPokerGame(
        is_server=choice == '1',
        server_ip=input('Server IP: ') if choice == '2' else None
    )
    game.run()


if __name__ == '__main__':
    main()