from typing import TYPE_CHECKING

import random

from .weapon import *
from core.Resources import *

if TYPE_CHECKING:
    from core.Lobby import Player


__all__ = ('CoreSpear',)

class CoreSpear(Weapon):

    Brief = "Increased Strength | Strong in 1 vs 1"
    cost = 500
    __slots__ = ('_lowered_armor')

    def __init__(self, character):
        super().__init__(
            character=character,
            shield=0,
            wImage="https://cdn.discordapp.com/attachments/668204203960696836/866133242105430026/547c1b382764ea4283acc48eddd27f0c.jpg",
            hImage="https://i.pinimg.com/originals/12/07/61/120761195d1db6ed632035fbfa4e071e.jpg",
            Strength=1.2,
            Armor=0.8
        )
        # self.Type = EWeaponType.Nobles
        self._lowered_armor: bool = False
        self._base_attack.long = self._base_attack.brief = f"Deals {self.User.Strength * 0.8:.0f} damage _(80% of your `Strength`)_ + 20% of target's `Armor`"
        self.Abilities = (
            self._base_attack,
            Ability(
                'Soul Slash',
                'You slash your target with your Spear',
                f'You slash your Spear to the target dealing {self.User.Strength * 0.6 + self.User.Health * 0.1:.0f} damage _(60% of your `Strength` + 10% of your `Maximum Health`)_ and `Wounding` them for 1% of their `Current Healt` for three turns\n__This ability can `Critically Strike` for {self.User.CritDamage:.2%} damage__\n\n_35 Stamina_',
                35,
                CostType.Stamina,
                self.SoulSlash,
                1
            ),
            Ability(
                'Aegis Assault',
                'You jump towards your enemy piercing them from above',
                f'You jump towards your target, lowering your `Perception` by 11 until the end of the turn and dealing {self.User.Strength * 1.15:.0f} damage _(115% of your `Strength`)_\n\n_27 Stamina_',
                27,
                CostType.Stamina,
                self.AegisAssault,
                1
            ),
            Ability(
                'Flawless Execution',
                'You search a _vital point_ of your target, if they have none this ability will fail',
                'You slash to a __Vital Point__ of the target, instantly killing them if they have less than `18% Health`\n\n_69 Stamina_',
                69,
                CostType.Stamina,
                self.FlawlessExecution,
                1
                ),
            Ability(
                'Grand Starfall',
                'You throw your Spear to the target Piercing them',
                f"You throw your Spear to the target dealing {self.User.Strength} damage _(100% of your `Strength`)_ + 20% of target's `Armor`\n\n_31 Stamina_",
                31,
                CostType.Stamina,
                self.GrandStarfall,
                1
            )
        )

    def RestoreArmor(self):
        if self._lowered_armor:
            self.User.Armor += 11
            self._lowered_armor = False
    
    def BaseAttack(self, target: 'Player') -> str:
                
        crit = random.randint(0, 100)
        critical = crit <= self.User.CritChance
        damage = self.User.Strength * 0.8 + target.Armor * 0.2
        damage *= self.User.CritDamage if critical else 1
        dmg_output = target.TakeDamage(round(damage), EDamage.BaseAttack)

        if critical:
            log = f"{self.User.display_name} has attacked {target.display_name} and has scored a `Critical Strike` for {dmg_output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        else:
            log = f"{self.User.display_name} has attacked {target.display_name} for {dmg_output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def SoulSlash(self, target: 'Player', _) -> str:

        self.User.cStamina -= self.Abilities[1].cost
        
        wound = target.cHealth*0.01
        target.AddWound(self.User, wound, 2, EWound.Wound)
        
        crit = random.randint(0, 100)
        critical = crit <= self.User.CritChance
        damage = self.User.Strength * 0.6 + self.User.Health * 0.1
        damage *= self.User.CritDamage if critical else 1
        dmg_output = target.TakeDamage(round(damage), EDamage.Ability)

        if critical:
            log = f"""{self.User.display_name} has used Soul Slash on {target.display_name} and has scored a `Critical Strike` for {dmg_output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}
            
            {target.display_name} is now `Wounded` and will suffer {target.cHealth*0.01:.0f} damage for two turns _(`Wound` damage is mitigated by both `Armor` and `Perception`)_."""
        else:
            log = f"""{self.User.display_name} has used Soul Slash on {target.display_name} for {dmg_output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}
            
            {target.display_name} is now `Wounded` and will suffer {target.cHealth*0.01:.0f} damage for two turns _(`Wound` damage is mitigated by both `Armor` and `Perception`)_."""
        return log

    def AegisAssault(self, target: 'Player', _) -> str:

        self.User.cStamina -= self.Abilities[2].cost
        
        self.User.Armor -= 11

        damage = self.User.Strength * 1.15
        dmg_output = target.TakeDamage(round(damage), EDamage.Ability)

        log = f"""{self.User.display_name} has used Aegis Assault {target.display_name} for {dmg_output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}
        
        {self.User.display_name}'s `Perception` is now {self.User.Perception} until the end of the turn."""
        
        return log

    def FlawlessExecution(self, target: 'Player', _) -> str:

        self.User.cStamina -= self.Abilities[3].cost

        if target.cHealth > target.Health * 0.18:
            log = f"{self.User.display_name} used Flawless Execution on {target.display_name} but it failed.\n_({target.display_name}'s percentage `Health`: {target.cHealth/target.Health:.2%})_"
            return log

        target.TakeDamage(target.Health, EDamage.TrueDamage)
        log = f'{self.User.display_name} used Flawless Execution on {target.display_name} and executed them.'
        return log

    def GrandStarfall(self, target: 'Player', _) -> str:

        self.User.cStamina -= self.Abilities[4].cost
        damage = self.User.Strength + target.Armor * 0.2
        dmg_output = target.TakeDamage(round(damage), EDamage.Ability)

        log = f"{self.User.display_name} used Grand Starfall on {target.display_name} and dealt {dmg_output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def EndTurn(self):
        self.RestoreArmor()
        super().EndTurn()
        