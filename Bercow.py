# Work with Python 3.6

import asyncio
from discord.ext import commands
import random
import argparse
import json
import aiofiles

#from methods import save


class NoExitParser(argparse.ArgumentParser):
	def error(self, message):
		raise ValueError(message)


owner_id = 345468527538339850
command_prefix = '?'

#with open('preferences.json', 'r') as file:
#	preferences = json.load(file)


try:
	# Open token file and read it into TOKEN
	with open('token.txt', mode='r') as txt:
		TOKEN = txt.read()

except FileNotFoundError:
	# If file does not exist, exit process
	print('Token file does not exist. Quitting process...')
	quit()




with open('discordcodeblock.txt') as f:
	code_block = f.read()


class BotClient(commands.Bot):
	def __init__(self, command_prefix, config):
		super().__init__(command_prefix = command_prefix)
		self.config_location = config
		with open(config,'r') as x:
			self.settings = json.load(x)
		if not owner_id in self.settings['admins']:
			self.settings['admins'].append(owner_id)
		self.current_votes = []
		print(json.dumps(self.settings, indent = 4, sort_keys = True))
	

	async def on_ready(self):
		print('Logged in as')
		print(self.user.name)
		print(self.user.id)
		print('------')


	async def on_message(self, message):
		if message.author.bot or message.channel.id in self.settings["no_bercow"]:
			return

		if await self.mr_speaker(message):
			return

		if await self.politics_chat(message):
			return
			
		await self.process_commands(message)
		
	
	
	async def mr_speaker(self, message):
		#Corrects member if they refer to Mr Speaker by name
		if ('bercow' in message.content or self.user in message.mentions) and command_prefix not in message.content:
			await message.channel.send('ORDER! The Honourable Member must refer to me as Mr Speaker at all times. I ask that they withdraw their comment.')
			return True
		return False
	
	async def politics_chat(self, message):
		#Identifies politics chat in wrong channels
		message_words = message.content.lower().split(' ')
		if not set(message_words).isdisjoint(set(self.settings['politics_triggers'])) and message.channel.id not in self.settings["politics_channels"]:
			bot_message = random.choice(self.response_options)
			await message.channel.send(bot_message)
			return True
		return False
		
	
	async def save_settings(self):
		#Saves the bot settings to an appropriate location
		async with aiofiles.open(self.config_location, "w+") as x:
			await x.write(json.dumps(self.settings, indent = 4, sort_keys = True))
	
	async def set_politics(self, channel_id):
		if channel_id not in self.settings['politics_channels']:
			self.settings['politics_channels'].append(channel_id)
			await self.save_settings()
			return 'I thank the Honourable Member for identifying this as the correct forum for political discussion'
		else:
			return 'I do hope that the Honourable Member is aware that the given channel has indeed already been identified as a channel of political discussion'
	
			
		

bot = BotClient(command_prefix, 'preferences.json')

@bot.command()
async def burn(ctx, arg=None):
	#No target
	if arg is None:
		bot_message = random.choice(bot.settings['burns']['no_target']).format(ctx)
	#if no mentions we need to identify target(s)
	elif not ctx.message.mentions:
		#lol george
		if arg.lower() == 'george':
			target = bot.get_user(478649485048676383)
			bot_message = random.choice(bot.settings['burns']['burns']).format(target)
		else:
			#count targets
			count = 0
			for x in ctx.channel.members:
				if arg in x.display_name.lower() or arg in x.name.lower():
					target = x
					count = count + 1
			if count == 0:
				bot_message = random.choice(bot.settings['burns']['no_target']).format(ctx)
			elif count == 1:
				bot_message = random.choice(bot.settings['burns']['burns']).format(target)
			else:
				bot_message = random.choice(bot.settings['burns']['multiple_targets']).format(ctx)
	else:
		if len(ctx.message.mentions)>1:
			bot_message = random.choice(bot.settings['burns']['multiple_targets']).format(ctx)
		else:
			bot_message = random.choice(bot.settings['burns']['burns']).format(ctx.message.mentions[0])
	await ctx.send(bot_message)


