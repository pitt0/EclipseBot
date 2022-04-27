from typing import TYPE_CHECKING

from .weapon import Weapon
from core.Resources import *

if TYPE_CHECKING:
    from core.Lobby import Player

__all__ = ('DimensionalSphere',)

class DimensionalSphere(Weapon):

    Brief = "Increased Intelligence|Kit focused on Multi Target"
    cost = 500
    __slots__ = ()

    def __init__(self, character):
        super().__init__(
            character=character,
            shield=0,
            wImage="https://w-dog.pw/android-wallpapers/1/84/436445688767469/sci-fi-planet-purple-stranger.jpg",
            hImage="https://cdn.discordapp.com/attachments/668204203960696836/866133100248694814/54ae6f190c7577953c3065f3a57d2c73.jpg",
            Health=1.1,
            Intelligence=1.1
        )

        # self.Type = EWeaponType.Shadowed
        # self.Description
        self.Abilities = (
            self._base_attack,
            Ability(
                'Star Call',
                'You flash an intense Star light to your target.',
                f'You flash an intense Star light to your target, dealing {self.User.Intelligence * 1.12:.0f} damage _(112% of your `Intelligence`)_ and `Blinding` them for 2 turns\n\n_30 Stamina_',
                30, CostType.Stamina,
                self.StarCall,
                1
            ),
            Ability(
                'Dark Shot',
                'You throw a bunch of Dark Matter to your target.',
                f'You throw a bunch of Dark Matter to your enemy dealing {self.User.Intelligence * 1.1:.0f} damage _(110% of your `Intelligence`)_ and `Burning` them for 1% of their `Health` for 3 turns\n\n_50 Stamina_',
                50, CostType.Stamina,
                self.DarkShot,
                1
            ),
            Ability(
                'Dimensional Dismantling',
                'You Confuse your target halving their `Perception`, then attack them.',
                f'You create an Illusional Dimension to confuse your target, whose `Perception` is now halved, then you attack them dealing {self.User.Strength * 0.7 + self.User.Intelligence * 0.3:.0f} damage _(70% of your `Strength` + 30% of your `Intelligence`)_\n\n_37 Stamina_',
                37, CostType.Stamina,
                self.DimensionalDismantling,
                1
            ),
            Ability(
                'Singularity',
                'You create a Gravity cage to bound your target.',
                f'You create a Gravity cage to bound your target dealing {self.User.Intelligence * 0.8 + self.User.cHealth * 0.1:.0f} damage _(80% of your `Intelligence` + 10% of your `Current Health`)_\n\n_67 Stamina_',
                67, CostType.Stamina,
                self.Singularity,
                1
            )
        )

    def StarCall(self, target: 'Player', _):
        self.User.cStamina -= self.Abilities[1].cost
        target.AddStatus(EStatus.Blinded, 2)
        damage = self.User.Intelligence * 1.12
        output = target.TakeDamage(round(damage), EDamage.Ability)

        log = f"{self.User.name} used `Star Call` on {target.name}, dealing {output} damage and `Blinding` them for 2 turns.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def DarkShot(self, target: 'Player', _):
        self.User.cStamina -= self.Abilities[2].cost
        wound = target.Health * 0.01
        target.AddWound(self.User, round(wound), 3, EWound.Burn)
        damage = self.User.Intelligence * 1.1
        output = target.TakeDamage(round(damage), EDamage.Ability)
        
        log = f"{self.User.name} used `Dark Shot` on {target.name} and dealt {output} damage. {target.name} is now `Burnt` and will suffer {wound:.0f} damage for three turns.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def DimensionalDismantling(self, target: 'Player', _):
        self.User.cStamina -= self.Abilities[3].cost
        p = target.Perception
        target.Perception /= 2.0
        damage = self.User.Strength * 0.7 + self.User.Intelligence * 0.3
        output = target.TakeDamage(round(damage), EDamage.Ability)
        target.Perception = p

        log = f"{self.User.name} used `Dimensional Dismantling` on {target.name} halving their `Perception` for this attack and dealing {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def Singularity(self, target: 'Player', _):
        self.User.cStamina -= self.Abilities[4].cost

        damage = self.User.Intelligence * 0.8 + self.User.cHealth * 0.1
        output = target.TakeDamage(round(damage), EDamage.Ability)

        log = f"{self.User.name} used `Singularity` on {target.name} dealing {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log
