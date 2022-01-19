from typing import TYPE_CHECKING

from ..weapon import Weapon
from ...Resources import *

if TYPE_CHECKING:
    from ...Lobby import Player

__all__ = ('NoblesTome')

class NoblesTome(Weapon):

    Brief = "Increased Intelligence | Focused on Team Fights"
    cost = 500
    __slots__ = ()

    def __init__(self, character):
        super().__init__(
            character=character,
            shield=12,
            wImage="https://cdn.discordapp.com/attachments/866261896600354846/866268480649953330/NoblesSpellBook.jpg",
            hImage="https://cdn.discordapp.com/attachments/668204203960696836/866132673936490546/366ee157497698f20ba5af5fd909f1a8.jpg",
            Intelligence=1.1,
            Strength=0.9
        )
        self.Name = "Noble'sTome"
        # self.Type = EWeaponType.Nobles

        # self.Description
        self.Abilities = {
            "Whimsy": {
                "Brief": "You cast a `Shadow` spell on yourself letting it corrupt your soul",
                "Description": "You cast a spell on yourself sacrificing 12 `Health Points` and increasing your `Intelligence` by 13 and your `Perception` by 7\n\n_23 Stamina_",
                "Stamina": 23,
                "Callable": self.Whimsy,
                "Targets": 0
            },
            "Astral Strike": {
                "Brief": "You call a comet to fall towards your target",
                "Description": f"You call a comet to fall towards your target dealing {self.User.Intelligence * 0.7 + self.User.Health * 0.1:.0f} damage _(70% of your `Intelligence` + 10% of your `Maximum Health`)_\n\n_33 Stamina_",
                "Stamina": 33,
                "Callable": self.AstralStrike,
                "Targets": 1
            },
            "Spiritual Link": {
                "Brief": "You link your team's souls with your enemies' ones, stealing part of their `Health`",
                "Description": f"You link your team's souls with your enemies' ones, dealing {self.User.Intelligence * 0.6 + self.User.Health/self.User.cHealth:.0f} damage (the less Current Health you have the more damage it does) and heal your team by a half of the damage dealt\n\n_50 Stamina_",
                "Stamina": 50,
                "Callable": self.SpiritualLink,
                "Targets": -1
            },
            "Noble Charm": {
                "Brief": "You charm the target, becoming `Targeted`",
                "Description": f"You charm the target dealing {self.User.Intelligence * 0.8} damage _(80% of your `Intelligence`)_ + 30% of target's `Perception` and becoming `Targeted`\n\n_34 Stamina_",
                "Stamina": 34,
                "Callable": self.NobleCharm,
                "Targets": 1
            }
        }

    def Whimsy(self, *args, **kwargs):
        self.User.cStamina -= self.Abilities["Whimsy"]["Stamina"]
        self.User.TakeDamage(12, EDamage.TrueDamage, False)
        self.User.Intelligence += 13
        self.User.Perception += 7
        log = f"{self.User.name} has used `Whimsy` on theirself, sacrificing 12 `Health Points` and increasing their `Intelligence` by 13 and their `Perception` by 7\n{self.User.name}'s `Health`: {self.User.Health}\n{self.User.name}'s `Intelligence`: {self.User.Intelligence}\n{self.User.name}'s `Perception`: {self.User.Perception}"
        return log

    def AstralStrike(self, target: 'Player', *args, **kwargs):
        self.User.cStamina -= self.Abilities["Astral Strike"]["Stamina"]
        damage = self.User.Intelligence * 0.7 + self.User.Health * 0.1
        output = target.TakeDamage(damage, EDamage.Ability)
        log = f"{self.User.name} has used `Astral Strike` on {target.name} dealing {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        return log

    def SpiritualLink(self, target: list['Player'], allies: list['Player']):
        self.User.cStamina -= self.Abilities["Spiritual Link"]["Stamina"]
        damage = self.User.Intelligence * 0.6 + self.User.Health / self.User.cHealth
        heal = damage / 2
        for ally in allies:
            ally.GetHealed(heal, EHeal.Normal, self.User)
        results: dict['Player', int] = {}
        for t in target:
            results[t] = t.TakeDamage(damage, EDamage.Ability)

        log = f"{self.User.name} has used `Spiritual Link` and healed their team by {heal} health hitting {', '.join(enemy.name for enemy in target)} and dealing {damage} damage to every"
        return log

    def NobleCharm(self, target: 'Player', allies: list['Player']):
        self.User.cStamina -= self.Abilities["Noble Charm"]["Stamina"]
        for ally in allies:
            if ally.CheckStatus(EStatus.Targeted):
                ally.RemoveStatus(EStatus.Targeted)
        
        self.User.AddStatus(EStatus.Targeted)
        damage = self.User.Intelligence * 0.8 + target.Perception * 0.3
        output = target.TakeDamage(damage, EDamage.Ability)
        log = f"{self.User.name} used `Noble Charm` on {target.name}, dealing {output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}\n{self.User.name} is now `Targeted`."
        return log