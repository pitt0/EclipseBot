from typing import TYPE_CHECKING

from .weapon import Weapon
from game.Resources import *

if TYPE_CHECKING:
    from game.Lobby import Player

__all__ = ('DreadfulSpellBook',)

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
        self.Abilities = (
            self._base_attack,
            Ability(
                'Call of the Void',
                'You Charm your target with a `Shadow` Spell',
                f"You Charm your target becoming `Targeted` and dealing {self.User.Intelligence * 0.8:.0f} damage _(80% of your `Intelligence`)_ + 2% of target's `Maximum Health`\n\n_43 Stamina_",
                43, CostType.Stamina,
                self.CallOfTheVoid,
                1
            ),
            Ability(
                'Twilight Clutch',
                'You bring down the night entangling your target',
                f"You brign down the dark entangling your target and dealing 80% of target's `Strength`, lowering their `Perception` by 12\n\n_42 Stamina_",
                42, CostType.Stamina,
                self.TwilightClutch,
                1
            ),
            Ability(
                'Imperio',
                "You take control of target's mind, making them attack theirself",
                f"You take control of target's mind, dealing {self.User.Intelligence * 0.8:.0f} _(80% of your `Intelligence`)_ + 30% of target's `Strength`\n_This ability is mitigated as a `Base Attack`_\n\n_40 Stamina_",
                40, CostType.Stamina,
                self.Imperio,
                1
            ),
            Ability(
                'Mantra',
                'You Charm yourself to free your body from `Shadows`',
                'You Charm yourself sacrificing 8 `Health Points` and increasing your `Armor` and your `Perception` by 13\n\n_26 Stamina_',
                26, CostType.Stamina,
                self.Mantra,
                0
            )
        )

    def CallOfTheVoid(self, target: 'Player', allies: list['Player']):
        self.User.cStamina -= self.Abilities[1].cost
        for ally in allies:
            if ally.CheckStatus(EStatus.Targeted):
                ally.RemoveStatus(EStatus.Targeted)
        self.User.AddStatus(EStatus.Targeted, 1)
        damage = self.User.Intelligence * 0.8 + target.Health * 0.02
        output = target.TakeDamage(round(damage), EDamage.Ability)
        
        log = f"{self.User.name} used `Call of the Void` on {target.name} and dealt {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log + f"\n{self.User.name} is now `Targeted` for the next turn"

    def TwilightClutch(self, target: 'Player', _):
        self.User.cStamina -= self.Abilities[2].cost
        damage = target.Strength * 0.8
        output = target.TakeDamage(round(damage), EDamage.Ability)

        target.Perception -= 12

        log = f"{self.User.name} used `Twilight Clutch` on {target.name} and dealt them {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log + f"\n{target.name}'s `Perception` dropped by 12."

    def Imperio(self, target: 'Player', _):
        self.User.cStamina -= self.Abilities[3].cost
        damage = self.User.Intelligence * 0.8 + target.Strength * 0.3
        output = target.TakeDamage(round(damage), EDamage.BaseAttack)

        log = f"{self.User.name} used `Imperio` on {target.name} and dealt {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def Mantra(self, _, __):
        self.User.cStamina -= self.Abilities[4].cost
        
        self.User.TakeDamage(8, EDamage.TrueDamage, affects_shield=False)
        self.User.Armor += 13; self.User.Perception += 13
        
        log = f"{self.User.name} used `Mantra` on theirself, suffering 8 damage and increasing their `Armor` and their `Perception` by 13"
        return log
