from typing import Callable

from discord import SelectOption
import discord

from game import Player
import resources as res
import game

__all__ = ('Info')

class Ability(discord.ui.Button['Info']):

    def __init__(self, ability: str):
        super().__init__(label=ability, row=1)

    async def callback(self, interaction: discord.Interaction):
        self.ability = self.view.player.Abilities[self.label]
        self.view.embed = await res.edit_embed(
            embed=self.view.embed,
            title=self.label,
            description=f"of {self.view.player.display_name}'s {self.view.player.Weapon.Name}",
            fields={"Description": [self.ability["Description"], False]},
            image=self.view.player.Weapon.Image
        )
        
        # children may not have buttons
        for button in self.view.children:
            if not hasattr(button, '_selected_values') :
                button.disabled = False
        
        self.disabled = True
        await interaction.response.edit_message(embed=self.view.embed, view=self.view)
        

class Info(discord.ui.View):
    def __init__(self, player: Player):
        self.player = player
        
        embed = discord.Embed(title='Statistics', color=player.color)
        embed.set_thumbnail(url=player.Weapon.Image)
        embed.set_image(url=player.Image)
        embed.add_field(name="Class", value=self.player.role, inline=True)
        embed.add_field(name='Weapon', value=self.player.Weapon.Name, inline=True)
        embed.add_field(name='Status', value='-', inline=False)
        embed.add_field(name='Health', value=f'{self.player.cHealth}/{self.player.Health}', inline=True)
        embed.add_field(name='Stamina', value=f'{self.player.cStamina}/{self.player.Stamina}', inline=True)
        embed.add_field(name='Strength', value=self.player.Strength, inline=True)
        embed.add_field(name='Armor', value=self.player.Armor, inline=True)
        embed.add_field(name='Intelligence', value=self.player.Intelligence, inline=True)
        embed.add_field(name='Perception', value=self.player.Perception, inline=True)
        embed.add_field(name='Speed', value=self.player.Speed, inline=True)
        embed.add_field(name='Critical Strike Damage', value=f"{self.player.CritDamage:.0%}", inline=True)
        embed.add_field(name='Critical Strike Chance', value=f"{self.player.CritChance}%", inline=True)
        embed.set_footer(text='`Armor` is applied against `Base Attacks`, `Perception` is applied against `Abilities`')
        self.embed = embed

        super().__init__()

    def reset_default_option(self, select: discord.ui.Select):
        for opt in select.options:
            opt.default = False
        return select

    def remove_buttons(self):
        children: list[discord.ui.Item] = self.children.copy()
        for child in children:
            if not hasattr(child, '_selected_values'):
                self.remove_item(child)

    def add_ability_buttons(self, fields: dict[str, list[Callable, bool]]) -> dict[str, list[Callable, bool]]:
        for ability in self.player.Abilities:
            fields[ability] = [self.player.Abilities[ability]["Brief"], False]
            self.add_item(Ability(ability))
        return fields

    @discord.ui.select(options=[SelectOption(label="Statistics", default=True), SelectOption(label="Weapon"), SelectOption(label="Exit")])
    async def selection(self, select: discord.ui.Select, interaction: discord.Interaction):
        self.remove_buttons()
        select = self.reset_default_option(select)

        click = interaction.data['values'][0]
        match click:
            
            case 'Statistics':
                select.options[0].default = True
                self.embed = await res.edit_embed(
                    embed=self.embed,
                    title="Statistics",
                    thumbnail=self.player.Weapon.Image,
                    fields={
                        "Class": [self.player.role, True],
                        "Weapon": [self.player.Weapon.Name, True],
                        "Status": ['-', False],
                        "Health": [f"{self.player.cHealth}/{self.player.Health}", True],
                        "Stamina": [f"{self.player.cStamina}/{self.player.Stamina}", True],
                        "Strength": [self.player.Strength, True],
                        "Armor": [self.player.Armor, True],
                        "Intelligence": [self.player.Intelligence, True],
                        "Perception": [self.player.Perception, True],
                        "Speed": [self.player.Speed, True],
                        "Critical Strike Damage": [f"{self.player.CritDamage:.0%}", True],
                        "Critical Strike Chance": [f"{self.player.CritChance}%", True]
                    },
                    image=self.player.Image,
                    footer='`Armor` is applied against `Base Attacks`, `Perception` is applied against `Abilities`'
                )
                await interaction.response.edit_message(embed=self.embed, view=self)
            
            case 'Weapon': 
                select.options[1].default = True
                fields = self.add_ability_buttons({"Base Attack": [self.player.Weapon.BA, False]})
                self.embed = await res.edit_embed(
                    embed=self.embed,
                    title=f"{self.player.display_name}'s {self.player.Weapon.Name}",
                    fields=fields,
                    image=self.player.Weapon.Image,
                    footer=None
                )
                await interaction.response.edit_message(embed=self.embed, view=self)
            
            case 'Exit':
                await interaction.response.defer()
                await interaction.message.delete()
                self.player.activity = game.EActivity.Idle
                self.stop()
            