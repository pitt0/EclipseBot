from typing import Literal, Optional, Type, Any
from colorthief import ColorThief
from discord import DMChannel

import asyncio
import discord
import json

from discord.user import _UserTag

from .resources import *
from .overtimedamage import OverTimeDamage
from .status import Status

from ...Weapons import Weapon as _Weapon
from ...Resources import (
    EDamage, 
    EHeal, 
    EStatus, 
    ECondition, 
    EWound
    )


__all__ = (
    'Player'
)

path = 'game/stats.json'
with open(path) as f: statistics = json.load(f)
Position = tuple[int, int]

class Player(discord.User):

    __slots__ = (
        
        '_user',
        '__role',
        '__channel',

        '__activity',
        '__busy',

        '__chealth',
        '__cstamina',
        '_coordinates',
        '__overtime_damage',
        '__stats',
        '_status',
        '__team',

        'Description',
        '__weapon',
        'Position'

    )

    def __init__(self, user: discord.User, role = None):
        self._user = user
        self.__role = role # Used in bot subclass
        self.__channel: discord.TextChannel = None
        
        self.__team: ETeam = None
        self._coordinates: dict[str, list[Position]] = None
        
        self.__weapon: _Weapon = None
        try:
            self.__stats: dict[str, int | float] = statistics[role or self.__class__.__name__]
        except KeyError:
            self.__stats = {'Health': 12, 'Stamina': 13, 'Speed': 15}
            print(f'{self.__class__.__name__} is not into stats')

        self.__chealth = round(self.__stats['Health'])
        self.__cstamina = round(self.__stats['Stamina'])

        self._status = Status()
        self.__overtime_damage = OverTimeDamage()

        self.__activity = EActivity.Idle
        self.__busy: asyncio.Future[bool] | None = None

        self.Description: str = ''
        self.Position: Position = None
        

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, _UserTag) and self._user.id == __o.id 

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)
    
    def __repr__(self) -> str:
        return f'User={self.name} class={self.__class__.__name__}'

    @property
    def activity(self) -> EActivity:
        """:enum:`EActivity`: What user is doing.
        
        If user is doing nothing, :value:`EActivity.Idle` is returned.
        If user's activity is not :value:`EActivity.Idle`, user has a waiting timer.
        """
        return self.__activity

    @activity.setter
    def activity(self, value: EActivity) -> None:
        self.__activity = value
        if value == EActivity.Idle:
            if self.__busy is not None and not self.__busy.done():
                self.__busy.set_result(False)
            self.__busy = None
        else:
            if self.__busy is not None:
                return
            loop = asyncio.get_running_loop()
            self.__busy = loop.create_future()

    async def wait_ready(self):
        if self.activity == EActivity.Idle:
            return
        assert self.__busy is not None
        return await self.__busy

    async def send(
        self,
        content: str | None = None, 
        embed: discord.Embed = None, 
        view: discord.ui.View = None
    ):
        if self.__channel is not None:
            return await self.__channel.send(content, embed=embed, view=view)
        return await self._user.send(content, embed=embed, view=view)

    async def SetChannel(self, channel: discord.TextChannel | int) -> None:
        if type(channel) is int:
            guild = self._user.mutual_guilds[0]
            channel = await guild.fetch_channel(channel) 
            
        self.__channel = channel

    @property
    def bot(self) -> bool:
        return self._user.bot

    @property
    def name(self) -> str:
        return self._user.display_name

    @property
    def display_name(self) -> str:
        return self._user.display_name

    @property
    def mention(self) -> str:
        return self._user.mention

    @property
    def id(self) -> int:
        return self._user.id

    @property
    def bot(self) -> bool:
        return self._user.bot
        
    @property
    def color(self) -> discord.Colour:
        """:class:`Color`: The most present color into user's :class:`Avatar`"""
        # if self._user.avatar is None:
        return discord.Colour.default()
        # TODO: Add a setting where players choose their own color
        """image_byte = asyncio.run_coroutine_threadsafe(self._user.avatar.read(), asyncio.get_event_loop())
        image = ColorThief(image_byte)
        palette = image.get_palette()
        for color in palette:
            if all(c > 200 or c < 30 for c in color):
                palette.remove(color)
        return discord.Colour.from_rgb(*palette[0])"""

    @property
    def team(self) -> ETeam:
        """:enum:`ETeam`: The team the user is part of."""
        return self.__team

    @team.setter
    def team(self, value: ETeam):
        if value == self.__team:
            raise AlreadyInTeam
        self.__team = value

    @property
    def role(self):
        return self.__role or self.__class__.__name__

    @property
    def Alive(self) -> bool:
        return self.cHealth > 0

    @property
    def Health(self) -> int:
        return round(self.__stats['Health'])

    @Health.setter
    def Health(self, value: int) -> int:
        assert value > 0
        self.__stats['Health'] = value
    @property
    def cHealth(self) -> int:
        return round(self.__chealth)

    @cHealth.setter
    def cHealth(self, value: int) -> int:
        if value < 0:
            value = 0
        self.__chealth = value

    @property
    def Stamina(self) -> int:
        return round(self.__stats['Stamina'])

    @Stamina.setter
    def Stamina(self, value: int) -> int:
        assert value >= 0 
        self.__stats['Stamina'] = value

    @property
    def cStamina(self) -> int:
        return round(self.__cstamina)

    @cStamina.setter
    def cStamina(self, value: int) -> int:
        assert value >= 0
        if value > self.Stamina:
            value = self.Stamina
        self.__cstamina = value

    @property
    def Strength(self) -> int:
        return round(self.__stats['Strength'])

    @Strength.setter
    def Strength(self, value: int):
        assert value > 0
        self.__stats['Strength'] = value

    @property
    def Armor(self) -> int:
        return round(self.__stats['Armor'])

    @Armor.setter
    def Armor(self, value: int):
        assert value > 0
        self.__stats['Armor'] = value
    
    @property
    def Intelligence(self) -> int:
        return round(self.__stats['Intelligence'])

    @Intelligence.setter
    def Intelligence(self, value: int):
        assert value > 0
        self.__stats['Intelligence'] = value

    @property
    def Perception(self) -> int:
        return round(self.__stats['Perception'])

    @Perception.setter
    def Perception(self, value: int):
        assert value > 0
        self.__stats['Perception'] = value

    @property
    def Speed(self) -> int:
        return round(self.__stats['Speed'])

    @Speed.setter
    def Speed(self, value: int):
        assert value > 0
        self.__stats['Speed'] = value

    @property
    def CritDamage(self) -> float:
        return round(self.__stats['CritDamage'], 2)

    @CritDamage.setter
    def CritDamage(self, value: float):
        """Should never be used"""
        assert value > 0
        self.__stats['CritDamage'] = value
        
    @property
    def CritChance(self) -> int:
        return 25

    @property
    def Shield(self):
        return self.Weapon.Shield

    @Shield.setter
    def Shield(self, value: int):
        if value < 0:
            value = 0
        self.Weapon.Shield = value

    @property
    def Weapon(self):
        return self.__weapon

    @property
    def Abilities(self) -> dict[str, dict[str, Any]]:
        if not self.Weapon:
            return 
        return self.Weapon.Abilities

    @property
    def Image(self) -> str:
        if not self.Weapon:
            return 'https://127.0.0.1'
        return self.Weapon.HolderImage

    def EquipWeapon(self, weapon: Type[_Weapon]):
        self.__weapon = weapon(self)
        self.__overtime_damage.set_player(self)

        self.Health = round(self.Health * self.Weapon.Health)
        self.Stamina = round(self.Stamina * self.Weapon.Stamina)

        self.cHealth = self.Health
        self.cStamina = self.Stamina

        self.Strength = round(self.Strength * self.Weapon.Strength)
        self.Armor = round(self.Armor * self.Weapon.Armor)
        self.Intelligence = round(self.Intelligence * self.Weapon.Intelligence)
        self.Speed = round(self.Speed * self.Weapon.Speed)
        

    def Coordinates(self, used: list[tuple[int, int]], role: Literal['as_player', 'as_enemy']) -> tuple[int, int]:
        """Cheks for all the occupied positions on the field and finds a free one.

        Parameters
        ---
        used: :class:`list[Position]`
            The list of the occupied positions.
        role: :class:`Literal['as_player', 'as_enemy']`
            Whether to search for player's position
        
        Returns
        ---
        :class:`tuple[int, int]`
            Players's position.
        
        Raises
        ---
        :exc:`.PositionNotFound`
            If there are no possible positions remained.
        """
        for position in self._coordinates[role]:
            if position not in used:
                break
        else:
            raise PositionNotFound(f'{self.name} found no position.')
        return position

    def AddStatus(self, status: EStatus, turns: int = 0):
        """Adds an :enum:`EStatus` and an :enum:`ECondition` to :class:`Player`'s :class:`Status`.
        
        Parameters
        ---
        condition: :enum:`ECondition`
            The type of condition that afflicts the :class:`Player`
        status: :enum:`EStatus`
            The status that afflicts the :class:`Player`
        turns: :class:`Optional[int]`
            The number of turns that the :class:`Player` is afflicted
        """
        match status:
            case EStatus.Stunned | EStatus.Blinded | EStatus.Disarmed:
                condition = ECondition.Attacking
            case EStatus.Targeted | EStatus.Transferred | EStatus.Untouchable:
                condition = ECondition.Targeting
            case EStatus.Wounded | EStatus.Burnt:
                raise TypeError('Trying to add a wounding status manually.')
        
        return self._status._add_condition(condition, status, turns)
    
    def AddCondition(self, status: EStatus, turns: int):
        """Adds an :enum:`EStatus` and an :enum:`ECondition` to :class:`Player`'s :class:`Status`.
        
        Parameters
        ---
        condition: :enum:`ECondition`
            The type of condition that afflicts the :class:`Player`
        status: :enum:`EStatus`
            The status that afflicts the :class:`Player`
        turns: :class:`Optional[int]`
            The number of turns that the :class:`Player` is afflicted
        """
        return self.AddStatus(status, turns)

    def CheckStatus(self, status: EStatus) -> bool:
        """Checks if an :enum:`EStatus` condition is in :class:`Player`'s :class:`Status`.
        
        Parameter
        ---
        status: :enum:`EStatus`
            The status to check.
        
        Returns
        ---
        :class:`bool`
            Whether or not :class:`Player` is afflicted by :param:`status` condition
        """
        return self._status._check_status(status)

    def CheckCondition(self, condition: ECondition) -> bool:
        """Checks if an :enum:`ECondition` condition is in :class:`Player`'s :class:`Status`.
        
        Parameter
        ---
        status: :enum:`ECondition`
            The status to check.
        
        Returns
        ---
        :class:`bool`
            Whether or not :class:`Player` is afflicted by :param:`condition`
        """
        return self._status._check_condition(condition)

    def RemoveStatus(self, status: EStatus):
        """Adds an :enum:`EStatus` and an :enum:`ECondition` to :class:`Player`'s :class:`Status`.
        
        Parameters
        ---
        condition: :enum:`ECondition`
            The type of condition that afflicts the :class:`Player`
        status: :enum:`EStatus`
            The status that afflicts the :class:`Player`
        turns: :class:`Optional[int]`
            The number of turns that the :class:`Player` is afflicted
        """
        return self._status._remove_status(status)

    def AddWound(self, source: 'Player', damage: int, turns: int, type: EWound):
        """Adds a Wound to :class:`Player`'s :var:`_overtime_damage`.
        
        This also automatically adds :var:`EStatus.Wounded` or :var:`EStatus.Burnt` to :class:`Player`'s :class:`Status`
        
        Parameters
        ---
        source: :class:`Player`
            The player from whom this player got wounded
        damage: :class:`int`
            The damage this player will suffer every turn.
            The damage is *NOT* split over turns. The player will suffer all the damage in parameter every turn.
        turns: :class:`int`
            The number of turns the wound will remain. Pass -1 to make it permanent.
        type: :enum:`EWound`
            The type of damage. Either :var:`EWound.Wound` or :var:`EWound.Burn`
        """
        return self.__overtime_damage._add_wound(source, damage, turns, type)

    def BaseAttack(self, target: 'Player'):
        return self.Weapon.BaseAttack(target)

    def GetHealed(self, heal: int, type: EHeal, healer: 'Player'):
        match type:
            case EHeal.Normal:
                self.cHealth += heal
                if self.cHealth > self.Health:
                    self.cHealth = self.Health
            case EHeal.Cursed:
                self.cHealth += heal
                self.AddWound(healer, heal//3 + heal%3, 3, EWound.Heal)

    def _mitigate_damage(self, damage):
        damage, self.Shield = damage - self.Shield, self.Shield - damage
        return damage

    def TakeDamage(self, raw_damage: int, source: EDamage, affects_shield: bool = True) -> int:        
        match source:
            case EDamage.BaseAttack:
                if affects_shield:
                    raw_damage = self._mitigate_damage(raw_damage)
                damage = raw_damage * (100/(100+self.Armor))

            case EDamage.Ability:
                if affects_shield:
                    raw_damage = self._mitigate_damage(raw_damage)
                damage = raw_damage * (100/(100+self.Perception))

            case EDamage.TrueDamage:
                if affects_shield:
                    raw_damage = self._mitigate_damage(raw_damage)
                damage = raw_damage

            case _:
                damage = raw_damage * ((100/(100+(self.Armor/2))) + (100/(100+(self.Perception/2))))

        if damage <= 0:
            return 0
        damage = round(damage)
        self.cHealth -= damage
        return damage

    def RestoreStamina(self):
        self.cStamina += 15

    def AfterAttack(self):
        self.Weapon.AfterAttack()
        return

    def EndTurn(self):
        self.Weapon.EndTurn()
        self.RestoreStamina()
        self._status._end_turn()
        otd = self.__overtime_damage._end_turn()
        if otd == 0:
            return 
        log = f"{self.name} took {otd} damage from Wounds and Burns."
        if not self.Alive:
            log += f"\n{self.name} died from Wounds."
        return log