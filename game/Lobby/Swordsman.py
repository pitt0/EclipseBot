from .Player import Player

class Swordsman(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            'as_player': [
                (1, 2)
            ],
            'as_enemy': [
                (3, 1)
                ]
        }
        self.Description = """
        _The master swordsman isn't interested in killing people. He only wants to perfect his arts._ -Helen DeWitt
        """

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)