@bot.command()
async def setpolitics(ctx, arg=None):
	#Check authorisation
	if not ctx.message.author.id in bot.settings["admins"]:
		bot_message = 'I certainly won\'t take orders such as those from a junior minister! Hrumph!'
	else:
		try:
			#Identify channel and pass to bot.set_politics which will do the work and return a message
			if arg is None:
				cid = ctx.channel.id
			else:
				cid = int(arg)
			bot_message = await bot.set_politics(cid)

		except:
			# Broad exception because Bercow is lazy
			bot_message = 'If the honourable member had consulted Erskine May, chapter 6, before making their request, they would have avoided wasting this chamber\'s time by issuing an invalid ' \
							'request.\nI ask that they are more careful next time.'
	await ctx.send(bot_message)


@bot.command()
async def nobercow(ctx, arg=None):
	if not ctx.message.author.id in bot.settings["admins"]:
		bot_message = 'I certainly won\'t take orders such as those from a junior minister! Hrumph!'
		await ctx.channel.send(bot_message)
		return

	if arg is None:
		bot.settings["no_bercow"].append(ctx.channel.id)
		bot_message = 'I recognise that I am no longer welcome in this channel. \U0001f622'
		await ctx.send(bot_message)
		await bot.save_settings()
		return

	try:
		if int(arg) not in bot.settings["no_bercow"]:
			bot.settings["no_bercow"].append(int(arg))
			bot_message = 'As requested, I shall withdraw from the given channel indefinitely.'
			await ctx.send(bot_message)
			await bot.save_settings()
		else:
			bot_message = 'I do hope that the honourable member is aware that I am no longer present in the specified channel.'
			await ctx.send(bot_message)

	except:
		# Broad exception because Bercow is lazy
		bot_message = 'That is not how we do things in this house and the Honourable Member knows it. Please improve and resubmit your amendment.'
		await ctx.send(bot_message)


@bot.command()
async def setmusic(ctx, arg=None):
	if not ctx.message.author.id in bot.settings["admins"]:
		bot_message = 'I certainly won\'t take orders such as those from a junior minister! Hrumph!'
		await ctx.channel.send(bot_message)
		return

	if arg is None:
		if ctx.channel.id not in bot.settings["music_text"]:
			bot.settings["music_text"].append(ctx.channel.id)
			bot_message = 'I hereby give notice that the government has successfully passed a motion to designate this channel a music channel.'

			await bot.save_settings()
		else:
			bot_message = 'It is rather disappointing that the honourable member insists on providing information we already know. If they would stop that would be much appreciated.'
	else:
		try:
			if int(arg) not in bot.settings["music_text"]:
				bot.settings["music_text"].append(int(arg))
				channel_name = bot.get_channel(int(arg)).name

				await bot.save_settings
			else:
				bot_message = 'It is rather disappointing that the honourable member insists on providing information we already know. If they would stop that would be much appreciated.'
				await ctx.send(bot_message)

				return
		except:
			# Broad exception because Bercow is lazy
			bot_message = 'Unfortunately the Honourable Member has made an invalid request; I ask that they try again.'
		else:
			bot_message = 'I hereby give notice that the government has successfully passed a motion to designate ' + channel_name + ' a music channel.'

	await ctx.send(bot_message)


@bot.command()
async def setdj(ctx, arg=None):
	if ctx.message.author.id not in bot.settings["admins"]:
		bot_message = 'I certainly won\'t take orders such as those from a junior minister! Hrumph!'
		await ctx.channel.send(bot_message)
		return

	if arg is None:
		bot_message = 'I must kindly ask the Honourable Member to repeat their request but this time specifying a channel ID.'

		await ctx.send(bot_message)
		return
	else:
		try:
			if int(arg) not in bot.settings["music_voice"]:
				bot.settings["music_voice"].append(int(arg))
				channel_name = bot.get_channel(int(arg)).name

				await bot.save_settings
			else:
				bot_message = 'I tell the honourable member that I applaud their efforts, but I would remind them that this house does not need to hear a particular contribution ' \
							  'multiple times, and I think their colleagues would appreciate it if they kept that in mind.'
				await ctx.send(bot_message)

				return
		except:
			# Broad exception because Bercow is lazy
			bot_message = 'Unfortunately the Honourable Member has made an invalid request; I ask that they try again.'
		else:
			bot_message = 'I hereby give notice that the government has successfully passed a motion to designate ' + channel_name + ' a DJ channel.'

	await ctx.send(bot_message)


