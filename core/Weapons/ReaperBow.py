from typing import TYPE_CHECKING

import random

from .weapon import Weapon
from core.Resources import *

if TYPE_CHECKING:
    from core.Lobby import Player

__all__ = ('ReaperBow',)

class ReaperBow(Weapon):

    Brief = "Increased Strength|Focused on Team Fights|Low Defense"
    cost = 500
    __slots__ = ('stacks')

    def __init__(self, character):
        super().__init__(
            character=character,
            shield=0,
            wImage="https://i.pinimg.com/736x/75/64/22/75642266dbe95b2c9c39bf1447474eff--sagittarius-tattoos-fantasy-weapons.jpg",
            hImage="https://cdn.discordapp.com/attachments/668204203960696836/866132772702781440/56f11106983b4c3dc659fd595f4c11b1.jpg",
            Health=0.95,
            Strength=1.1,
            Armor=0.9
        )

        self.stacks: dict[int, int] = {}
        # self.Type = EWeaponType.Shadowed
        self._base_attack.long = self._base_attack.brief = "Deals {self.User.Strength * 0.95:.0f} _(95% of your `Strength`)_ + 5% of your `Strength` per target's `Death` stack and applies 1 `Death` stack. At 4 stacks the target takes 100% of their `Armor` as `Ability` damage and removes all of their `Death` stacks."
        # self.Description
        self.Abilities = (
            self._base_attack,
            Ability(
                'Ghost Link',
                'You shot a Spectral Arrow that pierces the target',
                f"You shot a Spectral Arrow that pierces the target dealing {self.User.Strength * 0.8:.0f} _(80% of your `Strength`)_ + 25% of target's `Armor` and applying 1 `Death` stack\n\n_25 Stamina_",
                25, CostType.Stamina,
                self.GhostLink, 1
            ),
            Ability(
                'Relentless Slinger',
                'You aim at a __vital point__ of the enemy and shoot a Spectral Arrow',
                f"You shoot a Spectral Arrow to a __Vital Point__ of the target dealing {self.User.Strength * 0.9:.0f} _(90% of your `Strength`)_ + 30% of target's `Armor`\n\n_42 Stamina_",
                42, CostType.Stamina,
                self.RelentlessSlinger, 1
            ),
            Ability(
                'Shadow Showdown',
                'You free your Soul in the form of a `Shadow` Arrow, attacking up to three enemies at once',
                f'You attack up to three enemies suffering 34 `Health Points` for each enemy hit, dealing {self.User.Strength * 0.75:.0f} damage _(75% of your `Strength`)_ and lowering their `Strength` by 12 * `Death` stacks on target\n\n_31 Stamina_',
                31, CostType.Stamina,
                self.ShadowShowdown, 3
            ),
            Ability(
                'Ruined Quiver',
                'You let your Bow seize yourself, increasing your damage',
                'You let your Bow seize yourself, increasing your `Strength` by 15 * `Death` stack on the field and taking 23 damage\n\n_31 Stamina_',
                31, CostType.Stamina,
                self.RuinedQuiver, 0
            )
        )

    def BaseAttack(self, target: 'Player'):
        crit = random.randint(0, 100)
        critical = crit <= self.User.CritChance

        stacks = self.stacks.get(target.id, 0)
        to_add = None

        damage = self.User.Strength * (0.95 + (0.5 * stacks))
        damage *= self.User.CritDamage if critical else 1
        output = target.TakeDamage(damage, EDamage.BaseAttack)

        stacks += 1
        if stacks == 4:
            stacks = 0
            output_ = target.TakeDamage(target.Armor, EDamage.Ability)
            to_add = f"\n{self.User.name}'s fourth `Death` stack has been absorbed by their body and they suffered {output_} more damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"

        self.stacks[target.id] = stacks

        log = f"{self.User.name} attacked {target.name} dealing {output} damage.\n{self.User.name}'s `Death` stacks: {self.stacks[target.id]}" + to_add if to_add is not None else f"\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def GhostLink(self, target: 'Player', _):
        self.User.cStamina -= self.Abilities[1].cost
        damage = self.User.Strength * 0.8 + target.Armor * 0.25

        stacks = self.stacks.get(target.id, 0)
        stacks += 1
        if stacks == 4:
            stacks = 0

        self.stacks[target.id] = stacks

        output = target.TakeDamage(damage, EDamage.Ability)

        log = f"{self.User.name} has used `Ghost Link` on {target.name} dealing {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log + f"\n{target.name} got +1 `Death` stack\n{target.name}'s `Death` stacks: {self.stacks[target.id]}."

    def RelentlessSlinger(self, target: 'Player', _):
        self.User.cStamina -= self.Abilities[2].cost
        wound = self.User.Strength * 0.9 + target.Armor * 0.3
        target.AddWound(self.User, round(wound), 1, EWound.Wound)

        log = f"{self.User.name} used `Relentless Slinger` on {target.name}, who will suffer {wound:.0f} `Wound` damage at the end of the turn"
        return log

    def ShadowShowdown(self, target: list['Player'], _):
        self.User.cStamina -= self.Abilities[3].cost
        self.User.TakeDamage(34, EDamage.TrueDamage, False)

        damage = self.User.Strength*0.75
        for t in target:
            t.Strength -= 12 * self.stacks[t.id]
            t.TakeDamage(damage, EDamage.Ability)

        log = f"{self.User.name} used `Shadow Showdown` and hit {', '.join(t.name for t in target)} dealing everyone {damage:.0f} damage and loosing {34*len(target)} `Health Points`."
        return log

    def RuinedQuiver(self, _, __):
        self.User.cStamina -= self.Abilities[4].cost

        self.User.TakeDamage(23, EDamage.TrueDamage, False)

        stacks = 0
        for stack in self.stacks.values():
            stacks += stack
        self.User.Strength += (15 * stacks)
        log = f"{self.User.name} used `Ruined Quiver`, increasing their `Strength` by {15*stacks} and taking 23 damage.\n{self.User.name}'s `Health`: {self.User.cHealth}\n{self.User.name}'s `Strength`: {self.User.Strength}"
        return log