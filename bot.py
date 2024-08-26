import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
from typing import List, Dict

# Define constants
QUEUE_CHANNEL_ID = 1275349042750033940
VOICE_CHANNEL_LIMIT = 4
GAME_CHANNEL_NAME = "game-channel"
ELO_WIN = 35
ELO_LOSS = -5

# Global data structures
queue: List[discord.Member] = []
active_games: Dict[int, Dict[str, List[discord.Member]]] = {}  # Game ID -> {'team1': [], 'team2': []}
elo_ratings: Dict[int, int] = {}  # player_id -> elo_rating

class QueueButton(Button):
    def __init__(self):
        super().__init__(label="Join Queue", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user

        # Check if the member is in a voice channel
        if not member.voice or not member.voice.channel:
            await interaction.response.send_message("You need to be in a voice channel to join the queue.", ephemeral=True)
            return

        # Check if the member is already in the queue
        if member in queue:
            await interaction.response.send_message("You are already in the queue.", ephemeral=True)
            return

        # Add member to the queue
        queue.append(member)
        await interaction.response.send_message(f"{member.mention} has joined the queue.", ephemeral=True)

class StartGameButton(Button):
    def __init__(self):
        super().__init__(label="Start Game", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        if len(queue) < 8:   # u can change the number here
            await interaction.response.send_message("Not enough players in the queue.", ephemeral=True)
            return

        # Start the game
        await interaction.response.send_message("Starting the game...", ephemeral=True)
        await start_game()

async def start_game():
    guild = bot.get_guild(GUILD_ID)  # Replace with ur guild / ur discord server ID
    channel = bot.get_channel(QUEUE_CHANNEL_ID)
    global queue

    # Create voice channels
    voice_channels = [await guild.create_voice_channel(f"{GAME_CHANNEL_NAME}-{i}") for i in range(2)]
    game_channel = await guild.create_text_channel(GAME_CHANNEL_NAME)

    # Split the queue into two teams
    team1 = queue[:4]
    team2 = queue[4:]

    # Assign permissions
    for team in [team1, team2]:
        for member in team:
            for vc in voice_channels:
                await vc.set_permissions(member, connect=True, speak=True)
            await game_channel.set_permissions(member, send_messages=True)

    # Save game data
    game_id = len(active_games) + 1
    active_games[game_id] = {'team1': team1, 'team2': team2}

    # Inform players
    for team, members in [('Team 1', team1), ('Team 2', team2)]:
        member_mentions = ' '.join(member.mention for member in members)
        await game_channel.send(f"{team}: {member_mentions}")

    # Clean up queue
    queue = []

    # Create picking phase
    await picking_phase(game_channel)

async def picking_phase(game_channel: discord.TextChannel):
    # * picking phase
    # Choose captains, let them pick players, etc.
    # Place for picking phase
    await game_channel.send("Picking phase has started.")

@bot.command(name='queue')
async def queue_command(ctx):
    button = QueueButton()
    view = View()
    view.add_item(button)
    await ctx.send("Click the button to join the queue. You must be in a voice channel to do so.", view=view)

@bot.command(name='start_game')
@commands.has_role('Admin')  # Replace with appropriate role check
async def start_game_command(ctx):
    button = StartGameButton()
    view = View()
    view.add_item(button)
    await ctx.send("Click the button to start the game.", view=view)

@bot.command(name='score')
@commands.has_role('Admin')  # Replace with  role check
async def score(ctx, game_id: int):
    if game_id not in active_games:
        await ctx.send("Invalid game ID.")
        return

    # Ensure a file is attached
    if not ctx.message.attachments:
        await ctx.send("Please attach the score file.")
        return

    # Process the score
    file = ctx.message.attachments[0]
    # Here dis would process the score file and update Elo ratings
    # * for Elo calculation
    # Updatesssss the Elo ratings based on the game result

    # Lock game channel
    game_channel = discord.utils.get(ctx.guild.text_channels, name=GAME_CHANNEL_NAME)
    if game_channel:
        await game_channel.set_permissions(ctx.guild.default_role, send_messages=False)

    # Final process the game
    await finalize_game(game_id)

async def finalize_game(game_id: int):
    if game_id not in active_games:
        return

    game_data = active_games.pop(game_id)
    team1, team2 = game_data['team1'], game_data['team2']

    # Calculate Elo changes and notify teams
    # Placeholder for Elo calculation
    await bot.get_channel(QUEUE_CHANNEL_ID).send("Game finalized. Elo ratings updated.")

@bot.command(name='i')
async def info_command(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    elo = elo_ratings.get(member.id, 1000)  # Default Elo rating if not found
    await ctx.send(f"{member.mention} has an Elo rating of {elo}.")

bot.run('set ur discord token here')
