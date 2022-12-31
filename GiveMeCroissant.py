import time
import discord


class CroissantView(discord.ui.View):

    def __init__(self, croissanting):
        super().__init__()
        self.croissanting = croissanting

    @discord.ui.button(label="Prendre un croissant", style=discord.ButtonStyle.green)
    async def take_croissant(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.croissanting.eaters:
            await interaction.response.send_message("Vous avez déjà pris un croissant !", ephemeral=True)
            return
        if interaction.user.id == self.croissanting.ctx.author.id:
            await interaction.response.send_message("Vous ne pouvez pas prendre un croissant à vous même !", ephemeral=True)
            return
        if time.time() - self.croissanting.last_eating_time >= self.croissanting.croissant_guild.pick_delay:
            await interaction.response.send_message("Vous avez prit un croissant !", ephemeral=True)
            self.croissanting.eaters.append(interaction.user.id)
            self.croissanting.last_eating_time = time.time()
            return
        else:
            await interaction.response.send_message("Vous devez attendre encore un peu !", ephemeral=True)
            return

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.croissanting.ctx.author.id:
            await interaction.response.send_message("Vous avez stoppé la croissanting !", ephemeral=True)
            await self.croissanting.stop()
        else:
            await interaction.response.send_message("Vous n'êtes pas le croissanté !", ephemeral=True)


class Croissanting:

    def __init__(self, _croissant_guild, ctx):
        self.croissant_guild = _croissant_guild
        self.ctx = ctx
        self.croissanting_view = CroissantView(self)
        self.eaters = []
        self.last_eating_time = 0
        self.message = None  # PLACEHOLDER

    async def initialize(self):
        # Embed
        embed = discord.Embed(title="Quelqu'un a été croissanté !", color=0xf5ce42)
        embed.set_thumbnail(
            url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/325/croissant_1f950.png")
        embed.set_footer(text="Made with ❤️ by Hugo")
        field_name = f"On a faim !"
        field_value = f"Merci {self.ctx.author.mention} on pense fort à toi !" \
                      f"\n\nUn croissant pourra être prit chaque {round(self.croissant_guild.pick_delay / 60)}mn." \
                      f"\nCroisanté, appuie vite sur le bouton !" \

        embed.add_field(name=field_name, value=field_value)

        self.message = await self.ctx.channel.send(embed=embed, view=self.croissanting_view)
        await self.ctx.delete()

    async def stop(self):
        # Embed
        embed = discord.Embed(title="La croissantage est terminée !", color=0xf5ce42)
        embed.set_thumbnail(
            url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/325/croissant_1f950.png")
        embed.set_footer(text="Made with ❤️ by Hugo")
        field_name = f"On a faim !"
        field_value = f"Merci {self.ctx.author.mention} on pense fort à toi !"
        embed.add_field(name=field_name, value=field_value)

        field_name = "Mangeurs:"
        field_value = ""
        for eater in self.eaters:
            field_value += f"<@{eater}> "
        if field_value == "":
            field_value = "Personne n'a pris de croissants !"

        embed.add_field(name=field_name, value=field_value, inline=False)

        await self.message.edit(embed=embed, view=None)

        self.croissant_guild.croissantings.pop(self.ctx.author.id)

# Instanced for every guild
class CroissantGuild:
    def __init__(self, _bot, _guild_id, _channel_id, pick_delay):
        self.bot = _bot
        self.guild_id = _guild_id
        self.channel_id = _channel_id
        self.pick_delay = pick_delay  # In seconds, time between two croissant picking

        self.croissantings = {}  # Key: user_id, Value: Croissanting instance

    # Events
    async def on_message(self, message):
        # Check if message is in the right channel
        if message.channel.id == self.channel_id:
            # Initialise a new croissanting if there is none
            if message.author.id not in self.croissantings:
                croissanting = Croissanting(self, message)
                self.croissantings[message.author.id] = croissanting
                await croissanting.initialize()
            else:
                await message.delete()


class Client(discord.Client):
    def __init__(self, _token: str, _guilds: dict, constants: dict, *args, **kwargs):
        # Call discord.py Client constructor
        super().__init__(*args, **kwargs)

        self._guilds = _guilds  # Used to instanciate guilds in instanciate_guilds()
        self.croissant_guilds = {}  # Key: guild_id, Value: Guilds instance

        self.constants = constants

        self.run(_token)

    # Instanciate CroissantGuild for every guild
    async def instanciate_guilds(self):
        for guild in self.guilds:
            if guild.id in self._guilds:
                # Instanciate croissant guild object
                self.croissant_guilds[guild.id] = CroissantGuild(self, guild.id, self._guilds[guild.id],
                                                                 self.constants["pick_delay"])

    # Events & Commands
    async def on_ready(self):
        await self.instanciate_guilds()
        print("Bot ready")

    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild.id in self.croissant_guilds:
            await self.croissant_guilds[message.guild.id].on_message(message)


# --- CONSTANTS ---
token = "token"
test_token = "token"

guilds = {}  # Key: guild_id, Value: bot channel id
test_guilds = {}  # Key: guild_id, Value: bot channel id

pick_delay = 300  # In seconds, time between two croissant picking

# --- Wrapper initialisation ---
intents = discord.Intents.all()
client = Client(test_token, test_guilds, {"pick_delay": pick_delay}, intents=intents)
