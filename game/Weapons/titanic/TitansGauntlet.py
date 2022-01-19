from typing import TYPE_CHECKING
from ..weapon import Weapon
from ...Resources import *

if TYPE_CHECKING:
    from ...Lobby import Player

__all__ = ['TitansGauntlet']

class TitansGauntlet(Weapon):

    Brief = "Optimal in Team Fights | Greedy"
    cost = 500
    __slots__ = ()

    def __init__(self, character):
        super().__init__(
            character=character,
            shield=20,
            wImage="https://cdn.discordapp.com/attachments/668204203960696836/866133447797899284/7cb3b403660a5953a86a6cc43fa402e6.jpg",
            hImage="https://cdna.artstation.com/p/assets/images/images/021/084/424/large/changyoung-jung-20161014-vakinboss-sheet-m.jpg?1570347113",
            Strength=1.1,
            Speed=0.8
        )
        self.Name = "Titan'sGauntlet"
        # self.Type = EWeaponType.Titanic

        # self.Description
        self.Abilities = {
            "Tempest": {
                "Brief": "You call a tempest of meteors to fall towards your enemies",
                "Description": f"You call a tempest of meteors to fall towards your enemies dealing {self.User.cStamina * 0.8:.0f} damage _(80% of your `Stamina`)_\n\n_13% Current Health_",
                "Health": self.User.cHealth * 0.13,
                "Callable": self.Tempest,
                "Targets": -1
            },
            "Titan Overload": {
                "Brief": "You focus to free all of your energy",
                "Description": f"You explode dealing {self.User.cStamina * 2} damage _(200% of your `Stamina`)_ to all of your enemies\n\n_50% Current Health_",
                "Health": self.User.cHealth * 0.5,
                "Callable": self.TitanOverload,
                "Targets": -1
            },
            "Thunder Shot": {
                "Brief": "You attack your target with a powerful fist, empowered by your energy",
                "Description": f"You explode a fist that deals {self.User.Strength * 0.8 + self.User.cStamina * 0.5:.0f} damage _(80% of your `Strength` + 50% of your `Stamina`)_\n\n_14% Current Health_",
                "Health": self.User.cHealth * 0.14,
                "Callable": self.ThunderShot,
                "Targets": 1
            },
            "Meditate": {
                "Brief": "You start to meditate placating yourself",
                "Description": f"You recover 20% of your `Health` but your `Stamina` decreases by 20\n\n_0 Current Health_",
                "Health": 0,
                "Callable": self.Meditate,
                "Targets": 0
            }
        }

    def Tempest(self, target: list['Player'], *args, **kwargs):
        self.User.TakeDamage(self.Abilities["Tempest"]["Health"], EDamage.TrueDamage, False)
        damage = self.User.cStamina * 0.8
        for enemy in target:
            enemy.TakeDamage(damage, EDamage.Ability)

        log = f"{self.User.name} used `Tempest` and dealt {damage} to every enemy"
        return log

    def TitanOverload(self, target: list['Player'], *args, **kwargs):
        self.User.TakeDamage(self.Abilities["Titan Overload"]["Health"], EDamage.TrueDamage, False)

        damage = self.User.cStamina * 2
        for enemy in target:
            enemy.TakeDamage(damage, EDamage.Ability)
        
        log = f"{self.User.name} used `Titan Overload` and dealt {damage} to every enemy"
        return log

    def ThunderShot(self, target: 'Player', *args, **kwargs):
        self.User.TakeDamage(self.Abilities["Thunder Shot"]["Health"], EDamage.TrueDamage, False)
        damage = self.User.Strength * 0.8 + self.User.cStamina * 0.5
        output = target.TakeDamage(damage, EDamage.Ability)

        log = f"{self.User.name} used `Thunder Shot` on {target.name} and dealth them {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def Meditate(self, *args, **kwargs):
        heal = self.User.Health * 0.2
        self.User.GetHealed(round(heal), EHeal.Normal, self.User)
        self.User.cStamina -= 20

        log = f"{self.User.name} used `Meditate` and recovered {heal}.\n{self.User.name}'s `Health`: {self.User.cHealth}/{self.User.Health}"
        return log
