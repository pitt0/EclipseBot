from .Player import Player, AS, Position

class Titan(Player):

    def __init__(self, user):
        super().__init__(user)
        self._coordinates = {
            AS.Player: [
                Position(2, 2),
                Position(3, 2)
            ],
            AS.Enemy: [
                Position(2, 1),
                Position(1, 1)
            ]
        }
        self.Description = """
        In Greek mythology, the Titans were the pre-Olympian gods. According to the Theogony of Hesiod, they were the twelve children of the primordial parents Uranus and his mother, Gaia, with six male Titans: Oceanus, Coeus, Crius, Hyperion, Iapetus, and Cronus, and six female Titans, called the Titanides: Theia, Rhea, Themis, Mnemosyne, Phoebe, and Tethys. Cronus mated with his older sister Rhea and together they became the parents of the first generation of Olympians – the six siblings Zeus, Hades, Poseidon, Hestia, Demeter, and Hera.\n
        """
    
    def __eq__(self, __o: object) -> bool:
        return self._user == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)