"""Heads Down! A two player Texas Hold'em poker game"""
__version__ = '05/22/2025'
__author__ = 'Kayla Cao'

#flint sessions
#https://app.flintk12.com/activities/pygame-project-260f9d/sessions/3e431a2d-b733-48c5-997f-21943aba0496
#https://app.flintk12.com/activities/pygame-debug-le-1fe068/sessions/42d7c71b-fb7b-43f5-91ad-98d8035f60b4
#https://app.flintk12.com/activities/pygame-debug-le-1fe068/sessions/eae6e9bb-5ded-4a29-b415-8952857b466d
#https://app.flintk12.com/activities/pygame-debug-le-1fe068/sessions/796c4af8-acf1-45f6-84db-6af5034893f6
#https://app.flintk12.com/activities/pygame-debug-le-1fe068/sessions/534c9756-0ff5-43bb-9ff8-541797717244

#Notes:
# ADD DOCUMENTATION
# add logging in console for each action that is made and at the end of the game what each player's hand was and what the community cards on the table were
# implement sound

import pygame
import os
import sys

from config import *
from deck import Deck  # Import Deck from deck.py
from hand import Hand  # Import Hand from hand.py
from player import Player
from input_handler import InputHandler
from button import Button
from hand_evaluator import HandEvaluator
from game_over_handler import GameOverHandler
from sounds import *

# Initialize pygame
pygame.init()

