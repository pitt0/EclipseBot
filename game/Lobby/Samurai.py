from .Player import Player

class Samurai(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            'as_player': [
                (0, 2),
                (1, 2)
            ],
            'as_enemy': [
                (4, 1),
                (3, 1)
            ]
        }
        self.Description = """
        Coming Soon
        """

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)
    
    def RestoreStamina(self):
        return

    