from .Player import Player, AS, Position

class Lancer(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            AS.Player: [
                Position(3, 2),
                Position(4, 2)
            ],
            AS.Enemy: [
                Position(1, 1),
                Position(0, 1)
            ]
        }
        self.Descriprion = """
            [A lancer was a type of cavalryman who fought with a lance. Lances were used for mounted warfare in Assyria as early as 700 BC. The weapon was widely used throughout Europe and Asia during the Middle Ages and the Renaissance by heavy cavalry, before being adopted later on by light cavalry. In a modern context, a lancer regiment usually denotes an armoured unit.](https://en.wikipedia.org/wiki/Lancer)\n
            _What must triumph here is the knight's path of chivalry that we champion_ - Unknown
            """

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)