from .Player import Player, AS, Position

class Magician(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            AS.Player: [
                Position(3, 3),
                Position(4, 3)
            ],
            AS.Enemy: [
                Position(1, 0),
                Position(0, 0)
            ]
        }
        self.Description = """
        _What the eyes see and the ears hear, the mind believes._ -Karl Germain
        """

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)