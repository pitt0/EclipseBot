from typing import TYPE_CHECKING

import random

from ..weapon import Weapon
from ...Resources import *

if TYPE_CHECKING:
    from ...Lobby import Player

__all__ = ('CursedBlade')

class CursedBlade(Weapon):

    Brief = "Increased Strength | Kit focused on 1 vs 1"
    cost = 500
    __slots__ = ()

    def __init__(self, character):
        super().__init__(
            character=character,
            shield=0,
            wImage="http://i.gr-assets.com/images/S/compressed.photo.goodreads.com/hostedimages/1379797594i/633938._SX540_.jpg",
            hImage="https://cdn.discordapp.com/attachments/668204203960696836/866090061966606338/920af882af9db4f8d9d53aaa308e2613.jpg",
            Strength=1.2,
            Armor=0.9
        )

        # self.Type = EWeaponType.Shadowed
        self.BA = f"Deals {round(self.User.Strength * 0.9)} (90% of your Strength) and Wounds your target for 4 damage over 2 turns."
        # self.Description
        self.Abilities = {
            "Curse": {
                "Brief": "You let the `Shadow` inside your Blade corrupt your soul empowering your `Strength`",
                "Description": "You Sacrifice 12 `Health Points` to increase your `Strength` by 15 and your `Perception` by 3\n\n_18 Stamina_",
                "Stamina": 18,
                "Callable": self.Curse,
                "Targets": 0
            },
            "Silent Assault": {
                "Brief": "You jump behind your enemy Stabbing them with your Blade",
                "Description": f"You jump behind your enemy dealing {self.User.Strength * 0.7 + self.User.Intelligence * 0.5:.0f} damage _(70% of your `Strength` + 50% of your `Intelligence`)_, and `Wounding` them for 21 damage over 3 turns.\n\n_23 Stamina_",
                "Stamina": 23,
                "Callable": self.SilentAssault,
                "Targets": 1
            },
            "Deathly Hallow": {
                "Brief": "You Stab a _vital point_ of your enemy, dealing damage depending on enemy's `Maximum Health`",
                "Description": f"You Stab a _vital point_ of your enemy, dealing {self.User.Strength * 0.2 + self.User.Intelligence * 0.1:.0f} _(20% of your `Strength` + 10% of your `Intelligence`)_ + 10% of target's `Maximum Health`\n\n_50 Stamina_",
                "Stamina": 50,
                "Callable": self.DeathlyHallow,
                "Targets": 1
            },
            "Plague": {
                "Brief": "You Pierce your enemy with your Blade, then twist it `Wounding` them",
                "Description": f"You Pierce your enemy with your Blade, then you twist it dealing {self.User.Strength} damage _(100% of your `Strength`)_, lowering target's `Armor` by 8 and `Strength` by 12 and `Wounding` them for 5 damage for 5 turns\n\n_31 Stamina_",
                "Stamina": 31,
                "Callable": self.Plague,
                "Targets": 1
            }
        }

    def BaseAttack(self, target: 'Player'):
        target.AddWound(self.User, 4, 2, EWound.Wound)
        crit = random.randint(0, 100)
        critical = crit <= self.User.CritChance * 100
        damage = self.User.Strength * 0.9
        damage *= self.User.CritDamage if critical else 1
        output = target.TakeDamage(damage, EDamage.BaseAttack)

        log = f"{self.User.name} attacked {target.name} dealing {output} damage and `Wounding` them for 8 damage over 2 turns.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def Curse(self, *args, **kwargs):
        self.User.cStamina -= self.Abilities["Curse"]["Stamina"]
        self.User.TakeDamage(12, EDamage.TrueDamage, False)
        self.User.Strength += 15

        log = f"{self.User.name} used `Curse` and lost 12 `Health` to increase their `Strength` by 15 and their `Perception` by 3"
        return log

    def SilentAssault(self, target: 'Player', allies: list['Player']):
        self.User.cStamina -= self.Abilities["Silent Assault"]["Stamina"]

        target.AddWound(self.User, 7, 3, EWound.Wound)
        damage = self.User.Strength * 0.7 + self.User.Intelligence * 0.5
        output = target.TakeDamage(round(damage), EDamage.Ability)

        log = f"{self.User.name} used `Silent Assault` on {target.name}, dealing {output} damage and `Wounding` them for 21 damage over 3 turns.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def DeathlyHallow(self, target: 'Player', allies: list['Player']):
        self.User.cStamina -= self.Abilities["Deathly Hallow"]["Stamina"]
        
        damage = self.User.Strength * 0.2 + self.User.Intelligence * 0.1 + target.Health * 0.1
        output = target.TakeDamage(round(damage), EDamage.Ability)

        log = f"{self.User.name} used `Deathly Hallow` on {target.name} dealing {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def Plague(self, target: 'Player', allies: list['Player']):
        self.User.cStamina -= self.Abilities["Plague"]["Stamina"]
        target.Armor -= 8; self.User.Strength -= 12

        damage  = self.User.Strength
        output = target.TakeDamage(damage, EDamage.Ability)

        target.AddWound(self.User, 5, 5, EWound.Wound)

        log = f"{self.User.name} used `Plague` on {target.name} and dealt {output} damage. {target.name} is now `Wounded` and will suffer 25 damage over 5 turns.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log
