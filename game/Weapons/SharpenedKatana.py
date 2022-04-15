from typing import TYPE_CHECKING

import random

from .weapon import Weapon
from game.Resources import *

if TYPE_CHECKING:
    from game.Lobby import Player

__all__ = ('SharpenedKatana',)

class SharpenedKatana(Weapon):

    Brief = "Increased Strength | Stronger in Team Fights"
    cost = 500
    __slots__ = "UsedAbilities"

    def __init__(self, character):
        super().__init__(
            character=character,
            shield=0,
            wImage="https://cdn.discordapp.com/attachments/668204203960696836/866133243816050710/d7101cc7cb4a20de392ef35d783e8aa7.jpg",
            hImage="https://i.pinimg.com/236x/79/63/07/79630721befe3bc6477e0a7cbab3d068.jpg",
            Health=1.1,
            Strength=1.2,
            Armor=0.7
        )
        self.UsedAbilities = []
        
        # self.Type = EWeaponType.Nobles
        self._base_attack.long = self._base_attack.brief = f"Deals {self.User.Strength} damage _(100% of your `Strength`)_ and restores 20% of your `Maximum Stamina` (you do not restore `Stamina` after every Turn)"
        # self.Description - Has to use all the abilities before to use one twice
        self.Abilities = (
            self._base_attack,
            Ability(
                'Harakiri',
                'You empower your Katana pouring your own blood on it.',
                'You sacrifice 30 `Health Points` to increase your `Strength` by 21\n\n_32 Stamina_',
                32, CostType.Stamina,
                self.Harakiri,
                0
            ),
            Ability(
                'Blood Thirst',
                "Your Katana follows enemies' blood damaging the `Wounded` ones.",
                f'You attack every `Wounded` enemy dealing {self.User.Strength * 0.8:.0f} damage _(80% of your `Strength`)_\n\n_41 Stamina_',
                41, CostType.Stamina,
                self.BloodThirst,
                -2
                ),
            Ability(
                'Sharpened Breath',
                'You instantly jump to the target lacerating their flesh.',
                f"You instantly jump to the target lacerating their flesh dealing {self.User.Strength * 0.8:.0f} _(80% of your `Strength`)_ + 25% of target's `Strength` damage, `Wounding` them for 9 damage over turn for 3 turns\n_This ability can `Critically Strike` for {self.User.CritDamage:.2%} of the damage_\n\n_31 Stamina_",
                31, CostType.Stamina,
                self.SharpenedBreath,
                1
            ),
            Ability(
                'Blood Moon',
                "You benefit from Darkness and Moonlight, pinpointing your targets' wounds, and lacerating those points.",
                f"You lacerate targets' `Wounds` dealing {self.User.Strength * 0.6 + self.User.Intelligence * 0.4:.0f} damage _(60% of your `Strength` + 40% of your `Intelligence`)_. If the target is `Wounded` you also deal 40% of their `Current Health`\n\n_47 Stamina_",
                47, CostType.Stamina,
                self.BloodMoon,
                -1
            )
        )

    def UseAbility(self, ability: str):
        self.UsedAbilities.append(ability)

    def BaseAttack(self, target: 'Player'):
        self.User.cStamina += int(self.User.Stamina * 0.2)
        return super().BaseAttack(target)

    def Harakiri(self, _, __):
        self.User.cStamina -= self.Abilities[1].cost
        self.UseAbility('Harakiri')
        self.User.TakeDamage(raw_damage=30, source=EDamage.TrueDamage, affects_shield=False)
        self.User.Strength += 21
        log = f"{self.User.name} used `Harakiri`. {self.User.name} lost 30 `Health Points` and increased their `Strength` by 21.\n{self.User.name}'s `Health`: {self.User.cHealth}/{self.User.Health}\n{self.User.name}'s `Strength`: {self.User.Strength}"
        return log

    def BloodThirst(self, target: list['Player'], _):
        self.User.cStamina -= self.Abilities[2].cost
        self.UseAbility('Blood Thirst')
        
        damage = self.User.Strength * 0.8
        for enemy in target:
            enemy.TakeDamage(damage, EDamage.Ability)

        log = f"""{self.User.name} used `Blood Thirst` and attacked every `Wounded` enemy dealing {damage} damage to each of them"""

        return log

    def SharpenedBreath(self, target: 'Player', _):
        self.User.cStamina -= self.Abilities[3].cost
        self.UseAbility('Sharpened Breath')

        target.AddWound(self.User, 3, 3, EWound.Wound)

        crit = random.randint(0, 100)
        critical = crit <= self.User.CritChance
        damage = self.User.Strength * 0.8 + target.Strength * 0.25
        damage *= self.User.CritDamage if critical else 1
        output = target.TakeDamage(damage, EDamage.Ability)
        
        if critical:
            log = f"{self.User.name} used `Sharpened Breath` on {target.name} and scored a `Critical Strike` dealing {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        else:
            log = f"{self.User.name} used `Sharpened Breath` on {target.name} dealing them {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"

        return log + f'\n{target.name} is now `Wounded` and will suffer 3 damage for three turns.'

    def BloodMoon(self, target: list['Player'], _):
        self.User.cStamina -= self.Abilities[4].cost
        self.UseAbility('Blood Moon')
        
        for enemy in target:
            if enemy.CheckStatus(EStatus.Wounded):
                damage = self.User.Strength * 0.6 + self.User.Intelligence * 0.4 + enemy.cHealth * 0.4
            else:
                damage = self.User.Strength * 0.6 + self.User.Intelligence * 0.4
                
            enemy.TakeDamage(round(damage), EDamage.Ability)
        
        log = f"{self.User.name} used `Blood Moon` and dealt {round(self.User.Strength * 0.6 + self.User.Intelligence * 0.4)} to every enemy _(+40% of enemy's `Current Health` if `Wounded`)_"

        return log

    def AfterAttack(self) -> None:
        if len(self.UsedAbilities) == 4:
            self.UsedAbilities = []
        return super().AfterAttack()