# Work with Python 3.6
import asyncio
from discord.ext import commands
import random
import argparse
import json
#from methods import save


class NoExitParser(argparse.ArgumentParser):
	def error(self, message):
		raise ValueError(message)


owner_id = 169891281139531776
politics_triggers = ['brexit', 'politics', 'tories', 'tory', 'labour', 'corbyn', 'theresa may', 'referendum', 'election', 'parliament']
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
			settings_file = json.load(x)
		self.settings = {}
		self.settings['response_options'] = settings_file['response_options']
		self.settings['politics_triggers'] = settings_file['politics_triggers']
		self.settings['no_bercow'] = settings_file['no_bercow']
		self.settings['politics_channels'] = settings_file['politics_channels']
		print(json.dumps(self.settings, indent = 4, sort_keys = True))
	

	async def on_ready(self):
		print('Logged in as')
		print(self.user.name)
		print(self.user.id)
		print('------')
	

	async def on_message(self, message):
		if message.author.bot or message.channel.id in preferences["no_bercow"]:
			return

		if ('bercow' in message.content or self.user in message.mentions) and command_prefix not in message.content:
			await message.channel.send('ORDER! The Honourable Member must refer to me as Mr Speaker at all times. I ask that they withdraw their comment.')
			return

		message_words = message.content.lower().split(' ')
		if not set(message_words).isdisjoint(set(self.politics_triggers)) and message.channel.id not in preferences["politics_channels"]:
			bot_message = random.choice(self.response_options)
			await message.channel.send(bot_message)

		await self.process_commands(message)

bot = BotClient(command_prefix, 'preferences.json')

@bot.command()
async def burn(ctx, arg=None):
	if arg is None:
		msg = 'It should be readily apparent to honourable members that the burn command requires a target.  It\'s a point so blindingly obvious that only an extraordinarily clever and sophisticated ' \
			  'person could fail to grasp it, {0.author.mention}'.format(ctx)
		await ctx.send(msg)
		return

	arg = arg.lower()

	if arg == 'george':
		guerro = bot.get_user(478649485048676383)
		bot_message = 'Yes, {0.mention} is quite the fool'.format(guerro)
		await ctx.send(bot_message)
		return
	#     bot_message = 'Yes, '
	#     for g in preferences["georges"]:
	#         g_user = bot.get_user(g)
	#         if g_user in ctx.channel.members:
	#             bot_message = bot_message + '{0.mention}'.format(g_user) + ', '

		# bot_message = bot_message[::-1]
		# bot_message = bot_message.replace(',', '', 1)
		# bot_message = bot_message.replace(',', 'dna ', 1)
		# bot_message = bot_message[::-1]
		#
		# bot_message = bot_message + 'are quite the fools'
		#
		# await ctx.send(bot_message)
		# return

	count = 0

	if not ctx.message.mentions:
		for x in ctx.channel.members:
			if arg in x.display_name.lower() or arg in x.name.lower():
				target = x
				count = count + 1

		if count == 0:
			bot_message = 'It should be readily apparent to honourable members that the burn command requires a target.  It\'s a point so blindingly obvious that only an extraordinarily clever and sophisticated ' \
			  'person could fail to grasp it, {0.author.mention}'.format(ctx)
		elif count == 1:
			bot_message = 'Yes, {0.mention} is quite the fool'.format(target)
		else:
			bot_message = 'It is most unparliamentary to cast such wide aspersions on honourable members.  Please be more specific in who you wish to address.'

		await ctx.send(bot_message)
	else:
		for x in ctx.message.mentions:
			await ctx.message.channel.send('Yes, {0.mention} is quite the fool'.format(x))
			print('{0.mention} just got burned'.format(x))



