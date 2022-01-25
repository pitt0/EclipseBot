import discord
from resources import *
from game import Player, ETeam, AlreadyInTeam

class Teams(discord.ui.View):
    """The discord View from where players can choose their team"""

    def __init__(self, players: list[Player]):
        super().__init__(timeout=None)
        self.players = players

        embed = discord.Embed(
            title="Team",
            description='Different teams have different Shops and different Weapons'
            )
        embed.add_field(name='Shadows', value='-')
        embed.add_field(name='Nobles', value='-')
        self.embed = embed

        self.response: discord.Message = None


    async def update_embed(self):
        self.embed = await edit_embed(
            embed=self.embed,
            title='Team',
            fields={
                'Shadows': [
                    ''.join(f'{player.mention}\n' for player in self.players if player.team is ETeam.Shadow)
                    if any(player.team is ETeam.Shadow for player in self.players) 
                    else '-',
                    True
                ],
                'Nobles': [
                    ''.join(f'{player.mention}\n' for player in self.players if player.team is ETeam.Noble)
                    if any(player.team is ETeam.Noble for player in self.players)
                    else '-',
                    True
                ]
            }
        )
        return

    def is_player(self, user: discord.User | discord.Member):
        return user in self.players
    
    def adapt_bots(self):
        for player in self.players:
            shadows = [player for player in self.players if player.team is ETeam.Shadow]
            nobles = [player for player in self.players if player.team is ETeam.Noble]
            if player.team is None:
                if len(shadows) < len(nobles):
                    player.team = ETeam.Shadow
                else:
                    player.team = ETeam.Noble

    async def check_ready(self) -> bool:
        children: list[discord.Button] = self.children
        non_bots = [player for player in self.players if not player.bot]
        ready_btn = children[2]
        if any(player.team is None for player in self.players):
            
            if all(player.team is not None for player in non_bots):
                self.adapt_bots()
                ready_btn.disabled = False
                return True

            ready_btn.disabled = True
            return False
        
        if all(player.team is ETeam.Shadow for player in self.players) or all(player.team is ETeam.Noble for player in self.players):
            
            if non_bots != []:
                self.adapt_bots()
                ready_btn.disabled = False
                return True

            ready_btn.disabled = True
            return False

        ready_btn.disabled = False
        return True

    @discord.ui.button(label='Shadows')
    async def Shadows(self, button: discord.Button, interaction: discord.Interaction):
        if not self.is_player(interaction.user):
            return

        try:
            index = self.players.index(interaction.user)
            self.players[index].team = ETeam.Shadow
        except AlreadyInTeam:
            await interaction.response.send_message('You are already in Shadow Team', ephemeral=True)
            return
        
        await self.check_ready()

        await self.update_embed()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='Nobles')
    async def Nobles(self, button: discord.Button, interaction: discord.Interaction):
        if not self.is_player(interaction.user):
            return

        try:
            index = self.players.index(interaction.user)
            self.players[index].team = ETeam.Noble
        except AlreadyInTeam:
            await interaction.response.send_message('You are already in Noble Team', ephemeral=True)
            return

        await self.check_ready()

        await self.update_embed()
        await interaction.response.edit_message(embed=self.embed, view=self)
    
    @discord.ui.button(label='Ready', disabled=True)
    async def Ready(self, button: discord.Button, interaction: discord.Interaction):
        return self.stop()

    async def on_timeout(self) -> None:
        children: list[discord.Button] = self.children
        for child in children:
            child.disabled = True

        await self.response.edit(view=self)
        self.stop()