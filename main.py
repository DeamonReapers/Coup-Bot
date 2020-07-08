import discord
from coup import *
from discord.ext import commands
from typing import Any, List, Optional, Tuple

client = commands.Bot(command_prefix='//')
# Is used to launch the bot, DO NOT SHARE IT
TOKEN = "Njg2Mzk1ODU0NjU5MTI1MzQ1.XmWoXA.mzQOJaPytBGPMmu8x77PREFViOQ"

# A game list for each discord server
# You are allowed one game per server
GAME_LIST = {}


@client.event
async def on_ready():
    # console message to confirm bot has logged in
    print('We have logged in as {0.user}'.format(client))


def command_list():
    """
    Returns an embed of all the commands
    """
    embed = discord.Embed()
    embed.add_field(name='Action', value="Command")
    embed.add_field(name='Income:', value="//income")
    embed.add_field(name='Foreign Aid:', value="//aid")
    embed.add_field(name='Tax:', value="//tax")
    embed.add_field(name='Coup:', value="//coup @user")
    embed.add_field(name='Assassinate:', value="//assassinate @user")
    embed.add_field(name='Steal:', value="//steal @user")
    embed.add_field(name='Exchange:', value="// exchange <index>")
    return embed


async def show_cards(player: Player):
    """
    Shows the players cards
    """
    await player.user.create_dm()
    await player.user.dm_channel.send("{}'s cards\n{} coins".format(player.name, player.coin))
    index = 0
    for card in player.cards:
        await player.user.dm_channel.send("{}. {}".format(index, card))
        await player.user.dm_channel.send(file=discord.File(f'{PATH}\{CARD_PICS[card]}'))
        index += 1


@client.command()
async def game(ctx, *players):
    """
    To add players to a game of coup, you must mention up to 1-5 users.
    The user who initializes it, is a player in the game
    Total of 2-6 players can play the game
    Any additional players are ignored
    """
    # Resets the players for each game
    if ctx.guild in GAME_LIST:
        await ctx.send("Game is in progress, wait until it finishes")
    else:
        if len(players) >= 2:
            GAME_LIST[ctx.guild] = Coup()
            GAME_LIST[ctx.guild].deck = generate_deck()
            await ctx.send("Now creating coup game with: ")
            for player in players[0:5]:
                # If the user does not have a nickname
                try:
                    user = ctx.guild.get_member(int(player[2:-1]))
                # If the user has a nickname
                except ValueError:
                    user = ctx.guild.get_member(int(player[3:-1]))
                await ctx.send(user.name)
                play = Player(user)
                play.cards = GAME_LIST[ctx.guild].deck.pop2()
                await show_cards(play)
                GAME_LIST[ctx.guild].players.append(play)

            # Chooses the first player in the list, thus the person who created the match
            GAME_LIST[ctx.guild].current_player = GAME_LIST[ctx.guild].players[0]
            await ctx.send("It is {} turn".format(GAME_LIST[ctx.guild].current_player.name))
            await ctx.send(embed=command_list())

        else:
            await ctx.send("Not enough players")


@client.command()
async def income(ctx) -> None:
    """
    Player takes 1 coin
    """
    if ctx.guild in GAME_LIST and ctx.author == GAME_LIST[ctx.guild].current_player.user and not GAME_LIST[ctx.guild].must_coup:
        await ctx.send(GAME_LIST[ctx.guild].income())
        await ctx.send(GAME_LIST[ctx.guild].GAME_LIST[ctx.guild].next_player())

    else:
        if GAME_LIST[ctx.guild].must_coup:
            await ctx.send("MUST COUP")
        else:
            await ctx.send("Oi, wait your turn")


@client.command()
async def aid(ctx) -> None:
    """
    Player takes 2 coins, can be blocked with a duke
    """
    if ctx.guild in GAME_LIST and ctx.author == GAME_LIST[ctx.guild].current_player.user and not GAME_LIST[ctx.guild].must_coup:
        GAME_LIST[ctx.guild].current_action = "aid"
        await ctx.send(GAME_LIST[ctx.guild].player_check())
    else:
        if GAME_LIST[ctx.guild].must_coup:
            await ctx.send("MUST COUP")
        else:
            await ctx.send("Oi, wait your turn")


