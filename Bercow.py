# Work with Python 3.6

import asyncio
from discord.ext import commands
import random
import argparse
import json
import aiofiles
import time


# from methods import save


class NoExitParser(argparse.ArgumentParser):
	def error(self, message):
		raise ValueError(message)


owner_id = 345468527538339850
command_prefix = '?'




# with open('preferences.json', 'r') as file:
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
		super().__init__(command_prefix=command_prefix)
		self.config_location = config
		with open(config, 'r') as x:
			self.settings = json.load(x)
		if not owner_id in self.settings['admins']:
			self.settings['admins'].append(owner_id)
		self.current_votes = []
		self.current_vote_channels = []
		self.emoji_tu = '\U0001f44d'
		self.emoji_td = '\U0001f44e'
		self.politics_cooldowns ={}
		#print(json.dumps(self.settings, indent=4, sort_keys=True))

	async def on_ready(self):
		print('Logged in as')
		print(self.user.name)
		print(self.user.id)
		print('------')

	async def on_message(self, message):
		if message.content[:1]!=command_prefix:
			if message.author.bot or message.channel.id in self.settings["no_bercow"]:
				return

			if await self.mr_speaker(message):
				return

			if await self.politics_chat(message):
				return

		await self.process_commands(message)
	
	async def on_command_error(self, ctx, error):
		if isinstance(error,commands.CommandOnCooldown):
			await ctx.author.send(random.choice(self.settings["responses"]["cooldown"]).format(ctx))
			try:
				await ctx.message.delete()
			except commands.Forbidden:
				print("I do not have permissions to delete messages in {0.channel.name}".format(ctx))
			

	async def mr_speaker(self, message):
		# Corrects member if they refer to Mr Speaker by name
		if ('bercow' in message.content or self.user in message.mentions) and command_prefix not in message.content:
			await message.channel.send('ORDER! The Honourable Member must refer to me as Mr Speaker at all times. I ask that they withdraw their comment.')
			return True
		return False

	async def politics_chat(self, message):
		# Identifies politics chat in wrong channels
		message_words = message.content.lower().split(' ')
		if not set(message_words).isdisjoint(set(self.settings['politics_triggers'])) and message.channel.id not in self.settings["politics_channels"]:
			if message.channel.id in self.politics_cooldowns:
				if self.politics_cooldowns[message.channel.id]+60<time.time():
					await self.politics_warn(message.channel, message.author)
					self.politics_cooldowns[message.channel.id] = time.time()
					return True
				else:
					await self.politics_warn(message.author, message.author)
					return False
			else:
				await self.politics_warn(message.channel, message.author)
				self.politics_cooldowns[message.channel.id] = time.time()
				return True
			
		return False
	
	async def politics_warn(self, target_channel, target_user):
		'''Warn messageable to use an appropriate channel'''
		bot_message = random.choice(self.settings['responses']['politics']).format(target_user)
		await target_channel.send(bot_message)
	

	async def save_settings(self):
		# Saves the bot settings to an appropriate location
		async with aiofiles.open(self.config_location, "w+") as x:
			await x.write(json.dumps(self.settings, indent=4, sort_keys=True))

	async def set_politics(self, channel_id):
		if channel_id not in self.settings['politics_channels']:
			self.settings['politics_channels'].append(channel_id)
			await self.save_settings()
			return 'I thank the Honourable Member for identifying this as the correct forum for political discussion'
		else:
			return random.choice(self.settings['responses']['repeat'])

	async def set_music(self, channel_id):
		if channel_id not in self.settings['music_text']:
			channel = self.get_channel(channel_id)
			if channel is None:
				return random.choice(self.settings['responses']['invalid'])
			else:
				self.settings['music_text'].append(channel_id)
				await self.save_settings()
				return 'I hereby give notice that the government has successfully passed a motion to designate ' + channel.name + ' a music channel.'
		else:
			return random.choice(self.settings['responses']['repeat'])
			
	async def dispense_popcorn(self, channel, number):
		'''Dispense the appropriate number of popcorn'''
		popcorn_emoji = '\U0001f37f'
		if number<=0:
			response = 'I implore the Honourable Member to suggest how I should go about providing that many boxes of popcorn.'
		else:
			if number >20:
				response = random.choice(self.settings['responses']['too_much_corn'])
				number = 20
			else:
				response = "As requested, here is the honourable member's popcorn:\n"
			response = response + ''.join([popcorn_emoji] * number)
			await channel.send(response)
			
	async def start_poll(self, motion, context, time, unanimous):
		'''Initiates a poll given the motion, message context, time and unanimous parameters'''
		ctx = context
		#await ctx.send("Poll initiated")
		if unanimous:
			unanimous_str = 'This motion must be passed unanimously.'
		else:
			unanimous_str = ''
		#ctx.send("Unanimous processed")

		bot_message_a = 'The question is that ' + motion
		bot_message_a = bot_message_a + '\nAs many as are of that opinion react ' + self.emoji_tu + '. On the contrary ' + self.emoji_td + '.'
		bot_message_b = ('DIVISION! CLEAR THE LOBBY. You have %d seconds to vote. ' + unanimous_str) % time
		poll_question = await ctx.send(bot_message_a)
		await ctx.send(bot_message_b)
		poll_id = poll_question.id
		await poll_question.add_reaction(self.emoji_tu)
		await poll_question.add_reaction(self.emoji_td)		
		print("About to append to current_votes")
		self.current_votes.append({"motion": motion, "poll_id": poll_id, "channel": ctx.channel.id, "unanimous":unanimous})
		print(self.current_votes)
		
		await asyncio.sleep(time)
		
		for x in self.current_votes:
			if x["poll_id"]==poll_id:
