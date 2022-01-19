from typing import TYPE_CHECKING

import random

from ..Resources import EDamage

if TYPE_CHECKING:
    from ..Lobby import Player


__all__ = (
    'Weapon',
    'Log'
    )

Log = str

class Weapon:

    __slots__ = (
        "_name",
        "User",
        "Shield",
        "Image",
        "HolderImage",
        "Health",
        "Stamina",
        "Strength",
        "Armor",
        "Intelligence",
        "Speed",
        "BA",
        "Abilities",
        "Type",
        'payload'
    )

    def __init__(self, character: 'Player', shield: int, wImage: str, hImage: str, **stats):
        self.Name = self.__class__.__name__
        self.User = character
        self.Shield = shield
        self.Image = wImage
        self.HolderImage = hImage

        self.Health = stats.get("Health", 1)
        self.Stamina = stats.get("Stamina", 1)
        self.Strength = stats.get("Strength", 1)
        self.Armor = stats.get("Armor", 1)
        self.Intelligence = stats.get("Intelligence", 1)
        self.Speed = stats.get("Speed", 1)

        self.BA = f"Deals {self.User.Strength} damage _(100% of your `Strength`)_"
        self.payload = {
            'damage': 0,
            'critcal': False,
            'wound': False,
            'status': False,
            'statistics': {},
            'other': {}
        }
        # self.Type = EWeaponType.Idle

    @property
    def Name(self):
        return self._name

    @Name.setter
    def Name(self, value: str):
        v = list(value)
        name = v.copy()
        for index, letter in enumerate(v):
            if(letter.isupper() and index != 0):
                name.insert(index, " ")

        self._name = "".join(letter for letter in name)

    def BaseAttack(self, target: 'Player') -> str:

        crit = random.randint(0, 100)
        critical = crit <= self.User.CritChance
        damage: int = self.User.Strength
        damage *= self.User.CritDamage if critical else 1
        dmg_output = target.TakeDamage(damage, EDamage.BaseAttack)

        if critical:
            log = f"{self.User.display_name} has attacked {target.display_name} and has scored a `Critical Strike` for {dmg_output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"
        else:
            log = f"{self.User.display_name} has attacked {target.display_name} for {dmg_output} damage.\n{target.name}'s `Health`: {target.cHealth}/{target.Health}"

        return log

    def AfterAttack(self) -> None:
        return

    def EndTurn(self) -> None:
        return