@client.command()
async def tax(ctx) -> None:
    """
    Player takes 3 coins, is used by the duke
    """
    if ctx.guild in GAME_LIST and ctx.author == GAME_LIST[ctx.guild].current_player.user and not GAME_LIST[ctx.guild].must_coup:
        GAME_LIST[ctx.guild].current_action = "duke"
        await ctx.send(GAME_LIST[ctx.guild].player_check())
    else:
        if GAME_LIST[ctx.guild].must_coup:
            await ctx.send("MUST COUP")
        else:
            await ctx.send("Oi, wait your turn")


@client.command()
async def coup(ctx, player: str) -> None:
    """
    Player uses 7 coins, to immediately take away a players influence
    """
    if ctx.guild in GAME_LIST and ctx.author == GAME_LIST[ctx.guild].current_player.user and not GAME_LIST[ctx.guild].must_coup:
        if GAME_LIST[ctx.guild].current_player.coin >= 7 or GAME_LIST[ctx.guild].must_coup:
            GAME_LIST[ctx.guild].must_coup = False
            GAME_LIST[ctx.guild].current_player.coin -= 7
            challenger = GAME_LIST[ctx.guild].GAME_LIST[ctx.guild].find_player(player)
            if challenger is not None:
                await ctx.send(challenger)
                return
            print(GAME_LIST[ctx.guild].current_player.id)
            GAME_LIST[ctx.guild].challenger_index = challenger[1]
            if len(GAME_LIST[ctx.guild].challenger.cards) == 1:
                await ctx.send("{} discarded {} and is out of the game".format(GAME_LIST[ctx.guild].challenger.name,
                                                                               GAME_LIST[ctx.guild].challenger.cards.pop(0)))
                GAME_LIST[ctx.guild].GAME_LIST[ctx.guild].lose()
                await ctx.send(GAME_LIST[ctx.guild].GAME_LIST[ctx.guild].next_player())
            else:
                GAME_LIST[ctx.guild].current_action = "coup"
                await ctx.send("{} use //discard <index> to discard one of your cards"
                               .format(GAME_LIST[ctx.guild].challenger.name))
        else:
            await ctx.send("You require more coin")
    else:
        await ctx.send("It may be the name of the game, but it doesn't mean you can be the game")


@client.command()
async def assassinate(ctx, player: str) -> None:
    """
    Player uses 3 coins, to immediately take away a players influence
    """
    if ctx.guild in GAME_LIST and ctx.author == GAME_LIST[ctx.guild].current_player.user and not GAME_LIST[ctx.guild].must_coup:
        if GAME_LIST[ctx.guild].current_player.user.coin >= 3:
            GAME_LIST[ctx.guild].current_action = "assassin"
            GAME_LIST[ctx.guild].current_player.coin -= 3
            challenger = GAME_LIST[ctx.guild].find_player(player)
            if challenger is None:
                await ctx.send("Oi you dont exist")
                return
            await ctx.send("{} do you believe in lies, then use //bluff or //block. Otherwise //allow"
                           .format(challenger[0]))
        else:
            await ctx.send("You require more coin")
    else:
        await ctx.send(".......................................................")


@client.command()
async def steal(ctx, player: str) -> None:
    """
    Player steals 2 coins from another player, uses captain
    """
    if ctx.guild in GAME_LIST and ctx.author == GAME_LIST[ctx.guild].current_player.user and not GAME_LIST[ctx.guild].must_coup:
        GAME_LIST[ctx.guild].current_action = "captain"
        challenger = GAME_LIST[ctx.guild].find_player(player)
        if challenger is None:
            await ctx.send("Oi you dont exist")
            return
        await ctx.send("{} do you allow this fool to steal your hard earn cash, then use //bluff or "
                       "//block. Otherwise //allow".format(challenger[0]))
        await ctx.send(GAME_LIST[ctx.guild].player_check())
    else:
        if GAME_LIST[ctx.guild].must_coup:
            await ctx.send("MUST COUP")
        await ctx.send("Patience is not your strong suit is it")