#				await ctx.send("calling resolve_poll")
				await self.resolve_poll(poll_id)
		else:
			print("Vote {0} has been cancelled".format(poll_id))
		

		
		

	async def resolve_poll(self, poll_id):
		'''Resolves a poll given a poll message ID'''
		for x in self.current_votes:
			if x["poll_id"]==poll_id:
				channel = self.get_channel(x["channel"])
#				await channel.send("Got poll and context")
				try:
					#Get poll message
					final_poll = await channel.fetch_message(poll_id)
					poll_result = final_poll.reactions
					print(poll_result)

					ayes = 0
					noes = 0
					
					bot_message = ''
					
					#Perform the count
					for result in poll_result:
						if result.emoji == self.emoji_tu:
							ayes = result.count - 1
						elif result.emoji == self.emoji_td:
							noes = result.count - 1
						else:
							bot_message = 'I see an honourable member has abstained from voting by providing an alternative response. I reassure them that this will go on the record, ' \
										  'although I\'m not sure what good it will do.\n'
					channel.send("results processed")
					#No votes
					if ayes + noes ==0:
						bot_message = 'I see no-one has cast a vote. I would ask that in future, the honourable member refrains from proposing motions that even he is ambivalent about.'
					else:		
						bot_message = bot_message +	'The ayes to the right: %d. The noes to the left: %d \n' % (ayes, noes)

					#Unanimous vote failed
					if x["unanimous"] and not (ayes == 0 or noes == 0):
						bot_message = bot_message + 'I notice that there is disagreement amoungst Honourable Members. So the unanimous motion has failed.'

					#Clear winner
					elif not ayes == noes:
						winner = {
							0: 'noes',
							1: 'ayes'
						}
						result_str = winner[ayes > noes]
						bot_message = bot_message + 'So the %s have it. The %s have it. \n' % (result_str, result_str)
						if x["unanimous"]:
							bot_message = bot_message + 'Thus this unanimous motion has passed successfully.\n'
					
					else:
						bot_message = 'It is parliamentary custom for the speaker not to create a majority where one would otherwise not exist. So I cast my vote with the noes. The noes have it.\n'
					bot_message = bot_message + 'UNLOCK!'
					await channel.send(bot_message)
					self.current_vote_channels.remove(channel.id)
				except Exception as e:
					print('Caught error: ' + repr(e))
					bot_message = 'I am afraid there has been a counting issue and we must hold the vote again at a later date.'
					self.current_vote_channels.remove(channel.id)

					await channel.send(bot_message)				

				self.current_votes.remove(x)

#instantiate the bot				
bot = BotClient(command_prefix, 'preferences.json')


