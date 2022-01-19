from .Player import Player

class Rogue(Player):
    
    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            'as_player': [
                (0, 2),
                (0, 3),
                (4, 2),
                (4, 3)
            ],
            'as_enemy': [
                (4, 1),
                (4, 0),
                (0, 1),
                (0, 0)
            ]
        }
        self.Description = """
        _A thread will tie an honest man better than a chain a rogue._
        """

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)