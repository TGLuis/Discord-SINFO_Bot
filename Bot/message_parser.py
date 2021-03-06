# created by Sami Bosch on Thursday, 08 November 2018

# This file contains all functions necessary to reply to messages
import json
import os

import discord
import random

from course_handler import create_course, get_courses
from discord_utils import AsyncTimer
from tex_handler import *

haddock = '../haddock.json'
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, haddock)
with open(filename) as f:
    quotes = json.load(f)["quotes"]


def init(client):
    @client.command(pass_context=True)
    async def ban(context):
        """Takes a list of mentioned users + optionally an int. Bans all users in list, and if int has been supplied,
        unbans them after given time in days."""
        m = context.message
        if m.content.find(" ") > 0:
            try:
                unban_time = float(m.content.split(" ")[-1])
            except ValueError:
                unban_time = -1
        else:
            unban_time = -1

        if m.author.server_permissions.ban_members:
            for member in m.mentions:
                await client.ban(member, delete_message_days=0)
                await client.say("banned {} for {} days (-1 = indefinite)".format(member.nick, unban_time))

            if unban_time >= 0:
                async def unban_all():
                    for member in m.mentions:
                        await client.unban(m.server, member)
                        await client.send_message(m.channel, "unbanned {}".format(member.nick))

                AsyncTimer(unban_time * 86400, unban_all)
        else:
            await client.say("You do not have the permission to ban users")

    @client.command(pass_context=True)
    async def kick(context):
        """Takes a list of mentioned users and kicks them all."""
        m = context.message
        if m.author.server_permissions.kick_members:
            for member in m.mentions:
                await client.kick(member)
                await client.say("kicked {}".format(member.nick))
        else:
            await client.say("You do not have the permission to kick users")

    @client.command(aliases=['mute', 'silence'], pass_context=True)
    async def timeout(context):
        """Takes a list of mentioned users and a timeout at the end of the message and silences all users for the
        specified time in minutes."""
        m = context.message
        muted = discord.utils.get(m.server.roles, name='Muted')
        if m.content.find(" ") > 0:
            try:
                mute_time = float(m.content.split(" ")[-1])
            except ValueError:
                mute_time = -1
        else:
            mute_time = -1

        if m.author.server_permissions.manage_roles and mute_time >= 0:
            for member in m.mentions:
                await client.add_roles(member, muted)
                await client.say("Muted {} for {} minutes".format(member.nick, int(mute_time)))
            if mute_time >= 0:
                async def unban_all():
                    for member in m.mentions:
                        await client.remove_roles(member, muted)
                        await client.send_message(m.channel, "Unmuted {}".format(member.nick))

                AsyncTimer(mute_time * 60, unban_all)
        elif mute_time == -1:
            await client.say("Please provide a time (in minutes)")
        else:
            await client.say("You do not have the permission to ban users")

    @client.command(aliases=['add', 'ac'], pass_context=True)
    async def add_course(context):
        """Creates a channel and role for a list of courses."""
        m = context.message
        u = m.author
        if u.server_permissions.manage_channels:
            message = m.content
            if message.find(" ") > 0:
                for name in message.split(" ")[1:]:
                    role = discord.utils.get(m.server.roles, name=name.upper())
                    if role:
                        await client.say("Course exists!")
                    else:
                        await create_course(name, client, m.server)
                        await client.say("Created channel and role {}".format(name))
            else:
                await client.say("Please provide a name")
        else:
            await client.say("You don't have the permissions to use this command.")

    @client.command(aliases=['follow', 'fc'], pass_context=True)
    async def follow_course(context):
        """Allows an user to follow a list of courses."""
        m = context.message
        u = m.author

        message = m.content
        if message.find(" ") > 0:
            roles = []
            success = ""
            fail = ""
            refused = ""
            for name in message.split(" ")[1:]:
                role = discord.utils.get(m.server.roles, name=name.upper())
                if role:
                    annonceur = discord.utils.get(m.server.roles, name="Annonceur")
                    if role >= annonceur or role in u.roles:
                        refused += name + " "
                    else:
                        roles.append(role)
                        success += name + " "
                else:
                    fail += name + " "
            full = "You successfully followed: " + success.strip() + "\n" if success else ""
            full += "Couldn't follow: " + refused.strip() + "\n" if refused else ""
            full += "Couldn't find: " + fail.strip() if fail else ""
            await client.add_roles(u, *roles)
            await client.send_message(u, full.strip())
        else:
            await client.say("Please provide a course to follow")

    @client.command(aliases=['unfollow', 'uc'], pass_context=True)
    async def unfollow_course(context):
        """Allows an user to unfollow a list of courses."""
        m = context.message
        u = m.author

        message = m.content
        if message.find(" ") > 0:
            roles = []
            success = ""
            fail = ""
            refused = ""
            for name in message.split(" ")[1:]:
                role = discord.utils.get(m.server.roles, name=name.upper())
                if role:
                    annonceur = discord.utils.get(m.server.roles, name="Annonceur")
                    if role >= annonceur or role not in u.roles:
                        refused += name + " "
                    else:
                        roles.append(role)
                        success += name + " "
                else:
                    fail += name + " "
            full = "You successfully unfollowed: " + success.strip() + "\n" if success else ""
            full += "Couldn't unfollow: " + refused.strip() + "\n" if refused else ""
            full += "Couldn't find: " + fail.strip() if fail else ""
            await client.remove_roles(u, *roles)
            await client.send_message(u, full.strip())
        else:
            await client.say("Please provide a course to follow")

    @client.command(aliases=['list', 'lc'], pass_context=True)
    async def list_courses(context):
        """Lists all available courses in the server."""
        courses = get_courses(context.message.server)

        s = "| "
        for course in courses:
            s += course + " | "
        await client.say(s.strip())

    @client.command(aliases=['hello', 'hi', "bonjour", "bjr"], pass_context=True)
    async def greetings(context):
        """Answer with an hello message"""
        m = context.message
        if m.content.startswith('!bonjour') or m.content.startswith('!bjr'):
            msg = 'Bonjour {0.author.mention} !'.format(m)
        else:
            msg = 'Hello {0.author.mention}!'.format(m)
        await client.say(msg)

    @client.command(aliases=['haddockquote', 'haddock', 'hq'], pass_context=True)
    async def haddock_says(context):
        """Give a quote from Haddock"""
        msg = random.choice(quotes)
        await client.say(msg)

    """
        This command is greatly inspired by the bot of DXsmiley on github:
        https://github.com/DXsmiley/LatexBot
        To implement this command you must install on linux:
        texlive, dvipng
    """
    @client.command(aliases=['tex'], pass_context=True)
    async def latex(context):
        """Answer with the text send, generated in latex. (in the align* environment)"""
        m = context.message

        my_latex = m.content[m.content.find(" "):].strip()
        num = str(random.randint(0, 2 ** 31))
        fn = generate_image(my_latex, num)

        if fn and os.path.getsize(fn) > 0:
            await client.send_file(m.channel, fn)
        else:
            await client.say('Something broke. Check the syntax of your message. :frowning:')

        cleanup_output_files(num)
