from typing import TYPE_CHECKING
from .weapon import Weapon
from core.Resources import *

if TYPE_CHECKING:
    from core.Lobby import Player

__all__ = ('TitansGauntlet',)

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
        self.Abilities = (
            self._base_attack,
            Ability(
                'Tempest',
                'You call a tempest of meteors to fall towards your enemies',
                f'You call a tempest of meteors to fall towards your enemies dealing {self.User.cStamina * 0.8:.0f} damage _(80% of your `Stamina`)_\n\n_13% Current Health ({int(self.User.cHealth * 0.13)})_',
                int(self.User.cHealth * 0.13), CostType.Health,
                self.Tempest, -1
            ),
            Ability(
                'Titan Overload',
                'You focus to free all of your energy',
                f'You explode dealing {self.User.cStamina * 2} damage _(200% of your `Stamina`)_ to all of your enemies\n\n_50% Current Health ({int(self.User.cHealth * 0.5)})_',
                int(self.User.cHealth * 0.5), CostType.Health,
                self.TitanOverload, -1
            ),
            Ability(
                'Thunder Shot',
                'You attack your target with a powerful fist, empowered by your energy',
                f'You explode a fist that deals {self.User.Strength * 0.8 + self.User.cStamina * 0.5:.0f} damage _(80% of your `Strength` + 50% of your `Stamina`)_\n\n_14% Current Health ({int(self.User.cHealth * 0.14)})_',
                int(self.User.cHealth * 0.14), CostType.Health,
                self.ThunderShot, 1
            ),
            Ability(
                'Meditate',
                'You start to meditate placating yourself',
                f'You recover 20% of your `Health` but your `Stamina` decreases by 20\n\n_0 Current Health_',
                0, CostType.Null, 
                self.Meditate, 0
            )
        )

    def Tempest(self, target: list['Player'], _):
        self.User.TakeDamage(self.Abilities[1].cost, EDamage.TrueDamage, False)
        damage = self.User.cStamina * 0.8
        for enemy in target:
            enemy.TakeDamage(damage, EDamage.Ability)

        log = f"{self.User.name} used `Tempest` and dealt {damage} to every enemy"
        return log

    def TitanOverload(self, target: list['Player'], _):
        self.User.TakeDamage(self.Abilities[2].cost, EDamage.TrueDamage, False)

        damage = self.User.cStamina * 2
        for enemy in target:
            enemy.TakeDamage(damage, EDamage.Ability)
        
        log = f"{self.User.name} used `Titan Overload` and dealt {damage} to every enemy"
        return log

    def ThunderShot(self, target: 'Player', _):
        self.User.TakeDamage(self.Abilities[3].cost, EDamage.TrueDamage, False)
        damage = self.User.Strength * 0.8 + self.User.cStamina * 0.5
        output = target.TakeDamage(damage, EDamage.Ability)

        log = f"{self.User.name} used `Thunder Shot` on {target.name} and dealth them {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def Meditate(self, _, __):
        heal = self.User.Health * 0.2
        self.User.GetHealed(round(heal), EHeal.Normal, self.User)
        self.User.cStamina -= 20

        log = f"{self.User.name} used `Meditate` and recovered {heal}.\n{self.User.name}'s `Health`: {self.User.cHealth}/{self.User.Health}"
        return log
