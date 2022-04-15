from typing import TYPE_CHECKING

import random

from .weapon import Weapon
from game.Resources import *

if TYPE_CHECKING:
    from game.Lobby import Player

__all__ = ('MalletOfTheFallen',)

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
        self.Abilities = (
            self._base_attack,
            Ability(
                'Hammer Shock',
                'You club the target with your Mallet',
                f"You club the target with your Mallet, dealing {self.User.Strength * 0.8:.0f} damage _(80% of your `Strength`)_ and reducing target's `Armor` by 12\n_This ability can `Critically Strike` for {self.User.CritDamage:.2%} of the damage_\n\n_31 Stamina_",
                31, CostType.Stamina,
                self.HammerShock, 1
            ),
            Ability(
                'Rock Throwing',
                'You use your Mallet to throw some rocks and boulders to the target',
                f'You use your Mallet to throw some rocks and boulders to the target dealing from {self.User.Strength * 0.99:.0f} to {self.User.Strength * 1.17:.0f} damage _(from 99% to 117% of your `Strength`)_\n\n_37 Stamina_',
                37, CostType.Stamina,
                self.RockThrowing, 1
            ),
            Ability(
                'Mallet Hurl',
                'You hurl your Mallet to the target',
                f"You hurl your Mallet to the target dealing {self.User.Strength * 1.1:.0f} _(110% of your `Strength`)_ | The lower target's `Armor` is the higher damage becomes.\n\n_43 Stamina_",
                43, CostType.Stamina,
                self.MalletHurl, 1
            ),
            Ability(
                'Dragon Hammer',
                'You enlight your Mallet with magic fire, bounce at your target and club them',
                f"You enlight your Mallet with magic fire, bounce at your target `Burning` them for 3 damage every turn for 3 turns and clubbing them dealing {self.User.Strength * 0.9 + self.User.Intelligence * 0.3} _(90% of your Strength + 30% of your Intelligence)_\n\n_32 Stamina_",
                32, CostType.Stamina,
                self.DragonHammer, 1
            )
        )

    def HammerShock(self, target: 'Player', _):
        self.User.cStamina -= self.Abilities[1].cost
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

    def RockThrowing(self, target: 'Player', _):
        self.User.cStamina -= self.Abilities[2].cost
        damage = self.User.Strength * 0.9 * random.choice((1.1, 1.2, 1.3))
        output = target.TakeDamage(damage, EDamage.Ability)

        log = f"{self.User.name} used `Rock Throwing` on {target.name} and dealt {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def MalletHurl(self, target: 'Player', _):
        self.User.cStamina -= self.Abilities[3].cost
        damage = self.User.Strength * 1.1 * 150/target.Armor
        output = target.TakeDamage(damage, EDamage.Ability)

        log = f"{self.User.name} used `Mallet Hurl` on {target.name} and dealt {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def DragonHammer(self, target: 'Player', _):
        self.User.cStamina -= self.Abilities[4].cost
        target.AddWound(self.User, 9, 3, EWound.Burn)

        damage = self.User.Strength * 0.9 + self.User.Intelligence * 0.3
        output = target.TakeDamage(round(damage), EDamage.Ability)

        log = f"{self.User.name} has used `Dragon Hammer` on {target.name} dealing {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log + f"\n{target.name} is now `Burnt` and will suffer 9 damage for 3 turns"
