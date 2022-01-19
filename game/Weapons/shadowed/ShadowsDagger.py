from typing import TYPE_CHECKING

import random

from ..weapon import Weapon
from ...Resources import *

if TYPE_CHECKING:
    from ...Lobby import Player

__all__ = ('ShadowsDagger')

class ShadowsDagger(Weapon):

    Brief = "Increased Power | Consumes Health as Stamina"
    cost = 500
    __slots__ = ("Shadowed")

    def __init__(self, character):
        super().__init__(
            character=character,
            shield=0,
            wImage="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/5a270ec3-3836-4dbb-89d4-08f067898a2c/d5d19ld-0a0d494d-becf-4c1d-a5af-a019bd323278.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwic3ViIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsImF1ZCI6WyJ1cm46c2VydmljZTpmaWxlLmRvd25sb2FkIl0sIm9iaiI6W1t7InBhdGgiOiIvZi81YTI3MGVjMy0zODM2LTRkYmItODlkNC0wOGYwNjc4OThhMmMvZDVkMTlsZC0wYTBkNDk0ZC1iZWNmLTRjMWQtYTVhZi1hMDE5YmQzMjMyNzguanBnIn1dXX0.3Y98Ixn_-rjy5M27omgwjT_O-Z8GE8ilErXMF_crh_Q",
            hImage="https://i.pinimg.com/originals/99/a7/9e/99a79e297d9502e5973e86450ae7134b.jpg",
            Health=2,
            Stamina=0,
            Strength=1.1,
            Armor=0.9,
            Intelligence=1.15
        )
        self.Name = "Shadow'sDagger"
        self.Shadowed = False
        # self.Type = EWeaponType.Shadowed

        self.BA = f"Deals {self.User.Strength * 0.8 + 1000/self.User.cHealth:.0f} damage _(80% of your `Strength`)_ and Heals you for a half of the damage Dealt | The less `Current Health` you have the more damage it does"
        # self.Description
        self.Abilities = {
            "Filthy Cut": {
                "Brief": "You appear behind the target and Stab them",
                "Description": f"You appear behind the target and Stab them dealing {self.User.Strength * 0.9:.0f} _(90% of your `Strength`)_ + 5% of target's `Current Health`\n\n_13% of your Current Health_",
                "Health": self.User.cHealth * 0.13,
                "Callable": self.FilthyCut,
                "Targets": 1
            },
            "Deathly Hallow": {
                "Brief": "You Stab your target in one of their __Vital Points__",
                "Description": f"You Stab your target in one of their __Vital Points__ dealing {self.User.Strength * 0.2 + self.User.Intelligence * 0.1:.0f} _(20% of your `Strength` + 10% of your `Intelligence`)_ + 10% of target's `Maximum Health`\n\n_15% of your Current Health_",
                "Health": self.User.cHealth * 0.15,
                "Callable": self.DeathlyHallow,
                "Targets": 1
            },
            "Shadow's Hallow": {
                "Brief": "The Shadow in your dagger takes control of you until your next turn",
                "Description": f"Your next `Base Attack` deals {self.User.Strength * 0.6:.0f} damage _(60% of your `Strength`)_ and ignores target's `Armor`\n\n_13% of your Current Health_",
                "Health": self.User.cHealth * 0.13,
                "Callable": self.ShadowsHallow,
                "Targets": 0
            },
            "Shadow's Pierce": {
                "Brief": "Your Dagger becomes Shadowed and you Stab the target with it",
                "Description": f"You Stab your target with your Shadowed Dagger dealing {self.User.Strength * 0.7:.0f} `True Damage` _(70% of your `Strength`)_ (`True Damage` is mitigated by target's `Shield`)\n\n_14% of your Current Health_",
                "Health": self.User.cHealth * 0.14,
                "Callable": self.ShadowsPierce,
                "Targets": 1
            },
        }

    def BaseAttack(self, target: 'Player'):
        crit = random.randint(0, 100)
        critical = crit <= self.User.CritChance
    
        if self.Shadowed:
            self.Shadowed = False
            damage = self.User.Strength * 0.6
            damage_type = EDamage.TrueDamage
        else:
            damage = self.User.Strength * 0.8 + 1000/self.User.cHealth
            damage_type = EDamage.BaseAttack
        
        damage *= self.User.CritDamage if critical else 1
        output = target.TakeDamage(damage, damage_type)
        if damage_type == EDamage.BaseAttack:
            self.User.GetHealed(output/2, EHeal.Normal, self.User)
        
        if critical:
            log = f"{self.User.name} attacked {target.name} scoring a `Critical Strike` and dealing {output}, healing for a half.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        else:
            log = f"{self.User.name} attacked {target.name} dealing them {output} and healing for a half.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"

        return log

    def FilthyCut(self, target: 'Player', *args, **kwargs):
        pay = self.Abilities["Filthy Cut"]["Health"]
        self.User.TakeDamage(pay, EDamage.TrueDamage, False)

        damage = self.User.Strength * 0.9 + target.cHealth * 0.05
        result = target.TakeDamage(damage, EDamage.Ability)

        log = f"{self.User.name} used `Filthy Cut` on {target.name} dealing {result} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def DeathlyHallow(self, target: 'Player', *args, **kwargs):
        pay = self.Abilities["Deathly Hallow"]["Health"]
        self.User.TakeDamage(pay, EDamage.TrueDamage, False)
        
        damage = self.User.Strength * 0.2 + self.User.Intelligence * 0.1 + target.Health * 0.1
        output = target.TakeDamage(damage, EDamage.Ability)

        log = f"{self.User.name} used `Deathly Hallow` on {target.name} and dealt {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def ShadowsHallow(self, target: 'Player', allies: list['Player']):
        pay = self.Abilities["Shadow's Hallow"]["Health"]
        self.User.TakeDamage(pay, EDamage.TrueDamage, False)
        self.Shadowed = True

        log = f"{self.User.name} used `Shadow Hallow`. {self.User.name}'s next `Base Attack` will deal {self.User.Strength * 0.6:.0f} damage _(60% of their `Strength`)_ and will ignore target's `Armor`."
        return log

    def ShadowsPierce(self, target: 'Player', *args, **kwargs):
        pay = self.Abilities["Shadow's Pierce"]["Health"]
        self.User.TakeDamage(pay, EDamage.TrueDamage, False)

        damage = self.User.Strength * 0.7
        output = target.TakeDamage(damage, EDamage.TrueDamage)

        log = f"{self.User.name} used `Shadow's Pierce` on {target.name}, dealing them {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log
