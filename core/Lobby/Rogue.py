from .Player import Player, AS, Position

class Rogue(Player):
    
    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            AS.Player: [
                Position(0, 2),
                Position(0, 3),
                Position(4, 2),
                Position(4, 3)
            ],
            AS.Enemy: [
                Position(4, 1),
                Position(4, 0),
                Position(0, 1),
                Position(0, 0)
            ]
        }
        self.Description = """
        _A thread will tie an honest man better than a chain a rogue._
        """

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)