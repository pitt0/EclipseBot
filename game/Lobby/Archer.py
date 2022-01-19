from .Player import Player

class Archer(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            'as_player': [
                (1, 3),
                (2, 3),
                (3, 3)
            ],
            'as_enemy': [
                (3, 0),
                (2, 0),
                (1, 0)
            ]
        }
        self.Description = """
        _The archer is the true weapon; the bow is just a long piece of wood. - Sebastien de Castell_
        """

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)