from .Player import Player

class Assassin(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            'as_player': [
                (0, 2),
                (4, 2),
                (0, 3),
                (4, 3)
            ],
            'as_enemy': [
                (4, 1),
                (0, 1),
                (4, 0),
                (0, 0)
            ]
        }
        self.Description = """
        [_The Assassins were a heretical group of Shiite Muslims in Persia and Syria from the 11th century CE until their defeat at the hands of the Mongols in the mid-13th century CE. Secure in their fortified hilltop castles, they became infamous for their strategy of singling out opposition figures and murdering them, usually in knife-wielding teams. The group was known as the Assassins by their enemies in reference to their use of hashish, 'assassin' being a corruption of the Arabic hasisi, and so the name has since come to be associated with their chief modus operandi, the act of murder for political or religious purposes._](https://www.worldhistory.org/The_Assassins/)\n
        _Not everything deserves to live - Callum Lynch_
        """

    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)
