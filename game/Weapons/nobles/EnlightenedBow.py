from typing import TYPE_CHECKING

import random

from ..weapon import Weapon
from ...Resources import *

if TYPE_CHECKING:
    from ...Lobby import Player

__all__ = ('EnlightenedBow')

class EnlightenedBow(Weapon):

    Brief = "Increased Power | Good in Team Fights"
    cost = 500
    __slots__ = ("Toggles")

    def __init__(self, character):
        super().__init__(
            character=character,
            shield=0,
            wImage="https://cdn.discordapp.com/attachments/668204203960696836/866133180376809542/f07a769a1b6bacbcbbe801c4f8e77b7b.jpg",
            hImage="https://cdn.discordapp.com/attachments/668204203960696836/866133755978973234/d6ca7889b156b9f2a72c8cf477805db9.jpg",
            Strength=1.2,
            Armor=0.9,
            Intelligence=1.1
        )

        self.Toggles = {
            'Peacemaker': False,
            'Enlightener': False,
            'Mind Breaker': False,
            'Shadows Hunter': False
        }
        
        # self.Type = EWeaponType.Nobles
        self.BA = f"Deals {self.User.Strength} damage _(100% of your Strength)_" if self.Toggles['Enlightener'] else f"Deals {self.User.Strength * 1.3:.0f} damage _(130% of your Strength)_, consumes 18 `Stamina` + 15 `Health Points` and have 5% more chance to `Critically Strike`"
        # self.Description
        self.Abilities = {
            "Peacemaker": {
                "Brief": "You shoot a precise `Enlightened` Arrow",
                "Description": f"You shoot an `Enlighened` Arrow that deals {self.User.Strength * 0.6:.0f} _(60% of your `Strength`)_ and `Disarms` the target for the next turn\n_This ability can `Critically Strike` for {self.User.CritDamage:.2%} of the damage_\n\n_29 Stamina_",
                "Stamina": 31,
                "Callable": self.Peacemaker,
                "Targets": 1,
                "Toggle": False
            },
            "Enlightener": {
                "Brief": "Your Arrows become `Elightened`, dealing more damage but consuming your Soul",
                "Description": f"Your Arrows become `Enlightened`, your `Base Attacks` now deal {self.User.Strength*1.3:.0f} _(130% of your `Strength`)_ and have 5% more chance to `Critically Strike` but consume 18 `Stamina` and 15 `Health Points`\n\n_Toggle_",
                "Stamina": 0,
                "Callable": self.Enlightener,
                "Targets": 0,
                "Toggle": True
            },
            "Mind Breaker": {
                "Brief": "You shoot an `Enlightened` arrow aiming at the head of your target",
                "Description": f"You shoot an arrow at the head of your target dealing {self.User.Strength * 0.6:.0f} _(60% of your `Strength`)_ + 70% of target's `Intelligence` damage\n\n_41 Stamina_",
                "Stamina": 41,
                "Callable": self.MindBreaker,
                "Targets": 1,
                "Toggle": False
            },
            "Shadows Hunter": {
                "Brief": "You shoot at your target, linking their soul with yours and taking half of the damage they take",
                "Description": f"You shoot at the sky linking you and your target, dealing them 10% of their `Health` as `True Damage` and taking half of the damage you deal as an `Ability Damage` (`True Damage` is mitigated by `Shield`)\n\n_25 Stamina_",
                "Stamina": 25,
                "Callable": self.ShadowsHunter,
                "Targets": 1,
                "Toggle": False
            }
        }

    def BaseAttack(self, target: 'Player'):
        if not self.Toggles['Enlightener']:
            return super().BaseAttack(target)

        self.User.cStamina -= 10
        
        self_damage = self.User.TakeDamage(12, EDamage.TrueDamage, False)
        
        crit = random.randint(0, 100)
        critical = crit <= self.User.CritChance + 5
        damage = self.User.Strength * 1.5
        damage *= self.User.CritDamage if critical else 1
        dmg_output = target.TakeDamage(damage, EDamage.BaseAttack)
        if critical:
            log = f"""{self.User.name} has attacked {target.name} and scored a `Critical Strike` for {dmg_output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}
            
            {self.User.name} has lost {self_damage} `Health`. {self.User.name}'s `Health`: {self.User.cHealth}/{self.User.Health}."""
        else:    
            log = f"""{self.User.name} has attacked {target.name} and dealt {dmg_output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}
            
            {self.User.name} has lost {self_damage} `Health`. {self.User.name}'s `Health`: {self.User.cHealth}/{self.User.Health}."""
        return log

    def Peacemaker(self, target: 'Player', allies: list['Player']):
        self.User.cStamina -= self.Abilities["Peacemaker"]["Stamina"]

        target.AddStatus(EStatus.Disarmed)

        crit = random.randint(0, 100)
        critical = crit <= self.User.CritChance
        damage = self.User.Strength * 0.6
        damage *= self.User.CritDamage if critical else 1
        dmg = target.TakeDamage(damage, EDamage.Ability)

        if critical:
            log = f"""{self.User.name} used `Peacemaker` on {target.name} scoring a `Critical Strike` and dealing {dmg}.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}
        
            {target.name} is now `Disarmed` for the next turn."""
        else:
            log = f"""{self.User.name} used `Peacemaker` on {target.name} dealing {dmg}.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}

            {target.name} is now `Disarmed` for the next turn."""

        return log

    def Enlightener(self, target: 'Player', allies: list['Player']):
        if not self.Toggles['Enlightener']:
            self.Toggles['Enlightener'] = True
            log = f'{self.User.name} has `Enlightened` their Arrows, from now on their `Base Attacks` will deal {self.User.Strength*1.3:.0f} _(130% of their `Strength`)_ and have 5% more chance to `Critically Strike`, but will consume 18 `Stamina` and deal 15 `Health Points`.'
        else:
            self.Toggles['Enlightener'] = False
            log = f'{self.User.name} has `Faded` their Arrows, from now on their `Base Attacks` will deal {self.User.Strength} _(100% of their `Strength`)_.'
        return log

    def MindBreaker(self, target: 'Player', allies: list['Player']):
        self.User.cStamina -= self.Abilities["Mind Breaker"]["Stamina"]
        damage = self.User.Strength * 0.6 + target.Intelligence * 0.7
        dmg = target.TakeDamage(damage, EDamage.Ability)
        log = f"{self.User.name} has used `Mind Breaker` on {target.name} and dealt {dmg} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def ShadowsHunter(self, target: 'Player', allies: list['Player']):
        self.User.cStamina -= self.Abilities["Shadows Hunter"]["Stamina"]

        damage = target.Health * 0.1
        self_damage = self.User.TakeDamage(damage/2, EDamage.Ability)
        dmg = target.TakeDamage(damage, EDamage.TrueDamage)
        log = f"{self.User.name} has used `Shadows Hunter` on {target.name} dealing {dmg} and suffering {self_damage}.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}.\n{self.User.name}'s `Health`: {self.User.cHealth}/{self.User.Health}"
        return log