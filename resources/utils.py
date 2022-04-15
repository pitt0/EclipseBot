from enum import Enum, auto
from typing import Any

import discord
from discord.utils import MISSING



__all__ = (
    'edit_embed',
    'EResult'
)


async def edit_embed(
    embed: discord.Embed, 
    title: str | None = MISSING, 
    description: str | None = MISSING, 
    colour: list[int] | None = MISSING, 
    author: discord.User | None = MISSING, 
    thumbnail: str | None = MISSING, 
    fields: dict[str, tuple[Any, bool]] | None = MISSING, 
    image: str | None = MISSING,
    footer: str | None = MISSING
) -> discord.Embed:

    if title is not MISSING:
        embed.title = str(title)
    if description is not MISSING:
        embed.description = str(description)
    
    if colour is not MISSING:
        if colour is None:
            embed.color = discord.Colour.default()
        else:
            embed.color = discord.Colour.from_rgb(*colour)
    
    if author is not MISSING:
        if author is None:
            embed.remove_author()
        else:
            if author.avatar is None:
                print('wtf')
                return discord.Embed(title='Error')
            embed.set_author(name=author.display_name, icon_url=author.avatar.url)

    if fields is not MISSING:
        embed.clear_fields()
        if fields is not None:
            for name, value in fields.items():
                embed.add_field(name=name, value=value[0], inline=value[1])

    if thumbnail is not MISSING:
        if thumbnail is None:
            thumbnail = 'http://localhost:8080'
        embed.set_thumbnail(url=thumbnail)

    if image is not MISSING:
        if image is None:
            image = 'http://localhost:8080'
        embed.set_image(url=image)
    
    if footer is not MISSING:
        if footer is not None:
            embed.set_footer(text=str(footer))
        else:
            embed.remove_footer()

    return embed

class EResult(Enum):
    Back = auto()
    Done = auto()
    Moved = auto()
