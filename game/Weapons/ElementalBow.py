from typing import TYPE_CHECKING

import random

from .weapon import Weapon
from game.Resources import *

if TYPE_CHECKING:
    from game.Lobby import Player

__all__ = ('ElementalBow',)

class ElementalBow(Weapon):

    Brief = "Multiple Effects on Attacks | Stronger in team"
    cost = 500
    __slots__ = ("Arrow")

    def __init__(self, character):
        super().__init__(
            character=character,
            shield=0,
            wImage="https://i.pinimg.com/originals/5e/64/67/5e6467c460ed9698069484a44b6c9c24.gif",
            hImage="https://cdn.discordapp.com/attachments/668204203960696836/866133574796836894/0689a7598fd9ed8ca82c456fed870d54.jpg",
            Health=1.12,
            Stamina=0,
            Attack=0.87,
            Intelligence=0.9
        )
        
        # self.Type = EWeaponType.Nobles
        self.Arrow = EArrowType.Normal
        # self.Description
        self._base_attack.long = self._base_attack.brief = f'Deals {self.User.Strength} _(100% of your `Strength`)_'
        self.Abilities = (
            self._base_attack,
            Ability(
                'Normalize',
                'Your Arrows become `Normal`',
                f'From now on, your Arrows become `Normal` and deal {self.User.Strength} _(100% of your `Strength`)_',
                0, CostType.Null,
                self.Normalize, 1
            ),
            Ability(
                'Electrify',
                'Your Arrows become `Electrified`',
                f'From now on your Arrows become `Electrical`, deal {self.User.Strength * 0.9 + self.User.Intelligence * 0.1:.0f} _(90% of your `Strength` + 10% of your `Intelligence`)_ and has 30% chance to `Paralyze` the target for one turn',
                0, CostType.Null,
                self.Electrify, 1
                ),
            Ability(
                'Ablaze',
                'Your Arrows become `Ablazed`',
                f'From now on your Arrows become `Ablazed`, deal {self.User.Strength * 0.7 + self.User.Intelligence * 0.4:.0f} _(70% of your `Strength` + 40% of your `Intelligence`)_ and has 10% chance to `Burn` the target for 3% of their `Health` for two turns.',
                0, CostType.Null,
                self.Ablaze, 1
            ),
            Ability(
                'Freeze',
                'Your Arrows become `Frozen`',
                f"From now on your Arrows become `Freezed`, deal {self.User.Strength * 0.65 + self.User.Intelligence * 0.5:.0f} _(65% of your `Strength` + 50% of your `Intelligence`)_ and lower target's `Strength` by 3 and `Perception` by 4",
                0, CostType.Null,
                self.Freeze, 1
                )
        )

    def BaseAttack(self, target: 'Player'):
        to_add = ""
        match self.Arrow:
            case EArrowType.Normal:
                damage = self.User.Strength

            case EArrowType.Electrical:
                par = random.randint(0, 100)
                if par <= 30:
                    target.AddStatus(EStatus.Stunned, turns=1)
                    to_add = f"{self.User.name}'s `Electrified` Arrow paralyzed {target.name}."
                damage = self.User.Strength * 0.9 + self.User.Intelligence * 0.1
                

            case EArrowType.Ablaze:
                bur = random.randint(0, 100)
                if bur <= 10:
                    burn = target.Health * 0.03
                    target.AddWound(self.User, round(burn), 2, EWound.Burn)
                    to_add = f"{self.User.name}'s `Ablazed` Arrow burnt {target.name} who will suffer {burn} damage for two turns."
                
                damage = self.User.Strength * 0.7 + self.User.Intelligence * 0.4
            
            case EArrowType.Frozen:
                target.Strength -= 3
                damage = self.User.Strength * 0.65 + self.User.Intelligence * 0.5
                to_add = f"{self.User.name}'s `Frozen` Arrow froze {target.name} and decreased their `Strength` by 3 and their `Perception` by 4."

        
        crit = random.randint(0, 100)
        critical = crit <= self.User.CritChance
        damage *= self.User.CritDamage if critical else 1
        dmg = target.TakeDamage(damage, EDamage.BaseAttack)
        if critical:
            log = f"{self.User.name} attacked {target.name} and scored a `Critical Strike` dealing {round(dmg)} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        else:
            log = f"{self.User.name} attacked {target.name} and dealt {round(dmg)} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        
        log = f"{log}\n\n{to_add}" if to_add else log
        return log


    def Normalize(self, target: 'Player', _):
        self.Arrow = EArrowType.Normal
        self._base_attack.long = self._base_attack.brief = f'Deals {self.User.Strength} _(100% of your `Strength`)_'
        return self.BaseAttack(target)

    def Electrify(self, target: 'Player', _):
        self.Arrow = EArrowType.Electrical
        self._base_attack.long = self._base_attack.brief = f'Deals {self.User.Strength * 0.9 + self.User.Intelligence * 0.1:.0f} _(90% of your `Strength` + 10% of your `Intelligence`)_ and has 30% chance to `Paralyze` the target for one turn'
        return self.BaseAttack(target)

    def Ablaze(self, target: 'Player', _):
        self.Arrow = EArrowType.Ablaze
        self._base_attack.long = self._base_attack.brief =  f'Deals {self.User.Strength * 0.7 + self.User.Intelligence * 0.4:.0f} _(70% of your `Strength` + 40% of your `Intelligence`)_ and has 10% chance to `Burn` the target for two turns.'
        return self.BaseAttack(target)
    
    def Freeze(self, target: 'Player', _):
        self.Arrow = EArrowType.Frozen
        self._base_attack.long = self._base_attack.brief =  f"Deals {self.User.Strength * 0.65 + self.User.Intelligence * 0.5:.0f} _(65% of your `Strength` + 50% of your `Intelligence`)_ and lowers target's `Strength` by 3 and `Perception` by 4"
        return self.BaseAttack(target)