from .Player import Player

class Wizard(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            'as_player': [
                (0, 3),
                (1, 3)
            ],
            'as_enemy': [
                (4, 0),
                (3, 0)
            ]
        }
        self.Description = """
        Among many primitive peoples, a wizard was an important person who performed sacred functions of soothsayer and healer
        _Do not meddle in the affairs of Wizards, for they are subtle and quick to anger._ - J. R. R. Tolkien
        """
    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)