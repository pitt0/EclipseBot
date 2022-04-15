from discord import SelectOption
import discord

from game import Player, Ability
import resources as res
import game

__all__ = ('Info',)

class AbilityData(discord.ui.Button['Info']):

    def __init__(self, ability: Ability):
        super().__init__(label=str(ability), row=1)
        self.ability = ability

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        self.view.embed = await res.edit_embed(
            embed=self.view.embed,
            title=self.label,
            description=f"of {self.view.player.display_name}'s {self.view.player.Weapon.Name}",
            fields={"Description": (self.ability.long, False)},
            image=self.view.player.Weapon.Image
        )
        
        # children include also selection
        for button in self.view.children:
            if not hasattr(button, '_selected_values') :
                button.disabled = False # type: ignore
        
        self.disabled = True
        await interaction.response.edit_message(embed=self.view.embed, view=self.view)
        

class Info(discord.ui.View):

    def __init__(self, player: Player):
        self.player = player
        self.embed = self.__create_embed(player)
        super().__init__()

    def __create_embed(self, player: Player) -> discord.Embed:
        embed = discord.Embed(title='Statistics', color=player.color)
        embed.set_thumbnail(url=player.Weapon.Image)
        embed.set_image(url=player.Image)
        for key, value in player.info:
            embed.add_field(name=key, value=value, inline=True)
        embed.set_footer(text='`Armor` is applied against `Base Attacks`, `Perception` is applied against `Abilities`')
        return embed

    def reset_default_option(self, select: discord.ui.Select):
        for opt in select.options:
            opt.default = False
        return select

    def remove_buttons(self, select: discord.ui.Select):
        self = self.clear_items()
        self.add_item(select)

    def _create_ability_buttons(self) -> dict[str, tuple[str, bool]]:
        _fields: dict[str, tuple[str, bool]] = {}
        for ability in self.player.Abilities:
            _fields[str(Ability)] = (ability.brief, False)
            self.add_item(AbilityData(ability))
        return _fields

    @discord.ui.select(options=[SelectOption(label="Statistics", default=True), SelectOption(label="Weapon"), SelectOption(label="Exit")])
    async def selection(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.remove_buttons(select)
        select = self.reset_default_option(select)

        click = interaction.data['values'][0] # type: ignore
        match click:
            
            case 'Statistics':
                select.options[0].default = True
                self.embed = await res.edit_embed(
                    embed=self.embed,
                    title="Statistics",
                    thumbnail=self.player.Weapon.Image,
                    fields={key: (value, True) for key, value in self.player.info},
                    image=self.player.Image,
                    footer='`Armor` is applied against `Base Attacks`, `Perception` is applied against `Abilities`'
                )
                await interaction.response.edit_message(embed=self.embed, view=self)
            
            case 'Weapon': 
                select.options[1].default = True
                fields = self._create_ability_buttons()
                self.embed = await res.edit_embed(
                    embed=self.embed,
                    title=f"{self.player.display_name}'s {self.player.Weapon.Name}",
                    fields=fields,
                    image=self.player.Weapon.Image,
                    footer=None
                )
                await interaction.response.edit_message(embed=self.embed, view=self)
            
            case 'Exit':
                await interaction.response.edit_message(content='Exiting...')
                await interaction.message.delete() # type: ignore
                self.player.activity = game.EActivity.Idle
                self.stop()
            