@client.command()
async def exchange(ctx) -> None:
    """
    Player wants to exchange one of their cards
    """
    if ctx.guild in GAME_LIST and ctx.author == GAME_LIST[ctx.guild].current_player.user and not GAME_LIST[ctx.guild].must_coup:
        GAME_LIST[ctx.guild].current_action = "ambassador"
        await ctx.send(GAME_LIST[ctx.guild].player_check())
    else:
        if GAME_LIST[ctx.guild].must_coup:
            await ctx.send("MUST COUP")
        await ctx.send("Patience is not your strong suit is it")

    # GAME_LIST[ctx.guild].exchange_cards[0] = index
    # GAME_LIST[ctx.guild].exchange_cards[1] = GAME_LIST[ctx.guild].deck.pop2()
    # await GAME_LIST[ctx.guild].current_player.user.create_dm()
    # index = 0
    # for card in GAME_LIST[ctx.guild].exchange_cards[1]:
    #     await GAME_LIST[ctx.guild].current_player.user.dm_channel.send("{}. {}".format(index, card))
    #     await GAME_LIST[ctx.guild].current_player.user.dm_channel.send(file=discord.File(f'{PATH}\{CARD_PICS[card]}'))
    #     index += 1


@client.command()
async def allow(ctx):
    """
    Player allows the current player to commit an action
    """
    if ctx.guild in GAME_LIST and ctx.author == GAME_LIST[ctx.guild].current_player.user and not GAME_LIST[ctx.guild].must_coup:
        # If the Current player allows the block or an attack is occur to a player by a captain or assassin
        if GAME_LIST[ctx.guild].current_action in ["assassin", "captain"] and ctx.author == GAME_LIST[ctx.guild].challenger.user:
            await ctx.send(GAME_LIST[ctx.guild].action())
        # If a block is initiated, go to the next player
        elif GAME_LIST[ctx.guild].block and ctx.author == GAME_LIST[ctx.guild].current_player.user:
            GAME_LIST[ctx.guild].challenger_index = 0
            await ctx.send(GAME_LIST[ctx.guild].next_player())
            await ctx.send(embed=command_list())

        # If the player allows it iterates to the next player
        else:
            if ctx.author == GAME_LIST[ctx.guild].challenger.user:
                # If the next player is the current increment by one
                if GAME_LIST[ctx.guild].challenger.user == GAME_LIST[ctx.guild].current_player.user:
                    GAME_LIST[ctx.guild].challenger_index += 1
                GAME_LIST[ctx.guild].challenger_index += 1
            else:
                await ctx.send("Wait ya turn")

            # Once all the players are asked, the current player action will go through
            if len(GAME_LIST[ctx.guild].players) <= GAME_LIST[ctx.guild].challenger_index:
                await ctx.send(GAME_LIST[ctx.guild].action())
                if GAME_LIST[ctx.guild].current_action in ["aid", "duke", "assassin"]:
                    await ctx.send(GAME_LIST[ctx.guild].next_player())
                    await ctx.send(embed=command_list())
            else:
                await ctx.send(GAME_LIST[ctx.guild].player_check())
    else:
        await ctx.send("MUST COUP")


@client.command()
async def bluff(ctx):
    """
    PLayer believes that the current player is lying about having an influence
    Thus the current player must show what card they have
    If they do have it, the player who called the bluff must discard one of their cards
    Otherwise, the current player does not have it, therefore must discard it
    """
    # If a block is initiated, the current player does not believe that the challenger does not have the influence
    if ctx.guild in GAME_LIST and GAME_LIST[ctx.guild].block and ctx.author == GAME_LIST[ctx.guild].current_player.user:
        await ctx.send("{} you must show your cards using //show_card!".format(GAME_LIST[ctx.guild].challenger.name))
    elif ctx.author == GAME_LIST[ctx.guild].challenger.user:
        await ctx.send("{} you must show your cards using //show_card!".format(GAME_LIST[ctx.guild].current_player.name))
    else:
        await ctx.send("Wait ya turn")