class Game:
    def __init__(self):
        """initialization"""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Heads Down!")

        # Load card images
        self.card_images = {}
        self.load_card_images()

        # making players
        self.player1 = Player(1)
        self.player2 = Player(2)
        self.community_cards = Player(3)  # considered a "player" since it has a "hand"
        self.community_cards.cards_visible = True  # community cards should always be face up

        # pot
        self.pot = 0

        # initialize hand evaluator
        self.hand_evaluator = HandEvaluator()

        # Initialize game over handler
        self.game_over_handler = GameOverHandler()

        # Initialize sound manager
        self.sound_manager = SoundManager() 

        # Add status message display
        self.status_message = ""

        # blinds
        self.small_blind = 0
        self.big_blind = 0

        # Set initial dealer and big blind
        #this is opposite since in self.reset() we call switch dealer which changes it
        self.current_player = self.player2
        self.current_dealer = self.player2
        self.current_bigblind = self.player1

        self.game_state = STATE_PREFLOP

        # Create font objects
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)

        # Create buttons
        self.buttons = pygame.sprite.Group()

        # Create button font
        self.button_font = pygame.font.SysFont(None, 24)

        # Create buttons
        self.p1_cards_button = Button(50, 550, 80, 40, "P1 Cards", self.button_font)
        self.p2_cards_button = Button(150, 550, 80, 40, "P2 Cards", self.button_font)
        self.call_button = Button(250, 550, 80, 40, "Call", self.button_font)
        self.raise_button = Button(350, 550, 80, 40, "Raise", self.button_font)
        self.fold_button = Button(450, 550, 80, 40, "Fold", self.button_font)
        self.check_button = Button(550, 550, 80, 40, "Check", self.button_font)
        self.play_again_button = Button(SCREEN_WIDTH // 2 - 60, 400, 120, 40, "Play Again", self.button_font)

        # Add buttons to group
        self.buttons.add(
            self.p1_cards_button,
            self.p2_cards_button,
            self.call_button,
            self.raise_button,
            self.fold_button,
            self.check_button,
            self.play_again_button,
        )

    def load_card_images(self):
        """Load all card images from the 'img' folder"""
        image_dir = 'img'

        # Try to load card back image (using red_back.png from folder)
        try:
            back_path = os.path.join(image_dir, 'red_back.png')
            if os.path.exists(back_path):
                self.card_back = pygame.image.load(back_path)
                self.card_back = pygame.transform.scale(self.card_back, (CARD_WIDTH, CARD_HEIGHT))
            else:
                print(f"Warning: Card back image not found at {back_path}")
                # Create a default card back
                self.card_back = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
                self.card_back.fill((0, 0, 128))  # Navy blue
        except pygame.error as e:
            print(f"Error loading card back: {e}")
            # Create a default card back
            self.card_back = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            self.card_back.fill((0, 0, 128))  # Navy blue

        # Define card values and suits for filenames
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
        suits = ['clubs', 'diamonds', 'hearts', 'spades']

        # Load each card image or create a default
        for suit in suits:
            for value in values:
                filename = f"{value}_of_{suit}.png"
                try:
                    path = os.path.join(image_dir, filename)
                    if os.path.exists(path):
                        img = pygame.image.load(path)
                        img = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
                    else:
                        print(f"Warning: Card image not found: {filename}")
                        # Create a default card image
                        img = self.create_default_card(value, suit)
                    self.card_images[filename] = img
                except pygame.error as e:
                    print(f"Error loading {filename}: {e}")
                    # Create a default card image
                    img = self.create_default_card(value, suit)
                    self.card_images[filename] = img

    def create_default_card(self, value, suit):
        """Create a default card image if the image file is missing"""
        img = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        img.fill((255, 255, 255))  # White background

        # Add a border
        pygame.draw.rect(img, (0, 0, 0), (0, 0, CARD_WIDTH, CARD_HEIGHT), 2)

        # Add text for value and suit
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"{value.upper()} of {suit.capitalize()}", True, (0, 0, 0))
        text_rect = text.get_rect(center=(CARD_WIDTH // 2, CARD_HEIGHT // 2))
        img.blit(text, text_rect)

        return img

    def reset_game(self):
        """Reset the game to its initial state"""
        # reset bg music to play from beginning
        self.sound_manager.stop_bg_music()
        self.sound_manager.play_bg_music()

        #setup deck
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
            max_value=min(self.player1.balance, self.player2.balance)//2  # Reasonable max
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

        #play poker chip sound
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

    def draw_card(self, card, x, y, player):
        """Draw a card at the specified position"""
        # Determine if this player is the current player
        is_current_player = (player == self.current_player)

        if player.cards_visible:
            filename = card.get_image_filename()
            if filename in self.card_images:
                card_image = self.card_images[filename].copy()
            else:
                # If image not found, create a default card
                card_image = self.create_default_card(
                    str(card.raw_value) if card.raw_value <= 10 else card.name.split()[0].lower(),
                    card.suit.lower()
                )
        else:
            # Use card back
            card_image = self.card_back.copy()

        # Add yellow border if it's the current player's turn
        if is_current_player:
            pygame.draw.rect(card_image, (255, 255, 0), card_image.get_rect(), 5)  # 5-pixel yellow border

        # Blit the card (with or without border)
        self.screen.blit(card_image, (x, y))

    def draw_hand(self, hand, x, y, player):
        """Draw all cards in a hand"""
        for i, card in enumerate(hand.cards):
            self.draw_card(card, x + i * 60, y, player)

    def draw_game(self):
        """Draw everything in the game"""
        # Fill background
        self.screen.fill(BACKGROUND_COLOR)

        # Draw player info
        p1_balance_text = self.font.render(f"Player 1: ${self.player1.balance}", True, TEXT_COLOR)
        p1_bet_text = self.font.render(f"Bet: ${self.player1.current_bet}", True, TEXT_COLOR)
        self.screen.blit(p1_balance_text, (50, 50))
        self.screen.blit(p1_bet_text, (50, 80))

        p2_balance_text = self.font.render(f"Player 2: ${self.player2.balance}", True, TEXT_COLOR)
        p2_bet_text = self.font.render(f"Bet: ${self.player2.current_bet}", True, TEXT_COLOR)
        self.screen.blit(p2_balance_text, (50, 320))
        self.screen.blit(p2_bet_text, (50, 350))

        # Draw whose turn it is
        if self.current_player == self.player1:
            turn_text = self.font.render("Player 1's Turn", True, (255, 255, 0))
        elif self.current_player == self.player2:
            turn_text = self.font.render("Player 2's Turn", True, (255, 255, 0))
        else:
            turn_text = self.font.render("Game Over", True, (255, 255, 0))
        self.screen.blit(turn_text, (SCREEN_WIDTH // 2 - 80, 10))

        community_cards_text = self.font.render("Community Cards", True, TEXT_COLOR)
        self.screen.blit(community_cards_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 80))

        # Draw hands
        self.draw_hand(self.player1.hand, 50, 110, self.player1)
        self.draw_hand(self.player2.hand, 50, 380, self.player2)

        # Draw community cards
        self.draw_hand(self.community_cards.hand, 250, SCREEN_HEIGHT // 2-50, self.community_cards)

        if self.status_message:
            status_font = pygame.font.SysFont(None, 36)
            status_text = status_font.render(self.status_message, True, (255, 255, 0))  # Yellow text
            status_rect = status_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
            self.screen.blit(status_text, status_rect)

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()

        if self.game_state != STATE_GAME_OVER and self.game_state != STATE_LOST:
            for button in self.buttons:
                if button != self.play_again_button:
                    button.render(button.is_hovered(mouse_pos))
                    button.draw(self.screen)
        elif self.game_state == STATE_GAME_OVER:
            # Only draw Play Again button when game is over
            self.play_again_button.render(self.play_again_button.is_hovered(mouse_pos))
            self.play_again_button.draw(self.screen)

            # Only add pot if winner exists and is not None
            if self.winner:
                self.winner.balance += self.pot
                self.pot = 0  # Ensure pot is reset after distribution

        # Add pot display
        pot_text = self.font.render(f"Pot: ${self.pot}", True, TEXT_COLOR)
        self.screen.blit(pot_text, (SCREEN_WIDTH // 2 - 50, 70))

    def run(self):
        """Main game loop"""
        running = True
        clock = pygame.time.Clock()

        # Initial setup
        self.player1.set_balance(self.screen, "player 1's")
        self.player2.set_balance(self.screen, "player 2's")

        # Prompt for blinds at the start
        self.set_blinds(self.screen)

        # Initial game reset will handle first hand's blinds
        self.reset_game()

        while running:
            # Draw everything
            self.draw_game()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                # Handle mouse clicks
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if self.game_state != STATE_GAME_OVER:
                        # p1 cards button
                        if self.p1_cards_button.is_hovered(mouse_pos):
                            if self.current_player == self.player1:
                                self.player1.cards_visible = not self.player1.cards_visible

                        # p2 cards button
                        elif self.p2_cards_button.is_hovered(mouse_pos):
                            if self.current_player == self.player2:
                                self.player2.cards_visible = not self.player2.cards_visible

                        # call button
                        elif self.call_button.is_hovered(mouse_pos):
                            if self.player1.current_bet > 0 or self.player2.current_bet > 0:
                                self.handle_call()

                        # raise button
                        elif self.raise_button.is_hovered(mouse_pos):

                            # Get the raise amount
                            raise_amount = self.current_player.player_bet(self.screen)

                            if raise_amount is not None:
                                # Call the raise method
                                result = self.handle_raise(raise_amount)

                        # Fold button
                        elif self.fold_button.is_hovered(mouse_pos):
                            self.handle_fold()

                        # Check button
                        elif self.check_button.is_hovered(mouse_pos):
                            self.handle_check()

                    # Play Again button (if game over)
                    elif ((self.game_state == STATE_GAME_OVER or self.game_state == STATE_LOST) and
                          self.play_again_button.is_hovered(mouse_pos)):
                        # Only allow play again if not in final lost state
                        if self.game_state == STATE_GAME_OVER:
                            self.reset_game()

            # Update display
            pygame.display.flip()

            # Cap the frame rate
            clock.tick(30)

        pygame.quit()
        sys.exit()

# Run the game if this file is executed directly
if __name__ == "__main__":
    game = Game()
    game.run()