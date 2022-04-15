import discord
import game
from discord import SelectOption


__all__ = (
    'shadow_item',
    'noble_item',
    'SHADOW_ITEMS',
    'NOBLE_ITEMS',
    'Shop'
)


SHADOW_ITEMS = [
    SelectOption(label=f"Corrupted Rod ({game.CorruptedRod.cost}g)", value='6', description=game.CorruptedRod.Brief),
    SelectOption(label=f"Cursed Blade ({game.CursedBlade.cost}g)", value='1', description=game.CursedBlade.Brief),
    SelectOption(label=f"Dimensional Sphere ({game.DimensionalSphere.cost}g)", value='2', description=game.DimensionalSphere.Brief),
    SelectOption(label=f"Dreadful Spell Book {game.DreadfulSpellBook.cost}g", value='3', description=game.DreadfulSpellBook.Brief),
    SelectOption(label=f"Raging Sword ({game.RagingSword.cost}g)", value='4', description=game.RagingSword.Brief),
    SelectOption(label=f"Reaper Bow ({game.ReaperBow.cost}g)", value='5', description=game.ReaperBow.Brief),
    SelectOption(label=f"Shadow's Dagger ({game.ShadowsDagger.cost}g)", value='7', description=game.ShadowsDagger.Brief)
]

NOBLE_ITEMS = [
    SelectOption(label=f"Core Spear ({game.CoreSpear.cost}g)", value='1', description=game.CoreSpear.Brief),
    SelectOption(label=f"Elemental Bow ({game.ElementalBow.cost}g)", value='2', description=game.ElementalBow.Brief),
    SelectOption(label=f"Enlightened Bow ({game.EnlightenedBow.cost}g)", value='3', description=game.EnlightenedBow.Brief),
    SelectOption(label=f"Icebound Axe ({game.IceboundAxe.cost}g)", value='4', description=game.IceboundAxe.Brief),
    SelectOption(label=f"Noble's Tome ({game.NoblesTome.cost}g)", value='5', description=game.NoblesTome.Brief),
    SelectOption(label=f"Sharpened Katana ({game.SharpenedKatana.cost}g)", value='6', description=game.SharpenedKatana.Brief),
]

def shadow_item(click: int, user: discord.User | discord.Member, view: 'Shop'):
    match click:
        case 1:
            view.player = game.Rogue(user)
            weapon = game.CursedBlade
        case 2:
            view.player = game.Shaman(user)
            weapon = game.DimensionalSphere
        case 3:
            view.player = game.Wizard(user)
            weapon = game.DreadfulSpellBook
        case 4:
            view.player = game.Swordsman(user)
            weapon = game.RagingSword
        case 5:
            view.player = game.Archer(user)
            weapon = game.ReaperBow
        case 6:
            view.player = game.Necromancer(user)
            weapon = game.CorruptedRod
        case 7:
            view.player = game.Assassin(user)
            weapon = game.ShadowsDagger

    view.player.team = game.ETeam.Shadow # Player is a new class now
    view.player.EquipWeapon(weapon) # type: ignore

def noble_item(click: int, user: discord.User | discord.Member, view: 'Shop'):
    match click:
        case 1:
            view.player = game.Lancer(user)
            weapon = game.CoreSpear
        case 2:
            view.player = game.Archer(user)
            weapon = game.ElementalBow
        case 3:
            view.player = game.Archer(user)
            weapon = game.EnlightenedBow
        case 4:
            view.player = game.Fighter(user)
            weapon = game.IceboundAxe
        case 5:
            view.player = game.Magician(user)
            weapon = game.NoblesTome
        case 6:
            view.player = game.Samurai(user)
            weapon = game.SharpenedKatana

    view.player.team = game.ETeam.Noble
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
    
    def __init__(self, player: game.Player):
        super().__init__()
        self.player = player
        if not player.bot:
            self.content = None
            self.embed = discord.Embed(
                title="Buy an Item",
                description='Increased Power means Increased Strength and Increased Intelligence',
                color=player.color
                )
            self.message: discord.Message = None # type: ignore
            match player.team:
                case game.ETeam.Shadow:
                    self.embed.set_image(url='https://i.pinimg.com/236x/23/0a/18/230a18bbbf15c45a565bf257edb15e6d.jpg')
                    sel = ShadowItems()
                case game.ETeam.Noble:
                    self.embed.set_image(url='https://i.pinimg.com/236x/b0/c7/26/b0c72658f75353aecbd210658c202a3c.jpg')
                    sel = NobleItems()

            self.add_item(sel)
        
        else:
            # The only bot player should be Cortana
            self.embed = None
            match player.team:
                case game.ETeam.Shadow:
                    self.content = f"Scegli tra {' '.join(opt.label for opt in SHADOW_ITEMS)}"
                case game.ETeam.Noble:
                    self.content = f"Scegli tra {' '.join(opt.label for opt in NOBLE_ITEMS)}"
                