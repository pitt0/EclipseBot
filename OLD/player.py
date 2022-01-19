import asyncio
import json
from typing import Literal, Type
# from ..Weapons import Weapon
from ..Resources import *
from discord import User
from dataclasses import dataclass

__all__ = ['Player']

with open('game/stats.json') as f:
    stats = json.load(f)


class Player:
    
    __slots__ = (
        # User
        "user", # removed, now Player is a "subclass" of discord.User
        '_user_status', # Done
        "Color", # updated
        "coordinates", # updated

        # Player
        "Class", # Done, property
        "weapon",
        "Alive", # Done, property
        "Status", # Done
        "Shield", # Done, property
        "_otd", # Done
        "priority", # Useless
        "team", # Done, property
        "Health", # Done, property
        "_chealth", # Done
        "Stamina", # Done, propety
        "_cstamina", # Done
        "core", # Done, updated, property
        "DodgeChance", # Done, property
        "CriticalChance", # Done, property
        "CriticalDamage", # Done, property

        # System
        '__busy' # Done
        )

    def __init__(self, user: User):
        self.Class = self.__class__.__name__
        self.user = user
        self._user_status = EUserStatus.Idle
        self.weapon: Weapon = None

        # statistics
        self.Health = self._chealth = stats[self.Class]["Health"]
        self.Stamina = self._cstamina = stats[self.Class]["Stamina"]
        self.core = {
            EStats.Strength: stats[self.Class]["Strength"],
            EStats.Armor: stats[self.Class]["Armor"],
            EStats.Intelligence: stats[self.Class]["Intelligence"],
            EStats.Speed: stats[self.Class]["Speed"]
        }
        self.DodgeChance = round(stats[self.Class]["Dodge"], 2)
        self.CriticalChance: int = 25
        self.CriticalDamage = round(stats[self.Class].get("CritDamage", 1), 2)

        self.Alive = True
        self.Shield = 0
        self.Status = Status()
        self.OverTimeDamage = OverTimeDamage()
        
        self.coordinates: dict[str, list[tuple[int, int]]] = {
            'as_player': [
                (0, 0)
                ],
            'as_enemy': [
                (0, 0)
                ]
        }
        self.priority = EPriority.Normal
        self.Color = [0, 0, 0]
        self.team = None
        
        
        self.__busy: asyncio.Future[bool] = None
    
    def equip_weapon(self, weapon: Type[Weapon]):
        self.weapon = weapon(self)
        self.OverTimeDamage.set_player(self)
        
        self.Health = round(self.Health * self.weapon.Health)
        self._chealth = self.Health

        self.Stamina = round(self.Stamina*self.weapon.Stamina)
        self._cstamina = self.Stamina

        self.core[EStats.Strength] *= self.weapon.Strength
        self.core[EStats.Armor] *= self.weapon.Armor
        self.core[EStats.Intelligence] *= self.weapon.Intelligence
        self.core[EStats.Speed] *= self.weapon.Speed
        for stat in self.core:
            self.core[stat] = round(self.core[stat])
        self.Shield = round(self.weapon.Shield)

    def set_team(self, team: ETeam):
        self.team = team

    def end_waiting(self):
        if not self.__busy.done():
            self.__busy.set_result(False)

    async def wait_ready(self):
        if not self.__busy:
            return
        return await self.__busy 

    @property
    def cHealth(self) -> int:
        return self._chealth
    @cHealth.setter
    def cHealth(self, value):
        if value <= 0:
            self.Alive = True
            self._chealth = 0
            return
        self._chealth = value

    @property
    def cStamina(self) -> int:
        return self._cstamina
    @cStamina.setter
    def cStamina(self, value):
        if value > self.Stamina:
            value = self.Stamina
        self._cstamina = value
        
    @property
    def Strength(self) -> int:
        return self.core[EStats.Strength]
    @Strength.setter
    def Strength(self, value):
        if value < 0:
            raise ValueError
        self.core[EStats.Strength] = value
    
    @property
    def Armor(self) -> int:
        return self.core[EStats.Armor]
    @Armor.setter
    def Armor(self, value):
        if value < 0:
            raise ValueError
        self.core[EStats.Armor] = value

    @property
    def Intelligence(self) -> int:
        return self.core[EStats.Intelligence]
    @Intelligence.setter
    def Intelligence(self, value):
        if value < 0:
            raise ValueError
        self.core[EStats.Intelligence] = value

    @property
    def Speed(self) -> int:
        return self.core[EStats.Speed]
    @Speed.setter
    def Speed(self, value):
        if value < 0:
            raise ValueError
        self.core[EStats.Speed] = value

    @property
    def UserStatus(self) -> EUserStatus:
        return self._user_status

    @UserStatus.setter
    def UserStatus(self, value: EUserStatus):
        match value:
            case EUserStatus.Idle:
                self.end_waiting()
            case _:
                loop = asyncio.get_running_loop()
                self.__busy = loop.create_future()

    
    def TakeDamage(self, damage: Damage) -> EResult:
        match damage.type:
            case EDamageType.BaseAttack:
                if self.Shield:
                    if self.Shield > damage.damage:
                        self.Shield -= damage.damage
                        return EResult.Shield
                    damage.damage -= self.Shield
                    self.Shield = 0

                if damage.damage - self.Armor <= 0:
                    return EResult.NoDamage

                self.cHealth -= damage.damage - self.Armor
                if damage.critical: 
                    return EResult.CriticalDamage
                else: 
                    return EResult.Idle

            case EDamageType.Ability:
                if damage.damage - (self.Armor * 0.75 + self.Intelligence * 0.25) <= 0:
                    return EResult.NoDamage
                
                self.cHealth -= damage.damage - (self.Armor * 0.75 + self.Intelligence * 0.25)
                return EResult.Idle
            
            case EDamageType.TrueDamage:
                self.cHealth -= damage.damage
                return EResult.Idle


    def GetHealed(self, heal: Heal):
        match heal.type:
            case EHealType.Normal:
                self.cHealth += heal.health
                if self.Health < self.cHealth:
                    self.cHealth = self.Health

            case EHealType.Cursed:
                self.cHealth += heal.health
                self.AddWound(heal.healer, heal.health//3 + heal.health%3, 3)
            

    def StatsChange(self, stats: dict[EStats, int]) -> EResult:
        temp = {}
        for stat in stats:
            temp[stat] = self.core[stat]
            try:
                match stat:
                    case EStats.Strength:
                        self.Strength = stats[stat]

                    case EStats.Armor:
                        self.Armor = stats[stat]

                    case EStats.Intelligence:
                        self.Intelligence = stats[stat]
                    
                    case EStats.Speed:
                        self.Speed = stats[stat]
            
            except ValueError:
                for stat in temp:
                    self.core[stat] = temp[stat]
                return EResult.NoStats
            
            else:
                return EResult.StatsChanged

    def AddStatus(self, status: EStatus, turns: int = 0):
        match status:
            case EStatus.Stunned | EStatus.Blinded:
                condition = ECondition.Attacking
            case EStatus.Targeted | EStatus.Transferred | EStatus.Untouchable:
                condition = ECondition.Targeting
            case EStatus.Wounded | EStatus.Burnt:
                condition = ECondition.TakeDamage
        
        return self.Status._add_condition(condition, status, turns)
    
    def AddCondition(self, status: EStatus, turns: int):
        return self.AddStatus(status, turns)

    def CheckStatus(self, status: EStatus) -> bool:
        """Checks if a `Status Condition` is in `Player`'s Status."""
        return self.Status._check_status(status)

    def RemoveStatus(self, status: EStatus):
        return self.Status._remove_status(status)

    def AddWound(self, source: 'Player', damage: int, turns: int, type: EStatus):
        return self.OverTimeDamage._add_wound(source, damage, turns, type)

    def GetWounded(self):
        damages = self.OverTimeDamage._wound_player()
        for source, damage in damages:
            self.TakeDamage(Damage(damage, EDamageType.Wound))

    def RestoreStamina(self):
        self.cStamina += 5

    def EndTurn(self):
        self.RestoreStamina()
        self.GetWounded()