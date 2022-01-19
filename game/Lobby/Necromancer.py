from .Player import Player

class Necromancer(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            'as_player': [
                (1, 3),
                (2, 3)
            ],
            'as_enemy': [
                (3, 0),
                (2, 0)
            ]
        }
        self.Description = """
        Coming Soon
        """

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)