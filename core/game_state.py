# core/game_state.py
class GameState:
    def __init__(self):
        self.current = "menu"

    def set_state(self, new_state):
        self.current = new_state
