from .Player import Player

class Shaman(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            'as_player': [
                (0, 4),
                (1, 4)
            ],
            'as_enemy': [
                (4, 0),
                (3, 0)
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