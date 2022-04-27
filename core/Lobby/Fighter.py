from .Player import Player, AS, Position

class Fighter(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            AS.Player: [
                Position(1, 2),
                Position(3, 2)
            ],
            AS.Enemy: [
                Position(3, 1),
                Position(1, 1)
            ]
        }
        self.Description = """
        Coming Soon
        """

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)