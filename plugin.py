###
# Copyright (c) 2013, Nicolas Coevoet
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
import supybot.ircdb as ircdb
import subprocess
from random import *
try:
	from supybot.i18n import PluginInternationalization
	_ = PluginInternationalization('Hailo')
except:
	# Placeholder that allows to run the plugin on a bot
	# without the i18n module
	_ = lambda x:x

def escape(s):
	return s

def similar (a,b):
	sa, sb = set(a), set(b)
	n = len(sa.intersection(sb))
	jacc = n / float(len(sa) + len(sb) - n)
	return jacc

class Hailo(callbacks.Plugin):
	"""this plugin allows the bot to communicate with Hailo"""
	threaded = True

	def callHailo (self,channel,arg,text):
		msg = None
		try:
			args = []
			args.append(self.registryValue('hailoPath'))
			args.append('-b')
			args.append(self.registryValue('hailoBrain',channel=channel))
			args.append(arg)
			if len(text):
				args.append(text)
			(msg, err) = subprocess.Popen(args,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
			if err:
				self.log.debug(err)
			if msg != None:
				msg = msg.replace('\n',' ')
		except subprocess.CalledProcessError:
			msg = None
		return msg

        def brainstats (self,irc,msg,args,channel):
		"""[<channel>]

		return brain stats"""
                m = self.callHailo(channel,'-s','')
                if m != None:
                	irc.reply(m)
	brainstats = wrap(brainstats,['op'])

	def doPrivmsg (self,irc,msg):
		(targets, t) = msg.args
		text = escape(t)
		if msg.prefix == irc.prefix:
			return
		for channel in targets.split(','):
			if irc.isChannel(channel) and channel in irc.state.channels:
				learn = self.registryValue('learn',channel=channel)
				replyRandom = self.registryValue('replyPercent',channel=channel) > 0.00
				replyAddressed = self.registryValue('replyWhenAddressed',channel=channel)
				called = False
				if ircdb.checkIgnored(msg.prefix,channel):
					continue
				if not learn and not replyRandom and not replyAddressed:
					continue
				if replyAddressed and msg.addressed:
					text = escape(callbacks.addressed(irc.nick,msg))
					m = None
					if learn:
						m = self.callHailo(channel,'-L',text)
					else:
						m = self.callHailo(channel,'-r',text)
					if m != None and len(m):
						irc.queueMsg(ircmsgs.privmsg(channel,m))
					called = True
				if not msg.addressed and replyRandom and randint(1,99) < self.registryValue('replyPercent',channel=channel)*100:
					m = None
					if learn:
						m = self.callHailo(channel,'-L',text)
					else:
						m = self.callHailo(channel,'-r',text)
					called = True
					if m != None and len(m):
						if self.registryValue('checkSimilarity',channel=channel):
							if similar(m,text) < self.registryValue('similarity',channel=channel):
								irc.queueMsg(ircmsgs.privmsg(channel,m))
						else:
							irc.queueMsg(ircmsgs.privmsg(channel,m))
				if not called and learn:
					self.callHailo(channel,'-l',text)
				
Class = Hailo


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
