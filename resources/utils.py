from enum import Enum, auto
from dataclasses import dataclass

import discord
from discord.utils import MISSING



__all__ = (
    'Buff',
    'edit_embed',
    'EAttackType',
    'EBuff',
    'ETarget'
)


name = str
value = int | str
inline = bool

async def edit_embed(
    embed: discord.Embed, 
    title: str | None = MISSING, 
    description: str | None = MISSING, 
    colour: list[int] | None = MISSING, 
    author: discord.User | None = MISSING, 
    thumbnail: str | None = MISSING, 
    fields: dict[name, list[value, inline]] | None = MISSING, 
    image: str | None = MISSING,
    footer: str | None = MISSING
) -> discord.Embed:

    if title is not MISSING:
        embed.title = str(title)
    if description is not MISSING:
        embed.description = str(description)
    
    if colour is not MISSING:
        if colour is None:
            embed.color = discord.embeds._EmptyEmbed()
        else:
            embed.color = discord.Colour.from_rgb(*colour)
    
    if author is not MISSING:
        if author is None:
            embed.remove_author()
        else:
            embed.set_author(name=author.display_name, icon_url=author.avatar.url)

    if fields is not MISSING:
        embed.clear_fields()
        if fields is not None:
            for name, value in fields.items():
                embed.add_field(name=name, value=value[0], inline=value[1])

    if thumbnail is not MISSING:
        if thumbnail is None:
            embed.remove_thumbnail()
        else:
            embed.set_thumbnail(url=thumbnail)

    if image is not MISSING:
        if image is None:
            embed.remove_image()
        else:
            embed.set_image(url=image)
    
    if footer is not MISSING:
        if footer is not None:
            embed.set_footer(text=str(footer))
        else:
            embed.remove_footer()

    return embed

class EAttackType(Enum):
    BaseAttack = auto()
    Ability = auto()

class ETarget(Enum):
    Back = auto()
    Done = auto()
    Moved = auto()

class EBuff(Enum):
    Health = auto()
    Stamina = auto()
    Strength = auto()
    Armor = auto()
    Intelligence = auto()
    Perception = auto()


@dataclass
class Buff:
    x: int
    y: int
    buff: EBuff