@bot.command()
async def setpolitics(ctx, arg=None):
	if not ctx.message.author.id in preferences["admins"]:
		bot_message = 'I certainly won\'t take orders such as those from a junior minister! Hrumph!'
		await ctx.channel.send(bot_message)
		return

	if arg is None:
		if ctx.channel.id not in preferences["politics_channels"]:
			preferences["politics_channels"].append(ctx.channel.id)
			bot_message = 'I thank the Honourable Member for identifying this as the correct forum for political discussion.'
			await ctx.send(bot_message)
			save(preferences, 'preferences.json')
		else:
			bot_message = 'I do hope that the honourable member is aware that this channel has indeed already been marked as a forum for political debate.'
			await ctx.send(bot_message)
		return

	try:
		if int(arg) not in preferences["politics_channels"]:
			preferences["politics_channels"].append(int(arg))
			bot_message = 'I thank the Honourable Member for identifying the correct forum for political discussion.'
			await ctx.send(bot_message)
			save(preferences, 'preferences.json')
		else:
			bot_message = 'I do hope that the honourable member is aware that the given channel has indeed already been marked as a forum for political debate.'
			await ctx.send(bot_message)

	except:
		# Broad exception because Bercow is lazy
		bot_message_a = 'If the honourable member had consulted Erskine May, chapter 6, before making their request, they would have avoided wasting this chamber\'s time by issuing an invalid ' \
						'request.'
		bot_message_b = 'I ask that they are more careful next time.'
		await ctx.send(bot_message_a)
		await ctx.send(bot_message_b)


@bot.command()
async def nobercow(ctx, arg=None):
	if not ctx.message.author.id in preferences["admins"]:
		bot_message = 'I certainly won\'t take orders such as those from a junior minister! Hrumph!'
		await ctx.channel.send(bot_message)
		return

	if arg is None:
		preferences["no_bercow"].append(ctx.channel.id)
		bot_message = 'I recognise that I am no longer welcome in this channel. \U0001f622'
		await ctx.send(bot_message)
		save(preferences, 'preferences.json')
		return

	try:
		if int(arg) not in preferences["no_bercow"]:
			preferences["no_bercow"].append(int(arg))
			bot_message = 'As requested, I shall withdraw from the given channel indefinitely.'
			await ctx.send(bot_message)
			save(preferences, 'preferences.json')
		else:
			bot_message = 'I do hope that the honourable member is aware that I am no longer present in the specified channel.'
			await ctx.send(bot_message)

	except:
		# Broad exception because Bercow is lazy
		bot_message = 'That is not how we do things in this house and the Honourable Member knows it. Please improve and resubmit your amendment.'
		await ctx.send(bot_message)


@bot.command()
async def setmusic(ctx, arg=None):
	if not ctx.message.author.id in preferences["admins"]:
		bot_message = 'I certainly won\'t take orders such as those from a junior minister! Hrumph!'
		await ctx.channel.send(bot_message)
		return

	if arg is None:
		if ctx.channel.id not in preferences["music_text"]:
			preferences["music_text"].append(ctx.channel.id)
			bot_message = 'I hereby give notice that the government has successfully passed a motion to designate this channel a music channel.'

			save(preferences, 'preferences.json')
		else:
			bot_message = 'It is rather disappointing that the honourable member insists on providing information we already know. If they would stop that would be much appreciated.'
	else:
		try:
			if int(arg) not in preferences["music_text"]:
				preferences["music_text"].append(int(arg))
				channel_name = bot.get_channel(int(arg)).name

				save(preferences, 'preferences.json')
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
	if ctx.message.author.id not in preferences["admins"]:
		bot_message = 'I certainly won\'t take orders such as those from a junior minister! Hrumph!'
		await ctx.channel.send(bot_message)
		return

	if arg is None:
		bot_message = 'I must kindly ask the Honourable Member to repeat their request but this time specifying a channel ID.'

		await ctx.send(bot_message)
		return
	else:
		try:
			if int(arg) not in preferences["music_voice"]:
				preferences["music_voice"].append(int(arg))
				channel_name = bot.get_channel(int(arg)).name

				save(preferences, 'preferences.json')
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
	if ctx.message.author.id not in preferences["admins"]:
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