@client.command()
async def block(ctx):
    """
    PLayer believes that the current player is lying about having an influence
    Thus the current player must show what card they have
    If they do have it, the player who called the bluff must discard one of their cards
    Otherwise, the current player does not have it, therefore must discard it
    """

    if ctx.guild in GAME_LIST and GAME_LIST[ctx.guild].current_action in ["duke", "aid", "ambassador"]:
        await ctx.send("Come on silly you can't block that!")
    else:
        if ctx.author == GAME_LIST[ctx.guild].challenger.user:
            await ctx.send("{} do you believe in the heart of the cards, that {} is lying!"
                           "\nThen use //bluff\nOtherwise use //allow"
                           .format(GAME_LIST[ctx.guild].current_player.name, GAME_LIST[ctx.guild].challenger.name))
            GAME_LIST[ctx.guild].block = True

        else:
            await ctx.send("Wait ya turn")


@client.command()
async def show_card(ctx, index: int):
    """
    PLayer must show one of their cards, if that card is the same as GAME_LIST[ctx.guild].current_action
    the other player must discard one of their cards
    """
    flag = False
    # If the challenger believes that the current player is lying
    if ctx.author == GAME_LIST[ctx.guild].challenger.user:
        challenger = GAME_LIST[ctx.guild].challenger
        actionman = GAME_LIST[ctx.guild].current_player
        flag = True
    # If the current player believes that the challenger is lying
    elif ctx.author == GAME_LIST[ctx.guild].current_player.user:
        challenger = GAME_LIST[ctx.guild].current_player
        actionman = GAME_LIST[ctx.guild].challenger
        flag = True
    else:
        await ctx.send("Do you want everyone to know your cards?")

    # If a block was used to initialize this state, set block to false
    if GAME_LIST[ctx.guild].block:
        GAME_LIST[ctx.guild].block = False
    # Only happens if a player is legitimately showing a card
    if flag:
        card = challenger.cards[index]
        await ctx.send(file=discord.File(f'{PATH}\{CARD_PICS[card]}'))
        # If the challenger correctly has the card, actionman must lose one
        if card == GAME_LIST[ctx.guild].current_action:
            print(False)
            GAME_LIST[ctx.guild].swap[0] = index
            GAME_LIST[ctx.guild].swap[1] = challenger
            if len(actionman.cards) == 1:
                discarded_card = actionman.cards.pop(0)
                await ctx.send("{} discarded {} and is out of the game".format(actionman.name,
                                                                               discarded_card))
                GAME_LIST[ctx.guild].GAME_LIST[ctx.guild].lose()
                await ctx.send(GAME_LIST[ctx.guild].next_player())
            else:
                await ctx.send("{} discard a card!\n Use //discard index".format(actionman.name))
            await show_cards(actionman)
            await ctx.send("{} use //swap if you wish to swap out the card you just showed\nOtherwise do nothing"
                           .format(challenger.name))

        # Otherwise challenger loses said card
        else:
            print(True)
            discarded_card = challenger.cards.pop(0)
            # If the player has no cards left
            if len(challenger.cards) == 0:
                await ctx.send(
                    "{} discarded {} and is out of the game".format(challenger.name, discarded_card))
                GAME_LIST[ctx.guild].lose()
            else:
                await ctx.send("{} discarded {}".format(challenger.name, discarded_card))
                await show_cards(challenger)

            # If ambassador was used, put the cards from the top of the deck
            if GAME_LIST[ctx.guild].current_action == "ambassador":
                for index in range(0, 2):
                    GAME_LIST[ctx.guild].deck.push_bottom(GAME_LIST[ctx.guild].exchange_cards[1].pop(0))

            if len(GAME_LIST[ctx.guild].players) > 1:
                await ctx.send(GAME_LIST[ctx.guild].action())
            await ctx.send(GAME_LIST[ctx.guild].next_player())
            await ctx.send(embed=command_list())


