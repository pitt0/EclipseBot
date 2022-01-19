from typing import TYPE_CHECKING

import random

from ..weapon import Weapon
from ...Resources import *

if TYPE_CHECKING:
    from ...Lobby import Player

__all__ = ('MalletOfTheFallen')

class MalletOfTheFallen(Weapon):

    Brief = "Increased Strength | Decreased Intelligence"
    cost = 500
    __slots__ = ()

    def __init__(self, character):
        super().__init__(
            character=character,
            shield=26,
            wImage="https://i.pinimg.com/236x/c0/fc/fb/c0fcfb10b9802e7de91e61074a8d7511.jpg",
            hImage="https://cdn.discordapp.com/attachments/668204203960696836/866132835848159272/4025127dbd0be305959cbbc449f20097.jpg",
            Strength=1.2,
            Intelligence=0.9,
            Armor=0.8,
            Speed=0.4
        )

        # self.Type = EWeaponType.Titanic
        # self.Description
        self.Abilities = {
            "Hammer Shock": {
                "Brief": "You club the target with your Mallet",
                "Description": f"You club the target with your Mallet, dealing {self.User.Strength * 0.8:.0f} damage _(80% of your `Strength`)_ and reducing target's `Armor` by 12\n_This ability can `Critically Strike` for {self.User.CritDamage:.2%} of the damage_\n\n_31 Stamina_",
                "Stamina": 31,
                "Callable": self.HammerShock,
                "Targets": 1
            },
            "Rock Throwing": {
                "Brief": "You use your Mallet to throw some rocks and boulders to the target",
                "Description": f"You use your Mallet to throw some rocks and boulders to the target dealing from {self.User.Strength * 0.99:.0f} to {self.User.Strength * 1.17:.0f} damage _(from 99% to 117% of your `Strength`)_\n\n_37 Stamina_",
                "Stamina": 37,
                "Callable": self.RockThrowing,
                "Targets": 1
            },
            "Mallet Hurl": {
                "Brief": "You hurl your Mallet to the target",
                "Description": f"You hurl your Mallet to the target dealing {self.User.Strength * 1.1:.0f} _(110% of your `Strength`)_ | The lower target's `Armor` is the higher damage becomes.\n\n_43 Stamina_",
                "Stamina": 43,
                "Callable": self.MalletHurl,
                "Targets": 1
            },
            "Dragon Hammer": {
                "Brief": "You enlight your Mallet with magic fire, bounce at your target and club them",
                "Description": f"You enlight your Mallet with magic fire, bounce at your target `Burning` them for 3 damage every turn for 3 turns and clubbing them dealing {self.User.Strength * 0.9 + self.User.Intelligence * 0.3} _(90% of your Strength + 30% of your Intelligence)_\n\n_32 Stamina_",
                "Stamina": 32,
                "Callable": self.DragonHammer,
                "Targets": 1
            }
        }

    def HammerShock(self, target: 'Player', *args, **kwargs):
        self.User.cStamina -= self.Abilities["Hammer Shock"]["Stamina"]
        target.Armor -= 12

        crit = random.randint(0, 100)
        critical = crit <= self.User.CritChance
        damage = self.User.Strength * 0.8
        damage *= self.User.CritDamage if critical else 1
        output = target.TakeDamage(damage, EDamage.Ability)

        if critical:
            log = f"{self.User.name} used `Hammer Shock` on {target.name} and scored a `Critical Strike` dealing {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        else:
            log = f"{self.User.name} used `Hammer Shock` on {target.name} and dealt {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log + f"\n{target.name}'s `Armor` decreased by 12"

    def RockThrowing(self, target: 'Player', *args, **kwargs):
        self.User.cStamina -= self.Abilities["Rock Throwing"]["Stamina"]
        damage = self.User.Strength * 0.9 * random.choice((1.1, 1.2, 1.3))
        output = target.TakeDamage(damage, EDamage.Ability)

        log = f"{self.User.name} used `Rock Throwing` on {target.name} and dealt {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def MalletHurl(self, target: 'Player', *args, **kwargs):
        self.User.cStamina -= self.Abilities["Mallet Hurl"]["Stamina"]
        damage = self.User.Strength * 1.1 * 150/target.Armor
        output = target.TakeDamage(damage, EDamage.Ability)

        log = f"{self.User.name} used `Mallet Hurl` on {target.name} and dealt {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def DragonHammer(self, target: 'Player', *args, **kwargs):
        self.User.cStamina -= self.Abilities["Dragon Hammer"]["Stamina"]
        target.AddWound(self.User, 9, 3, EWound.Burn)

        damage = self.User.Strength * 0.9 + self.User.Intelligence * 0.3
        output = target.TakeDamage(round(damage), EDamage.Ability)

        log = f"{self.User.name} has used `Dragon Hammer` on {target.name} dealing {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log + f"\n{target.name} is now `Burnt` and will suffer 9 damage for 3 turns"
