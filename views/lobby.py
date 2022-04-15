import discord
import datetime
import pytz

from resources import *


class Lobby(discord.ui.View):
    """The discord View from where people can join a game.
    
    Parameter
    ---
    player :class:`discord.User | discord.Member`
        The person who requested to play.
    """

    __slots__ = (
        'players',
        'embed',
        'response'
        )


    def __init__(self, player: discord.User | discord.Member):
        super().__init__()
        self.players: list[discord.User | discord.Member] = []
        self.players.append(player)

        embed = discord.Embed(title='Lobby', color=discord.Color.from_rgb(3, 97, 178))
        embed.add_field(name='Player 1', value=player.mention, inline=False)
        embed.set_footer(text=datetime.datetime.now(tz=pytz.timezone('Europe/Rome')).strftime('%A, %H:%M:%S'))
        self.embed = embed

        self.response: discord.Message | None = None

    @property
    def children(self) -> list[discord.ui.Button]:
        return [child for child in self.children if hasattr(child, 'disabled')]
    
    async def update_embed(self) -> None:
        self.embed = await edit_embed(
            embed=self.embed,
            title='Lobby',
            colour=[3, 97, 178],
            fields={f'Player{x+1}': (player.mention, False) for x, player in enumerate(self.players)},
            )
        self.check_ready()

    def check_ready(self):
        if len(self.players) >= 2:
            self.children[-1].disabled = False
        else:
            self.children[-1].disabled = True


    def add_player(self, player: discord.Member | discord.User):
        self.players.append(player)
        if len(self.players) == 10:
            self.children[0].disabled = True
            self.children[2].disabled = True

    def remove_player(self, player: discord.Member | discord.User):
        self.players.remove(player)
        if len(self.players) < 10:
            self.children[0].disabled = False
            self.children[2].disabled = False


    @discord.ui.button(label='Join', disabled=False)
    async def Join(self, interaction: discord.Interaction, _):
        if interaction.user in self.players:
            await interaction.response.send_message("You are already in the lobby", ephemeral=True)
            return
         
        self.add_player(interaction.user)

        await self.update_embed()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='Exit')
    async def Exit(self, interaction: discord.Interaction, _):
        if interaction.user not in self.players:
            await interaction.response.send_message("You are not in the lobby", ephemeral=True)
            return

        self.remove_player(interaction.user)
        if not self.players:
            if interaction.message is None:
                self.stop()
                return
            await interaction.message.delete()
            self.stop()
            return
        
        await self.update_embed()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='Ready', disabled=True)
    async def Ready(self, interaction: discord.Interaction, _):
        if interaction.user not in self.players:
            await interaction.response.send_message("You are not in the lobby", ephemeral=True)
            return
        self.stop()

    async def on_timeout(self) -> None:
        children: list[discord.ui.Button] = self.children
        for child in children:
            child.disabled = True
        self.players = []
        if self.response is not None:
            await self.response.edit(view=self)
        self.stop()