@client.command()
async def discard(ctx, index: int):
    """
    If current player used a coup or an assassin, the challenger must discard one of their cards
    """
    if ctx.guild in GAME_LIST and ctx.author == GAME_LIST[ctx.guild].challenger.user:
        if 0 <= index < len(GAME_LIST[ctx.guild].challenger.cards):
            discarded_card = GAME_LIST[ctx.guild].challenger.cards.pop(index)
            await ctx.send("{} discarded {}".format(GAME_LIST[ctx.guild].challenger.name, discarded_card))
            await ctx.send(GAME_LIST[ctx.guild].next_player())
            await ctx.send(embed=command_list())

        else:
            await ctx.send("Invalid index, try again")
    else:
        await ctx.send("DO YOU WANT TO DISCARD!!!!!!")


@client.command()
async def choice(ctx, index: int):
    """
    After seeing what the top 2 cards are, the player can choose which one they want to exchange
    """
    if ctx.guild in GAME_LIST and ctx.author == GAME_LIST[ctx.guild].challenger.user:
        if 0 <= index < 2:
            # Makes a list for the cards that must be put at the bottom of the deck
            GAME_LIST[ctx.guild].deck.push_bottom(GAME_LIST[ctx.guild].current_player.cards.pop(GAME_LIST[ctx.guild].exchange_cards[0]))
            GAME_LIST[ctx.guild].current_player.cards.append(GAME_LIST[ctx.guild].exchange_cards[1].pop(index))
            GAME_LIST[ctx.guild].deck.push_bottom(GAME_LIST[ctx.guild].exchange_cards[1].pop)
            await show_cards(GAME_LIST[ctx.guild].current_player)
            await ctx.send(GAME_LIST[ctx.guild].next_player())
            await ctx.send(embed=command_list())


@client.command()
async def swap(ctx, card_away: int = 0, card_want: int = 0):
    """
    If the current player is exchanging cards they must put in the card index they want to give away and the card index
    of the top 2 cards from the deck

    Otherwise, if an opponents bluff was incorrect they can swap the card that was shown for a card that is on top of the
    deck.
    """
    if ctx.guild in GAME_LIST and ctx.author == GAME_LIST[ctx.guild].swap[1].user:
        if GAME_LIST[ctx.guild].current_action == "ambassador":
            # Pushes the card that the current player wants to swap to the bottom of the deck
            GAME_LIST[ctx.guild].deck.push_bottom(GAME_LIST[ctx.guild].current_player.cards.pop(card_away))
            # Appends the card the current player wants to their cards list
            GAME_LIST[ctx.guild].current_player.cards.append(GAME_LIST[ctx.guild].exchange_cards.pop(card_want))
            # Pushes the last card in self.exchange_cards to the bottom
            GAME_LIST[ctx.guild].deck.push_bottom(GAME_LIST[ctx.guild].current_player.cards[card_away])
            await ctx.send(GAME_LIST[ctx.guild].GAME_LIST[ctx.guild].next_player())
        else:
            GAME_LIST[ctx.guild].deck.push_bottom(GAME_LIST[ctx.guild].swap[1].cards.pop(GAME_LIST[ctx.guild].swap[0]))
            GAME_LIST[ctx.guild].swap[1].cards.append(GAME_LIST[ctx.guild].deck.pop())
        await show_cards(swap[1])


@client.command()
async def end(ctx):
    """
    If the game ends up in a softlock, end the game
    """
    GAME_LIST.pop(ctx.guild)
    await ctx.send("GAME OVER")


# Launches the bot on discord
client.run(TOKEN)
