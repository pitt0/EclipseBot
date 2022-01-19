from .Player import Player

class Magician(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            'as_player': [
                (3, 3),
                (4, 3)
            ],
            'as_enemy': [
                (1, 0),
                (0, 0)
            ]
        }
        self.Description = """
        _What the eyes see and the ears hear, the mind believes._ -Karl Germain
        """

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)