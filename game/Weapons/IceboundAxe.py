from typing import TYPE_CHECKING

import random

from .weapon import Weapon
from game.Resources import *

if TYPE_CHECKING:
    from game.Lobby import Player

__all__ = ('IceboundAxe',)

class IceboundAxe(Weapon):

    Brief = 'Increased Strength | Stronger in 1 v 1'
    cost = 500
    __slots__ = ()

    def __init__(self, character):
        super().__init__(
            character=character,
            shield=0,
            wImage='https://cdn.discordapp.com/attachments/668204203960696836/866133180587442176/0b7dfed3f92190af952516f332aa34ac.jpg',
            hImage='https://cdn.discordapp.com/attachments/668204203960696836/866132575050661908/ae7e69b5ca8ae0e5c994298beec9d9f5.jpg',
            Health=1.1,
            Strength=1.1,
            Armor=0.8,
            Intelligence=0.95
        )
        # self.Type = EWeaponType.Nobles

        # self.Description
        self.Abilities = (
            self._base_attack,
            Ability(
                'IceBound Strike',
                'You club your target with your freezed Axe.',
                f'You freeze your Axe and hurl it to the target dealing {self.User.Strength * 1.1:.0f} damage _(110% of your `Strength`)_. This ability has 10% chance to `Stun` the target for two turns\n_This ability can `Critically Strike` for {self.User.CritDamage:.2%} of the damage_\n\n_27 Stamina_',
                27, CostType.Stamina,
                self.IceBoundStrike,
                1
            ),
            Ability(
                'Enforce',
                'You focus to enforce your body.',
                f'You focus to increase your `Perception` by 8 and your `Armor` by 6\n\n_14 Stamina_',
                14, CostType.Stamina,
                self.Enforce,
                0
            ),
            Ability(
                'Blizzard',
                'You call a frost storm to entangle your enemies.',
                f'You call a frost storm to entangle your enemies dealing {self.User.Strength*0.8 + self.User.Intelligence*0.3:.0f} _(80% of your `Strength` + 30% of your `Intelligence`)_\n\n_33 Stamina_',
                33, CostType.Stamina,
                self.Blizzard,
                -1
            ),
            Ability(
                'FrosFire Force',
                'You attack your target with all the strength in your arms.',
                f'You attack your target with all your strength dealing {self.User.Strength * 1.2:.0f} damage _(120% of your `Strength`)_ and lowering your `Strength` by 6\n_This ability can `Critically Strike` for {self.User.CritDamage:.2%} of the damage_\n\n_31 Stamina_',
                31, CostType.Stamina,
                self.FrostFireForce,
                1
            )
        )

    def IceBoundStrike(self, target: 'Player', _):
        self.User.cStamina -= self.Abilities[1].cost

        to_add = ""
        stun = random.randint(0, 100)
        if stun <= 10:
            target.AddStatus(EStatus.Stunned, turns=2)
            to_add = f'\n\n{target.name} has been `Stunned` for two turns.'

        crit = random.randint(0, 100)
        critical = crit <= self.User.CritChance
        damage = self.User.Strength * 1.1
        damage *= self.User.CritDamage if critical else 1        
        output = target.TakeDamage(damage, EDamage.Ability)

        if critical:
            log = f"{self.User.name} has used `IceBound Strike` on {target.name} and scored a `Critical Strike` dealing {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        else:
            log = f"{self.User.name} has used `IceBound Strike` on {target.name} dealing {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log + to_add

    def Enforce(self, _, __):
        self.User.cStamina -= self.Abilities[2].cost
        self.User.Perception += 8; self.User.Armor += 6
        log = f"{self.User.name} has empowered theirself, increasing their `Perception` by 8 and their `Armor` by 6.\n{self.User.name}'s `Perception`: {self.User.Perception}\n{self.User.name}'s `Armor`: {self.User.Armor}"
        return log

    def Blizzard(self, target: list['Player'], _):
        self.User.cStamina -= self.Abilities[3].cost

        damage = self.User.Strength * 0.8 + self.User.Intelligence * 0.3
        for enemy in target:
            enemy.TakeDamage(damage, EDamage.Ability)
        
        log = f"{self.User.name} has used `Blizzard` and hit {', '.join(enemy.name for enemy in target)} dealing {damage:.0f} damage to everyone"
        
        return log

    def FrostFireForce(self, target: 'Player', _):
        self.User.cStamina -= self.Abilities[4].cost

        crit = random.randint(0, 100)
        critical = crit <= self.User.CritChance
        damage = self.User.Strength*1.2
        damage *= self.User.CritDamage if critical else 1
        output = target.TakeDamage(damage, EDamage.Ability)

        self.User.Strength -= 6

        if critical:
            log = f"""{self.User.name} used `FrostFire Force` against {target.name} and scored a `Critical Strike` dealing {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}
            
            {self.User.name} has lost 6 `Strength`. {self.User.name}'s `Strength`: {self.User.Strength}."""
        else:
            log = f"""{self.User.name} used `FrostFire Force` against {target.name} and dealt {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}
            
            {self.User.name} has lost 6 `Strength`. {self.User.name}'s `Strength`: {self.User.Strength}."""
        return log