@bot.command()
@commands.cooldown(2,60, type=commands.BucketType.channel)
async def burn(ctx, arg=None):
	'''Applies a witty burn to a user of your choice'''
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
				if arg.lower() in x.display_name.lower() or arg.lower() in x.name.lower():
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
	'''Specifies a channel for politics.'''
	#Check authorisation
	if not ctx.message.author.id in bot.settings["admins"]:
		bot_message = random.choice(bot.settings['responses']['unauthorised'])
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
			bot_message = random.choice(bot.settings['responses']['invalid'])
	await ctx.send(bot_message)



@bot.command()
async def nobercow(ctx, arg=None):
	'''Specify a channel to exclude Bercow'''
	if not ctx.message.author.id in bot.settings["admins"]:
		bot_message = random.choice(bot.settings['responses']['unauthorised'])
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
	'''Designates a channel as a music channel'''
	if not ctx.message.author.id in bot.settings["admins"]:
		bot_message = random.choice(bot.settings['responses']['unauthorised']).format(ctx)
	else:
		try:
			if arg is None:
				cid = ctx.channel.id
			else:
				cid = int(arg)
			bot_message = await bot.set_music(cid)
			await ctx.send(bot_message)
		except:
			# Broad exception because Bercow is lazy
			bot_message = random.choice(bot.settings['responses']['invalid'])
	await ctx.send(bot_message)



@bot.command()
async def setdj(ctx, arg=None):
	'''Set a user as a DJ'''
	if ctx.message.author.id not in bot.settings["admins"]:
		bot_message = random.choice(bot.settings['responses']['unauthorised']).format(ctx)
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
				bot_message = random.choice(bot.settings['responses']['repeat']).format(ctx)
				await ctx.send(bot_message)

				return
		except:
			# Broad exception because Bercow is lazy
			bot_message = 'Unfortunately the Honourable Member has made an invalid request; I ask that they try again.'
		else:
			bot_message = 'I hereby give notice that the government has successfully passed a motion to designate ' + channel_name + ' a DJ channel.'

	await ctx.send(bot_message)


@bot.command()
#@commands.cooldown(1,600, type=commands.BucketType.channel)
async def vote(ctx, *args):
	'''Initiates a vote on a motion of your choice'''
	#await ctx.send("vote commenced")
	if len(args) == 0:
		bot_message = 'I\'m sure the Honourable Member is well aware that we cannot hold a vote unless they specify a motion. Please, try again {0.mention}'.format(ctx.author)
		await ctx.send(bot_message)
		return
	if ctx.channel.id in bot.current_vote_channels:
		msg = random.choice(bot.settings["responses"]["multiple_votes"]).format(ctx)
		await ctx.send(msg)
		return
	else:
		bot.current_vote_channels.append(ctx.channel.id)
#	await ctx.send("About to parse parameters")
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
	if parsed_args.unanimous is None:
		unanimous = False
	else:
		unanimous = parsed_args.unanimous
	args = [a for a in args if not (a.startswith('-') or args[args.index(a) - 1] in value_required)]
#	await ctx.send("Parsed Arguments")
	motion = ' '.join(args)
	#await ctx.send(motion)
	await bot.start_poll(motion, ctx, time, unanimous)




@bot.command()
async def source(ctx):
	'''Bercow will provide a link to the source code'''
	await ctx.send("You can find the source code for this bot at https://github.com/eclecticgamer/BercowBot")

	
@bot.command()
@commands.cooldown(1,60,type=commands.BucketType.channel)
async def popcorn(ctx, *args):
	popcorn_emoji = '\U0001f37f'
	try:
		if len(args) == 0:
			num_popcorns = 5
		elif len(args) == 1:
			num_popcorns = int(args[0])
		else:
			raise TypeError('More than one argument')
	except TypeError:
		popcorn_response = 'I admire the Honourable Member\'s enthusiasm but remind them that I would struggle to fulfill their request considering conflicting information has been provided.'
		await ctx.send(popcorn_response)
	except:
		popcorn_response = 'I will be the first to admit that the Honourable Member\'s request has confused me. How would they like me to use the irrelevant information they have provided ' \
								'me with?'
		await ctx.send(popcorn_response)
	else:
		await bot.dispense_popcorn(ctx.channel, num_popcorns)



bot.run(TOKEN)




