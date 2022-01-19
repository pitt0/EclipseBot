from typing import TYPE_CHECKING

import random

from ..weapon import Weapon
from ...Resources import *

if TYPE_CHECKING:
    from ...Lobby import Player

__all__ = ('RagingSword')

class RagingSword(Weapon):

    Brief = "Increased Strength | Optimal in 1 vs 1"
    cost = 500
    __slots__ = ('_rage')

    def __init__(self, character):
        super().__init__(
            character=character,
            shield=12,
            wImage="https://i.pinimg.com/originals/e5/36/59/e536591fc77a12e63f5feaabfd2f93e6.jpg",
            hImage="https://external-preview.redd.it/JQ1Un9l2TsBYe2x5znY-TgObq3xX7Ly5cpXqLjtQYhk.png?width=640&crop=smart&auto=webp&s=64ed198d0f42ff5ba7f76e4f296d456bd245aadf",
            Strength=1.1,
            Armor=0.9,
            Intelligence=0.8,
            Speed=1.1
        )

        self._rage = 0
        # self.Type = EWeaponType.Shadowed
        self.BA = f"Deals {self.User.Strength * 1.1 - self.User.Perception * 0.1:.0f} _(110% of your `Strength` - 20% of your `Armor`)_ and increases `Rage` stacks by 3. (Current `Rage` stacks: {self.Rage})\_Each Rage stack enhances your Strength by 3 and decreases your Perception by 2_"
        # self.Description
        self.Abilities = {
            "Enrage": {
                "Brief": "You let the `Rage` inside your Sword invade your body",
                "Description": "You let the `Rage` inside your Sword invade your body, adding 5 `Rage` stacks.\n\n_16 Stamina_",
                "Stamina": 16,
                "Callable": self.Enrage,
                "Targets": 0
            },
            "Raging Strike": {
                "Brief": "You use your rage to strike a powerful hit to your target",
                "Description": f"You strike a powerful hit to your target dealing {self.User.Strength * (0.8 + (0.1 * self.Rage // 5)):.0f} _((80 + 10 per 5 `Rage` stack)% of your `Strength`)_. This `Ability` removes 2 stack of `Rage`\n_This ability can `Critically Strike` for {self.User.CritDamage:.0%} of the damage_\n\n_36 Stamina_",
                "Stamina": 36,
                "Callable": self.RagingStrike,
                "Targets": 1
            },
            "Raging Pierce": {
                "Brief": "You focus to strike a precise hit to your target",
                "Description": f"You stike a precise hit to your target dealing {self.User.Strength * (0.5 + 0.1 * self.Rage):.0f} _((50 + 10 per `Rage` stack)% of your `Strength`)_ and `Wounding` them by 10% of the damage for {self.Rage} _(`Rage` stack)_ turns. This `Ability` removes 5 `Rage` stack.\n\n_32 Stamina_",
                "Stamina": 32,
                "Callable": self.RagingPierce,
                "Targets": 1
            },
            "Calm Down": {
                "Brief": "You focus and recover conscience, repelling your Sword's `Rage`",
                "Description": f"Removes all of your `Rage` stacks and restores {0.1 * self.Rage:.0%} `Missing Health`\n_Removig `Rage` stacks will return your Strength and Perception to their original values_\n\n_22 Stamina_",
                "Stamina": 22,
                "Callable": self.CalmDown,
                "Targets": 0
            },
        }

    @property
    def Rage(self) -> int:
        return self._rage

    @Rage.setter
    def Rage(self, value: int):
        if value < 0:
            return

        self.User.Perception += self._rage * 2
        self.User.Strength -= self._rage * 3

        self._rage = value

        self.User.Perception -= self._rage * 2
        self.User.Strength += self._rage * 3

    def BaseAttack(self, target: 'Player'):
        crit = random.randint(0, 100)
        critical = crit <= self.User.CritChance

        self.Rage += 3

        damage = self.User.Strength * 1.1 - self.User.Perception * 0.1
        damage *= self.User.CritDamage if critical else 1
        output = target.TakeDamage(round(damage), EDamage.BaseAttack)

        log = f"{self.User.name} attacked {target.name} and dealt {output:.0f} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}\n\n{self.User.name}'s `Rage` stack: {self.Rage}"
        return log

    def Enrage(self, *args, **kwargs):
        self.User.cStamina -= self.Abilities["Enrage"]["Stamina"]
        self.Rage += 5
        
        log = f"{self.User.name} used `Enrage` and increased their `Rage` stacks by 5. {self.User.name}'s `Rage` stacks: {self.Rage}"
        return log

    def RagingStrike(self, target: 'Player', *args, **kwargs):
        self.User.cStamina -= self.Abilities["Raging Strike"]["Stamina"]

        crit = random.randint(0, 100)
        critical = crit <= self.User.CritChance
        damage = self.User.Strength * (0.8 + (0.1 * self.Rage // 5))
        damage *= self.User.CritDamage if critical else 1
        output = target.TakeDamage(damage, EDamage.Ability)
        self.Rage -= 2
        
        if critical:
            log = f"{self.User.name} has used `Raging Strike` on {target.name} and scored a `Critical Strike`, dealing them {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        else:
            log = f"{self.User.name} used `Raging Strike` on {target.name} dealing {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        
        return log 

    def RagingPierce(self, target: 'Player', *args, **kwargs):
        self.User.cStamina -= self.Abilities["Raging Pierce"]["Stamina"]

        damage = self.User.Strength * (0.5 + 0.1 * self.Rage)
        wound = round(damage * 0.1)
        target.AddWound(self.User, wound, 4, EWound.Wound)
        output = target.TakeDamage(damage, EDamage.Ability)

        self.Rage -= 5

        log = f"{self.User.name} used `Raging Pierce` on {target.name}, dealing {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log + f"\n{target.name} is now `Wounded` and will suffer {wound} damage for {self.Rage + 5} turns."

    def CalmDown(self, *args, **kwargs):
        self.User.cStamina -= self.Abilities["Calm Down"]["Stamina"]

        perc = 0.1 * self.Rage
        healing = perc * (self.User.Health - self.User.cHealth)
        self.User.GetHealed(healing, EHeal.Normal, self.User)
        self.Rage = 0

        log = f"{self.User.name} used `Calm Down`, healing theirself for {healing:.0f} `Health` and removing all of their `Rage` stacks."
        return log
        
