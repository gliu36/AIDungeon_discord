import discord
from discord.ext import commands

import random
import sys

from AIDungeon.generator.gpt2.gpt2_generator import *
from AIDungeon.story import grammars
from AIDungeon.story.story_manager import *
from AIDungeon.story.utils import *

class AI(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('AI Script loaded')

    
    async def get_num(self, ctx, channel, n):
        def check(m):
            return m.channel == channel and ((m.content) in [str(i) for i in range(n)])
        msg = await ctx.bot.wait_for('message', check=check)
        return int(msg.content)

    async def get_text(self, ctx, channel):
        def check(m):
            return m.channel == channel
        msg = await ctx.bot.wait_for('message', check=check)
        return msg.content

    async def channel_say(self, channel, msg):
        return await channel.send(f"```{msg}```")

    async def lock_channel(self, ctx, channel, lock):
        perms = discord.PermissionOverwrite()
        perms.send_messages = not lock
        await channel.set_permissions(ctx.author, overwrite=perms)

    async def select_game(self, ctx, channel):
        with open(YAML_FILE, "r") as stream:
            data = yaml.safe_load(stream)

        # Random story?
        await self.channel_say(channel, "Random Story?\n\n0) yes\n1) no")
        msg = await self.get_num(ctx, channel, 2)

        if msg == 0:
            return self.random_story(data)

        # User-selected story...
        settings = data["settings"].keys()
        print_str = 'Pick a setting.\n\n'
        for i, setting in enumerate(settings):
            print_str += str(i) + ") " + setting
            if setting == "fantasy":
                print_str += " (recommended)"
            print_str += '\n'
        await channel.send(f"```{print_str}{str(len(settings))}) custom```")
        choice = await self.get_num(ctx, channel, len(settings) + 1)

        if choice == len(settings):
            return "custom", None, None, None, None

        setting_key = list(settings)[choice]

        characters = data["settings"][setting_key]["characters"]
        print_str = ''
        for i, character in enumerate(characters):
            print_str += (str(i) + ") " + character) + '\n'
        await channel.send(f"```Pick a character.\n\n{print_str}```")
        character_key = list(characters)[await self.get_num(ctx, channel, len(characters))]
        
        await self.channel_say(channel, "What is your name?")
        name = await self.get_text(ctx, channel)

        setting_description = data["settings"][setting_key]["description"]
        character = data["settings"][setting_key]["characters"][character_key]

        return setting_key, character_key, name, character, setting_description


    def random_story(self, story_data):
        # random setting
        settings = story_data["settings"].keys()
        n_settings = len(settings)
        n_settings = 2
        rand_n = random.randint(0, n_settings - 1)
        for i, setting in enumerate(settings):
            if i == rand_n:
                setting_key = setting

        # random character
        characters = story_data["settings"][setting_key]["characters"]
        n_characters = len(characters)
        rand_n = random.randint(0, n_characters - 1)
        for i, character in enumerate(characters):
            if i == rand_n:
                character_key = character

        # random name
        name = grammars.direct(setting_key, "character_name")

        return setting_key, character_key, name, None, None

    async def get_custom_prompt(self, ctx, channel):
        context = ""
        await channel.send("```Enter a prompt that describes who you are and the first couple sentences of where you start "
            "out ex:\n 'You are a knight in the kingdom of Larion. You are hunting the evil dragon who has been "
            + "terrorizing the kingdom. You enter the forest searching for the dragon and see' ```")

        await channel.send("Starting Prompt: ")

        prompt = await self.get_text(ctx, channel)

        return context, prompt

    async def get_curated_exposition(self, setting_key, character_key, name, character, setting_description):
        name_token = "<NAME>"
        try:
            context = grammars.generate(setting_key, character_key, "context") + "\n\n"
            context = context.replace(name_token, name)
            prompt = grammars.generate(setting_key, character_key, "prompt")
            prompt = prompt.replace(name_token, name)
        except:
            context = (
                "You are "
                + name
                + ", a "
                + character_key
                + " "
                + setting_description
                + "You have a "
                + character["item1"]
                + " and a "
                + character["item2"]
                + ". "
            )
            prompt_num = np.random.randint(0, len(character["prompts"]))
            prompt = character["prompts"][prompt_num]

        return context, prompt

    async def instructions(self):
        text = "\nAI Dungeon 2 Instructions:"
        text += '\n Enter actions starting with a verb ex. "go to the tavern" or "attack the orc."'
        text += '\n To speak enter \'say "(thing you want to say)"\' or just "(thing you want to say)" '
        text += "\n\nThe following commands can be entered for any action: "
        text += '\n  "/revert"   Reverts the last action allowing you to pick a different action.'
        text += '\n  "/quit"     Quits the game and saves'
        text += '\n  "/reset"    Starts a new game and saves your current one'
        text += '\n  "/restart"  Starts the game from beginning with same settings'
        text += '\n  "/save"     Makes a new save of your game and gives you the save ID'
        text += '\n  "/load"     Asks for a save ID and loads the game if the ID is valid'
        text += '\n  "/print"    Prints a transcript of your adventure (without extra newline formatting)'
        text += '\n  "/help"     Prints these instructions again'
        text += '\n  "/censor off/on" to turn censoring off or on.'
        return text


    @commands.is_owner()
    async def play_dungeon(self, ctx, channel):
        await self.lock_channel(ctx, channel, True)
        await channel.send("```Initializing AI Dungeon! (This might take a few minutes)```")
        generator = GPT2Generator()
        story_manager = UnconstrainedStoryManager(generator)

        with open(r"AIDungeon/opening.txt", "r", encoding="utf-8") as f:
            starter = f.read()
        await channel.send(f"```{starter}```")

        upload_story = False

        await self.lock_channel(ctx, channel, True)
        while True:
            if story_manager.story != None:
                story_manager.story = None

            while story_manager.story is None:

                await channel.send("```0) New Game\n\n1) Load Game```")
                msg = await self.get_num(ctx, channel, 2)

                if msg == 0: # New Game
                    (
                        setting_key,
                        character_key,
                        name,
                        character,
                        setting_description,
                    ) = await self.select_game(ctx, channel)

                    if setting_key == "custom":
                        context, prompt = await self.get_custom_prompt(ctx, channel)

                    else:
                        context, prompt = await self.get_curated_exposition(
                            setting_key, character_key, name, character, setting_description
                        )

                    await channel.send(f"```{await self.instructions()}```")
                    msg = await channel.send("```\n\n\nGenerating story...\n\n```")

                    result = story_manager.start_new_story(prompt, context=context, upload_story=upload_story)
                    await channel.send(f"```{result}\n\n Enter your action below:```")
                    await msg.delete()

                else: # Saved Game
                    await channel.send("```What is the ID of the saved game?```")
                    load_ID = await self.get_text(ctx, channel)
                    result = story_manager.load_new_story(load_ID, upload_story=upload_story)
                    await channel.send("\n\n\nLoading Game...\n\n")
                    await channel.send(f"```{result}\n\n>>Enter your action below:```")

            while True:
                await self.lock_channel(ctx, channel, False)
                thinking_msg = await channel.send("```Bot is thinking...```")
                action = await self.get_text(ctx, channel)
                await thinking_msg.delete()
                await self.lock_channel(ctx, channel, True)

                if len(action) > 0 and action[0] == "/":
                    split = action[1:].split(" ")  # removes preceding slash
                    command = split[0].lower()
                    args = split[1:]
                    if command == "reset":
                        story_manager.story.get_rating()
                        break

                    elif command == "restart":
                        story_manager.story.actions = []
                        story_manager.story.results = []
                        await self.channel_say(channel, f"Game restarted.\n {story_manager.story.story_start}")
                        continue

                    elif command == "quit":
                        # TO BE IMPLEMENTED
                        # story_manager.story.get_rating()
                        pass

                    elif command == "nosaving":
                        upload_story = False
                        story_manager.story.upload_story = False
                        await self.channel_say(channel, "Saving turned off.")

                    elif command == "help":
                        await self.channel_say(channel, await self.instructions())

                    elif command == "censor":
                        if len(args) == 0:
                            if generator.censor:
                                await self.channel_say(channel, "Censor is enabled.")
                            else:
                                await self.channel_say(channel, "Censor is disabled.")
                        elif args[0] == "off":
                            if not generator.censor:
                                await self.channel_say(channel, "Censor is already disabled.")
                            else:
                                generator.censor = False
                                await self.channel_say(channel, "Censor is now disabled.")

                        elif args[0] == "on":
                            if generator.censor:
                                await self.channel_say(channel, "Censor is already enabled.")
                            else:
                                generator.censor = True
                                await self.channel_say(channel, "Censor is now enabled.")

                        else:
                            await self.channel_say(channel, "Invalid argument: {}".format(args[0]))

                    elif command == "save":
                        if upload_story:
                            id = story_manager.story.save_to_storage()
                            await self.channel_say(channel, "Game saved.")
                            await self.channel_say(channel, "To load the game, type 'load' and enter the following ID: {}".format(id))
                        else:
                            await self.channel_say(channel, "Saving has been turned off. Cannot save.")

                    elif command == "load":
                        if len(args) == 0:
                            await self.channel_say(channel, "What is the ID of the saved game?")
                            load_ID = await self.get_text(ctx, channel)
                        else:
                            load_ID = args[0]
                        await self.channel_say(channel, "Loading Game...")
                        result = story_manager.story.load_from_storage(load_ID)
                        await self.channel_say(channel, result)

                    elif command == "print":
                        await self.channel_say(channel, str(story_manager.story))

                    elif command == "revert":
                        if len(story_manager.story.actions) == 0:
                            await self.channel_say(channel, "You can't go back any farther.")
                            continue

                        story_manager.story.actions = story_manager.story.actions[:-1]
                        story_manager.story.results = story_manager.story.results[:-1]
                        await self.channel_say(channel, "Last action reverted.")
                        if len(story_manager.story.results) > 0:
                            console_print(story_manager.story.results[-1])
                        else:
                            console_print(story_manager.story.story_start)
                        continue

                    else:
                        await self.channel_say(channel, "Unknown command: {}".format(command))

                else:
                    if action == "":
                        action = ""
                        result = story_manager.act(action)
                        await self.channel_say(channel, result)

                    elif action[0] == '"':
                        action = "You say " + action

                    else:
                        action = action.strip()

                        if "you" not in action[:6].lower() and "I" not in action[:6]:
                            action = action[0].lower() + action[1:]
                            action = "You " + action

                        if action[-1] not in [".", "?", "!"]:
                            action = action + "."

                        action = first_to_second_person(action)

                        action = "\n> " + action + "\n"

                    result = "\n" + story_manager.act(action)
                    if len(story_manager.story.results) >= 2:
                        similarity = get_similarity(
                            story_manager.story.results[-1], story_manager.story.results[-2]
                        )
                        if similarity > 0.9:
                            story_manager.story.actions = story_manager.story.actions[:-1]
                            story_manager.story.results = story_manager.story.results[:-1]
                            await self.channel_say(channel, "Woops that action caused the model to start looping. Try a different action to prevent that.")
                            continue

                    if player_won(result):
                        await self.channel_say(channel, "CONGRATS YOU WIN")
                        story_manager.story.get_rating()
                        break
                    elif player_died(result):
                        await self.channel_say(channel, result)
                        await self.channel_say(channel, "YOU DIED. GAME OVER\nOptions:\n0) Start a new game\n1) I'm not dead yet!... (If you didn't actually die)")
                        choice = self.get_num(ctx, channel, 2)
                        if choice == 0:
                            story_manager.story.get_rating()
                            break
                        else:
                            console_print("Sorry about that...where were we?")
                            await self.channel_say(channel, f"Sorry about that...where were we?\n\n {result}")

                    else:
                        await self.channel_say(channel, result)
        
        
        


def setup(bot):
    bot.add_cog(AI(bot))