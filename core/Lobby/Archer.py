from .Player import Player, AS, Position

class Archer(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            AS.Player: [
                Position(1, 3),
                Position(2, 3),
                Position(3, 3)
            ],
            AS.Enemy: [
                Position(3, 0),
                Position(2, 0),
                Position(1, 0)
            ]
        }
        self.Description = """
        _The archer is the true weapon; the bow is just a long piece of wood. - Sebastien de Castell_
        """

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)