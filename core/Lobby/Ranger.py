from .Player import Player, AS, Position

class Ranger(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            AS.Player: [
                Position(0, 3),
                Position(4, 3)
            ],
            AS.Enemy: [
                Position(4, 0),
                Position(0, 0)
            ]
        }
        self.Description = """
        Coming Soon
        """

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)