@bot.command()
async def vote(ctx, *args):
	if len(args) == 0:
		bot_message = 'I\'m sure the Honourable Member is well aware that we cannot hold a vote unless they specify a motion. Please, try again {0.mention}'.format(ctx.author)
		await ctx.send(bot_message)
		return

	value_required = ['-time']

	args_tb_parsed = [a for a in args if (a.startswith('-') or args[args.index(a) - 1] in value_required)]
	parser = argparse.ArgumentParser()
	parser.add_argument("-time", type=int)
	parser.add_argument("-unanimous", action="store_true")
	parsed_args = parser.parse_args(args_tb_parsed)

	if parsed_args.time is not None:
		time = parsed_args.time
	else:
		time = 30

	if parsed_args.unanimous:
		unanimous_str = 'This motion must be passed unanimously.'
	else:
		unanimous_str = ''

	emoji_tu = '\U0001f44d'
	emoji_td = '\U0001f44e'

	bot_message_a = 'The question is that'

	args = [a for a in args if not (a.startswith('-') or args[args.index(a) - 1] in value_required)]

	for a in args:
		bot_message_a = bot_message_a + ' ' + a

	bot_message_a = bot_message_a + '\nAs many as are of that opinion react ' + emoji_tu + '. On the contrary ' + emoji_td + '.'

	bot_message_b = ('DIVISION! CLEAR THE LOBBY. You have %d seconds to vote. ' + unanimous_str) % time

	poll_question = await ctx.channel.send(bot_message_a)
	await ctx.channel.send(bot_message_b)
	poll_id = poll_question.id
	bot.current_votes.append(poll_id)
	await poll_question.add_reaction(emoji_tu)
	await poll_question.add_reaction(emoji_td)

	await asyncio.sleep(time)
	try:
		final_poll = await ctx.channel.fetch_message(poll_id)
		poll_result = final_poll.reactions
		print(poll_result)

		ayes = 0
		noes = 0

		for result in poll_result:
			if result.emoji == emoji_tu:
				ayes = result.count - 1
			elif result.emoji == emoji_td:
				noes = result.count - 1
			else:
				bot_message = 'I see an honourable member has abstained from voting by providing an alternative response. I reassure them that this will go on the record, ' \
							  'although I\'m not sure what good it will do.'
				await ctx.send(bot_message)

		bot_message = 'The ayes to the right: %d. The noes to the left: %d' % (ayes, noes)
		await ctx.send(bot_message)

		if parsed_args.unanimous and not (ayes == 0 or noes == 0):
			bot_message = 'I notice that there is disagreement amoungst Honourable Members. So the unanimous motion has failed.'
			await ctx.send(bot_message)
			return

		if not ayes == noes:
			winner = {
				0: 'noes',
				1: 'ayes'
			}
			result_str = winner[ayes > noes]
			bot_message = 'So the %s have it. The %s have it. ' % (result_str, result_str)
			if parsed_args.unanimous:
				bot_message = bot_message + 'Thus this unanimous motion has passed successfully.'

			bot_message = bot_message + '\nUNLOCK!'
		else:
			if ayes == 0:
				bot_message = 'I see no-one has casted a vote. I would ask that in future, the honourable member refrains from proposing motions that even he is ambivalent about.'
			else:
				bot_message = 'It is parliamentary custom for the speaker not to create a majority where one would otherwise not exist. So I cast my vote with the noes. The noes have it.\nUNLOCK!'

		await ctx.send(bot_message)
	except Exception as e:
		print('Caught error: ' + repr(e))
		bot_message = 'I am afraid there has been a counting issue and we must hold the vote again at a later date.'

		await ctx.send(bot_message)


@bot.command()
async def source(ctx):
	if ctx.message.author.id not in bot.settings["admins"]:
		bot_message = 'I certainly won\'t take orders such as those from a junior minister! Hrumph!'
		await ctx.channel.send(bot_message)
		return

	with open('main.py') as f:
		source_code = f.readlines()

	msg = code_block + 'python\n'
	for x in source_code:
		if len(msg) + len(x) + 5 >= 2000:
			msg = msg + code_block
			await ctx.send(msg)
			# print('Print: ' + msg)
			msg = code_block + 'python\n'
		else:
			msg = msg + x

	await ctx.message.channel.send(msg + "\n" + code_block)




bot.run(TOKEN)