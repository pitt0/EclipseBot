from .Player import Player, AS, Position

class Shaman(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            AS.Player: [
                Position(0, 4),
                Position(1, 4)
            ],
            AS.Enemy: [
                Position(4, 0),
                Position(3, 0)
            ]
        }
        self.Description = """
        [Shamanism originated in Siberia, where members of indigenous tribes would gather the sometimes poisonous and highly psychoactive mushroom, Amanita muscaria. Once it was recognized and classified as shamanism, it became apparent many cultures around the world conducted similar practices.](https://www.gaia.com/article/how-much-do-you-know-about-shamanism)\n
        _You don't find light by avoiding the darkness._ - S. Kelley Harrel
        """    

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)