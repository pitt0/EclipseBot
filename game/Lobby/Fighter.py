from .Player import Player

class Fighter(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            'as_player': [
                (1, 2),
                (3, 2)
            ],
            'as_enemy': [
                (3, 1),
                (1, 1)
            ]
        }
        self.Description = """
        Coming Soon
        """

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)