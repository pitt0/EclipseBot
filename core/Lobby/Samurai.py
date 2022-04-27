from .Player import Player, AS, Position

class Samurai(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            AS.Player: [
                Position(0, 2),
                Position(1, 2)
            ],
            AS.Enemy: [
                Position(4, 1),
                Position(3, 1)
            ]
        }
        self.Description = """
        Coming Soon
        """

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)
    
    def RestoreStamina(self):
        return

    