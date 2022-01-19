from typing import TYPE_CHECKING

from ..weapon import Weapon
from ...Resources import *

if TYPE_CHECKING:
    from ...Lobby import Player 

__all__ = ('CorruptedRod')

class CorruptedRod(Weapon):

    Brief = "Increased Intelligence | Focused on Multi Target"
    cost = 500
    __slots__ = ()

    def __init__(self, character):
        super().__init__(
            character=character,
            shield=12,
            wImage="https://cdn.discordapp.com/attachments/668204203960696836/866336316295741460/3545339ba9d12197036c3e402da48682.jpg",
            hImage="https://i.imgur.com/z97ZlfK.jpg",
            Health=1.1,
            Intelligence=1.1,
            Speed=0.8
        )

        # self.Type = EWeaponType.Shadowed
        self.BA = f"Deals {self.User.Strength:.0f} (100% of your Strength) damage and heals you for 75 `Health`"
        self.Abilities = {
            "Requiem": {
                "Brief": "You invoke the Ruined Souls from the Lost `Shadow` Reign, making them to attack your targets",
                "Description": f"You invoke the Ruined Souls asking them to attack up to four targets, dealing {self.User.Intelligence * 0.6 + (self.User.Health - self.User.cHealth) * 0.15:.0f} _(60% of your `Intelligence` + 15% of your `Missing Health`)_ damage each taking 30 `Ability` damage for each enemy hit\n\n_42 Stamina_",
                "Stamina": 42,
                "Callable": self.Requiem,
                "Targets": 4
            },
            "Soul Defile": {
                "Brief": "You cast a `Shadow` Spell to your targets, defiling their and your souls.",
                "Description": f"You cast a `Shadow` Spell to up to three enemies, dealing {self.User.Intelligence * 0.3 + self.User.cHealth * 0.4:.0f} damage _(30% of your `Intelligence` + 30% of your `Current Health`)_, ignoring their `Perception` and their `Shield` and taking 63 `Ability` damage for each enemy hit\n\n_37 Stamina_",
                "Stamina": 37,
                "Callable": self.SoulDefile,
                "Targets": 3
            },
            "Mantra": {
                "Brief": "You make a pray to the `Shadow` Lord.",
                "Description": f"You make a pray to the `Shadow` Lord, `Curse-Healing` yourself by 240 `Health`, increasing your `Perception` by 25 and decreasing your `Intelligence` by 12\n\n_30 Stamina_",
                "Stamina": 30,
                "Callable": self.Mantra,
                "Targets": 0
            },
            "Defiance": {
                "Brief": "You resist your Rod's nature",
                "Description": f"You take control of your Rod, sacrificing 118 `Health Points` and `Healing` your allies by 131 each\n\n_42 Stamina_",
                "Stamina": 42,
                "Callable": self.Defiance,
                "Targets": 0
            }
        }

    def BaseAttack(self, target: 'Player') -> str:
        self.User.GetHealed(20, EHeal.Normal, self.User)
        return super().BaseAttack(target) + f"\n{self.User.name} healed theirself for 75 `Health`.\n{self.User.name}'s `Health`: {self.User.cHealth}"

    def Requiem(self, target: list['Player'], *args, **kwargs):
        self.User.cStamina -= self.Abilities["Requiem"]["Stamina"]
        damage = self.User.Intelligence * 0.6 + (self.User.Health - self.User.cHealth) * 0.15
        for t in target:
            self.User.TakeDamage(30, EDamage.Ability)
            t.TakeDamage(damage, EDamage.Ability)

        log = f"{self.User.name} used `Requiem` on {', '.join(t.name for t in target)} dealing {damage} damage to each and taking {30 * len(target)} damage."
        return log

    def SoulDefile(self, target: list['Player'], *args, **kwargs):
        self.User.cStamina -= self.Abilities["Soul Defile"]["Stamina"]
        damage = self.User.Intelligence * 0.3 + self.User.cHealth * 0.4
        for t in target:
            self.User.TakeDamage(63, EDamage.Ability, False)
            t.TakeDamage(damage, EDamage.TrueDamage, False)
        
        log = f"{self.User.name} used `Soul Defile` on {', '.join(t.name for t in target)} dealing {damage} damage to everyone and suffering {63 * len(target)} damage.\n{self.User.name}'s `Health`: {self.User.cHealth}"
        return log

    def Mantra(self, target: 'Player', *args, **kwargs):
        self.User.cStamina -= self.Abilities["Mantra"]["Stamina"]
        self.User.GetHealed(240, EHeal.Cursed, self.User)

        self.User.Intelligence -= 12
        self.User.Perception += 25

        log = f"{self.User.name} used `Mantra` and `Curse-Healed` theirself by 240 `Health`, increasing their `Perception` by 25 and decreasing their `Intelligence` by 12."
        return log

    def Defiance(self, target: 'Player', allies: list['Player']):
        self.User.cStamina -= self.Abilities["Defiance"]["Stamina"]

        self.User.TakeDamage(20, EDamage.TrueDamage)
        for ally in allies: 
            ally.GetHealed(31, EHeal.Normal, self.User)

        log = f"{self.User.name} used `Defiance`. {self.User.name} has lost 118 `Health` and has `Healed` their whole team for 131 `Health`"
        return log