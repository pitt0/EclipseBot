from typing import TYPE_CHECKING

import random

from ..weapon import Weapon
from ...Resources import *

if TYPE_CHECKING:
    from ...Lobby import Player

__all__ = ('LifeStoneShield')

class LifeStoneShield(Weapon):

    Brief = "Increased Defenses | Optimal in Team Fights"
    cost = 500
    __slots__ = ()

    def __init__(self, character):
        super().__init__(
            character=character,
            shield=32,
            wImage="https://cdn.discordapp.com/attachments/866261896600354846/876849117429645382/3ad21268824811.5b6ac036b1930.jpg",
            hImage="https://i.pinimg.com/564x/ac/cc/f9/acccf9d587f346ecdca65081bb8ba38e.jpg",
            Intelligence=1.3,
            Armor=0.8
        )

        self.BA = f"Deals {self.User.Strength + self.User.Armor * 0.2:.0f} damage _(100% of you `Strength` + 20% of your `Armor`)_"
        # self.Description
        self.Abilities = {
            "Taunt" : {
                "Brief": "You become `Targeted`",
                "Description": "You become `Targeted`, freeing your whole team from being `Targeted`\n\n_12 Stamina_",
                "Stamina": 12,
                "Callable": self.Taunt,
                "Targets": 0,
            },
            "Shield Blow": {
                "Brief": "You charge your target with your Shield",
                "Description": f"You charge your target with your Shield, dealing {self.User.Strength * 0.6 + self.User.Armor * 0.5:.0f} damage _(60% of your `Strength` + 50% of your `Armor`)_\n\n_32 Stamina_",
                "Stamina": 32,
                "Callable": self.ShieldBlow,
                "Targets": 1,
            },
            "Rise": {
                "Brief": "You empower yourself or one of your allies",
                "Description": "You empower yourself or onw of your allies increasing empowered's `Perception` by 7 and `Strength` by 3\n_16 Stamina_",
                "Stamina": 16,
                "Callable": self.Rise,
                "Targets": 1,
            },
        }

    def BaseAttack(self, target: 'Player'):
        crit = random.randint(0, 100)
        critical = crit <= self.User.CritChance
        damage = self.User.Strength + self.User.Armor * 0.2
        damage *= self.User.CritDamage if critical else 1
        output = target.TakeDamage(damage, EDamage.BaseAttack)

        log = f"{self.User.name} attacked {target.name} daling {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def Taunt(self, target: 'Player', allies: list['Player']):
        self.User.cStamina -= self.Abilities["Taunt"]["Stamina"]
        for ally in allies:
            if ally.CheckStatus(EStatus.Targeted):
                ally.RemoveStatus(EStatus.Targeted)
        self.User.AddStatus(EStatus.Targeted, 1)

        log = f"{self.User.name} used `Taunt`. For the next turn they will be `Targeted`."
        return log

    def ShieldBlow(self, target: 'Player', allies: list['Player']):
        self.User.cStamina -= self.Abilities["Shield Blow"]["Stamina"]

        damage = self.User.Strength * 0.6 + self.User.Armor * 0.5
        output = target.TakeDamage(damage, EDamage.Ability)

        log = f"{self.User.name} used `Shield Blow` on {target.name}, dealing them {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def Rise(self, target: 'Player', *args, **kwargs):
        self.User.cStamina -= self.Abilities["Rise"]["Stamina"]
        target.Perception += 7; target.Strength += 3

        log = f"{self.User.name} used `Rise` on {target.name} and increased their `Perception` by 7 and their `Strength` by 3"
        return log
