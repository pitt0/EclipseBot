from typing import TYPE_CHECKING

from ..weapon import Weapon
from ...Resources import *

if TYPE_CHECKING:
    from ...Lobby import Player

__all__ = ('DreadfulSpellBook')

class DreadfulSpellBook(Weapon):

    Brief = "Increased Intelligence | Stronger in Team Fights"
    cost = 500
    __slots__ = ()

    def __init__(self, character):
        super().__init__(
            character=character,
            shield=12,
            wImage="https://i.pinimg.com/originals/3e/dc/50/3edc502067bc0f4590722aa6e8c59b6d.jpg",
            hImage="https://i.pinimg.com/736x/fa/8e/4d/fa8e4d352168c0c95e7b443c3d4b7107--fantasy-mage-male-magician-fantasy.jpg",
            Intelligence=1.3,
            Armor=0.8
        )

        # self.Type = EWeaponType.Shadowed
        # self.Description
        self.Abilities = {
            "Call of the Void": {
                "Brief": "You Charm your target with a `Shadow` Spell",
                "Description": f"You Charm your target becoming `Targeted` and dealing {self.User.Intelligence * 0.8:.0f} damage _(80% of your `Intelligence`)_ + 2% of target's `Maximum Health`\n\n_43 Stamina_",
                "Stamina": 43,
                "Callable": self.CallOfTheVoid,
                "Targets": 1
            },
            "Twilight Clutch": {
                "Brief": "You bring down the night entangling your target",
                "Description": f"You brign down the night entangling your target and dealing 80% of target's `Strength`, lowering their `Perception` by 12\n\n_42 Stamina_",
                "Stamina": 42,
                "Callable": self.TwilightClutch,
                "Targets": 1
            },
            "Imperio": {
                "Brief": "You take control of target's mind, making them attack theirself",
                "Description": f"You take control of target's mind, dealing {self.User.Intelligence * 0.8:.0f} _(80% of your `Intelligence`)_ + 30% of target's `Strength`\n_This ability is mitigated as a `Base Attack`_\n\n_40 Stamina_",
                "Stamina": 40,
                "Callable": self.Imperio,
                "Targets": 1
            },
            "Mantra": {
                "Brief": "You Charm yourself to free your body from `Shadows`",
                "Description": "You Charm yourself sacrificing 8 `Health Points` and increasing your `Armor` and your `Perception` by 13\n\n_26 Stamina_",
                "Stamina": 26,
                "Callable": self.Mantra,
                "Targets": 0
            }
        }

    def CallOfTheVoid(self, target: 'Player', allies: list['Player']):
        self.User.cStamina -= self.Abilities["Call of the Void"]["Stamina"]
        for ally in allies:
            if ally.CheckStatus(EStatus.Targeted):
                ally.RemoveStatus(EStatus.Targeted)
        self.User.AddStatus(EStatus.Targeted, 1)
        damage = self.User.Intelligence * 0.8 + target.Health * 0.02
        output = target.TakeDamage(round(damage), EDamage.Ability)
        
        log = f"{self.User.name} used `Call of the Void` on {target.name} and dealt {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log + f"\n{self.User.name} is now `Targeted` for the next turn"

    def TwilightClutch(self, target: 'Player', allies: list['Player']):
        self.User.cStamina -= self.Abilities["Twilight Clutch"]["Stamina"]
        damage = target.Strength * 0.8
        output = target.TakeDamage(round(damage), EDamage.Ability)

        target.Perception -= 12

        log = f"{self.User.name} used `Twilight Clutch` on {target.name} and dealt them {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log + f"\n{target.name}'s `Perception` dropped by 12."

    def Imperio(self, target: 'Player', allies: list['Player']):
        self.User.cStamina -= self.Abilities["Imperio"]["Stamina"]
        damage = self.User.Intelligence * 0.8 + target.Strength * 0.3
        output = target.TakeDamage(round(damage), EDamage.BaseAttack)

        log = f"{self.User.name} used `Imperio` on {target.name} and dealt {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def Mantra(self, *args, **kwargs):
        self.User.cStamina -= self.Abilities["Mantra"]["Stamina"]
        
        self.User.TakeDamage(8, EDamage.TrueDamage, affects_shield=False)
        self.User.Armor += 13; self.User.Perception += 13
        
        log = f"{self.User.name} used `Mantra` on theirself, suffering 8 damage and increasing their `Armor` and their `Perception` by 13"
        return log
