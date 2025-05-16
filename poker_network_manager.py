class PokerNetworkManager(NetworkManager):
    def __init__(self, game, is_server=False, server_ip='127.0.0.1', port=5555):
        super().__init__(is_server, server_ip, port)
        self.game = game  # Reference to the main game object
    
    def _process_message(self, message, sender=None):
        """Handle poker-specific messages"""
        msg_type = message.get('type')
        
        if msg_type == 'action':
            # Handle player actions (bet, fold, etc.)
            action = message.get('action')
            amount = message.get('amount', 0)
            player_id = message.get('player_id')
            
            # Update the game state based on the action
            self.game.handle_remote_action(action, amount, player_id)
            
            # If server, broadcast the updated game state
            if self.is_server:
                self.send_game_state()
        
        elif msg_type == 'game_state':
            # Update local game state with server data
            if not self.is_server:
                self.game.update_from_network(message.get('state'))
    
    def send_action(self, action, amount=0, player_id=0):
        """Send a player action to the server"""
        message = {
            'type': 'action',
            'action': action,
            'amount': amount,
            'player_id': player_id
        }
        self.send_message(message)
    
    def send_game_state(self):
        """Send the current game state to all clients (server only)"""
        if not self.is_server:
            return
            
        message = {
            'type': 'game_state',
            'state': self.game.get_network_state()
        }
        self.send_message(message)