import discord
import core
from discord import SelectOption


__all__ = (
    'shadow_item',
    'noble_item',
    'SHADOW_ITEMS',
    'NOBLE_ITEMS',
    'Shop'
)


SHADOW_ITEMS = [
    SelectOption(label=f"Corrupted Rod ({core.CorruptedRod.cost}g)", value='6', description=core.CorruptedRod.Brief),
    SelectOption(label=f"Cursed Blade ({core.CursedBlade.cost}g)", value='1', description=core.CursedBlade.Brief),
    SelectOption(label=f"Dimensional Sphere ({core.DimensionalSphere.cost}g)", value='2', description=core.DimensionalSphere.Brief),
    SelectOption(label=f"Dreadful Spell Book {core.DreadfulSpellBook.cost}g", value='3', description=core.DreadfulSpellBook.Brief),
    SelectOption(label=f"Raging Sword ({core.RagingSword.cost}g)", value='4', description=core.RagingSword.Brief),
    SelectOption(label=f"Reaper Bow ({core.ReaperBow.cost}g)", value='5', description=core.ReaperBow.Brief),
    SelectOption(label=f"Shadow's Dagger ({core.ShadowsDagger.cost}g)", value='7', description=core.ShadowsDagger.Brief)
]

NOBLE_ITEMS = [
    SelectOption(label=f"Core Spear ({core.CoreSpear.cost}g)", value='1', description=core.CoreSpear.Brief),
    SelectOption(label=f"Elemental Bow ({core.ElementalBow.cost}g)", value='2', description=core.ElementalBow.Brief),
    SelectOption(label=f"Enlightened Bow ({core.EnlightenedBow.cost}g)", value='3', description=core.EnlightenedBow.Brief),
    SelectOption(label=f"Icebound Axe ({core.IceboundAxe.cost}g)", value='4', description=core.IceboundAxe.Brief),
    SelectOption(label=f"Noble's Tome ({core.NoblesTome.cost}g)", value='5', description=core.NoblesTome.Brief),
    SelectOption(label=f"Sharpened Katana ({core.SharpenedKatana.cost}g)", value='6', description=core.SharpenedKatana.Brief),
]

def shadow_item(click: int, user: discord.User | discord.Member, view: 'Shop'):
    match click:
        case 1:
            view.player = core.Rogue(user)
            weapon = core.CursedBlade
        case 2:
            view.player = core.Shaman(user)
            weapon = core.DimensionalSphere
        case 3:
            view.player = core.Wizard(user)
            weapon = core.DreadfulSpellBook
        case 4:
            view.player = core.Swordsman(user)
            weapon = core.RagingSword
        case 5:
            view.player = core.Archer(user)
            weapon = core.ReaperBow
        case 6:
            view.player = core.Necromancer(user)
            weapon = core.CorruptedRod
        case 7:
            view.player = core.Assassin(user)
            weapon = core.ShadowsDagger

    view.player.team = core.ETeam.Shadow # Player is a new class now
    view.player.EquipWeapon(weapon) # type: ignore

def noble_item(click: int, user: discord.User | discord.Member, view: 'Shop'):
    match click:
        case 1:
            view.player = core.Lancer(user)
            weapon = core.CoreSpear
        case 2:
            view.player = core.Archer(user)
            weapon = core.ElementalBow
        case 3:
            view.player = core.Archer(user)
            weapon = core.EnlightenedBow
        case 4:
            view.player = core.Fighter(user)
            weapon = core.IceboundAxe
        case 5:
            view.player = core.Magician(user)
            weapon = core.NoblesTome
        case 6:
            view.player = core.Samurai(user)
            weapon = core.SharpenedKatana

    view.player.team = core.ETeam.Noble
    view.player.EquipWeapon(weapon) # type: ignore

class ShadowItems(discord.ui.Select["Shop"]):
    def __init__(self):
        super().__init__(placeholder='Buy an Item', options=SHADOW_ITEMS)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        click = int(interaction.data['values'][0]) # type: ignore
        shadow_item(click, interaction.user, self.view)
        print(f'{self.view.player.name} has picked {self.view.player.Weapon.Name}.')
        await interaction.response.edit_message(content='Waiting for other players...', embed=None, view=None)
        self.view.stop() # type: ignore

class NobleItems(discord.ui.Select["Shop"]):
    def __init__(self):
        super().__init__(placeholder='Buy an Item', options=NOBLE_ITEMS)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        click = int(interaction.data['values'][0]) # type: ignore
        noble_item(click, interaction.user, self.view)
        print(f'{self.view.player.name} has picked {self.view.player.Weapon.Name}.')
        await interaction.response.edit_message(content='Waiting for other players...', embed=None, view=None)
        self.view.stop()

class Shop(discord.ui.View):
    """The unique Shop of every player.
    
    Parameters
    ---
    player :class:`Player`
        Player instance.
    """
    
    def __init__(self, player: core.Player):
        super().__init__()
        self.player = player
        self.embed = discord.Embed(
            title="Buy an Item",
            description='Increased Power means Increased Strength and Increased Intelligence',
            color=player.color
            )
        self.message: discord.Message = None # type: ignore
        match player.team:
            case core.ETeam.Shadow:
                self.embed.set_image(url='https://i.pinimg.com/236x/23/0a/18/230a18bbbf15c45a565bf257edb15e6d.jpg')
                sel = ShadowItems()
            case core.ETeam.Noble:
                self.embed.set_image(url='https://i.pinimg.com/236x/b0/c7/26/b0c72658f75353aecbd210658c202a3c.jpg')
                sel = NobleItems()

        self.add_item(sel)