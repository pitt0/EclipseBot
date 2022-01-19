from .Player import Player

class Cleric(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            'as_player': [
                (2, 3),
                (3, 3),
                (4, 3)
            ],
            'as_enemy': [
                (2, 0),
                (1, 0),
                (0, 0)
            ]
        }
        self.Description = """
        Coming Soon
        """

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)