import discord
from discord.ext import commands
import tkinter as tk
from tkinter import scrolledtext, simpledialog
import asyncio
import threading

# Discord bot setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# GUI setup
class BotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord Bot Controller")

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
        self.text_area.grid(column=0, row=0, padx=10, pady=10)

        self.conversation_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
        self.conversation_area.grid(column=1, row=0, padx=10, pady=10)

        self.start_button = tk.Button(root, text="Start Bot", command=self.start_bot)
        self.start_button.grid(column=0, row=1, padx=10, pady=10)

        self.exit_button = tk.Button(root, text="Exit", command=self.exit_bot)
        self.exit_button.grid(column=1, row=1, padx=10, pady=10)

        self.entry = tk.Entry(root, width=50)
        self.entry.grid(column=0, row=2, padx=10, pady=10)
        self.entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(root, text="Send", command=self.send_message_button)
        self.send_button.grid(column=0, row=3, padx=10, pady=10)

        self.server_var = tk.StringVar(value="")
        self.server_menu = tk.OptionMenu(root, self.server_var, "", command=self.update_channel_menu)
        self.server_menu.grid(column=0, row=4, padx=10, pady=10)

        self.channel_var = tk.StringVar(value="")
        self.channel_menu = tk.OptionMenu(root, self.channel_var, "")
        self.channel_menu.grid(column=0, row=5, padx=10, pady=10)

        self.refresh_button = tk.Button(root, text="Refresh Channel List", command=self.update_channel_menu)
        self.refresh_button.grid(column=0, row=6, padx=10, pady=10)

        self.refresh_server_button = tk.Button(root, text="Refresh Server List", command=self.update_server_menu)
        self.refresh_server_button.grid(column=1, row=6, padx=10, pady=10)

    def start_bot(self):
        token = simpledialog.askstring("Input", "Enter your Discord bot token:", parent=self.root)
        if token:
            self.text_area.insert(tk.END, "Starting bot...\n")
            threading.Thread(target=self.run_bot, args=(token,)).start()
        else:
            self.text_area.insert(tk.END, "No token provided. Bot not started.\n")

    def run_bot(self, token):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.start_bot_async(token))

    async def start_bot_async(self, token):
        await bot.start(token)

    def exit_bot(self):
        def close_bot():
            asyncio.run_coroutine_threadsafe(bot.close(), bot.loop).result()
            self.root.quit()
        threading.Thread(target=close_bot).start()

    def log_message(self, message):
        self.text_area.insert(tk.END, f"{message}\n")
        self.text_area.yview(tk.END)

    def log_conversation(self, message):
        self.conversation_area.insert(tk.END, f"{message}\n")
        self.conversation_area.yview(tk.END)

    def send_message(self, event):
        message = self.entry.get()
        if message:
            self.entry.delete(0, tk.END)
            asyncio.run_coroutine_threadsafe(self.send_discord_message(message), bot.loop)

    def send_message_button(self):
        message = self.entry.get()
        if message:
            self.entry.delete(0, tk.END)
            asyncio.run_coroutine_threadsafe(self.send_discord_message(message), bot.loop)

    async def send_discord_message(self, message):
        if bot.is_ready():
            server_name = self.server_var.get()
            channel_name = self.channel_var.get()
            for guild in bot.guilds:
                if guild.name == server_name:
                    for channel in guild.text_channels:
                        if channel.name == channel_name:
                            await channel.send(message)
                            self.log_message(f"Sent message to {guild.name} - {channel.name}: {message}")
                            return

    def list_chattable_areas(self):
        self.text_area.insert(tk.END, "Listing all chattable areas...\n")
        self.update_server_menu()
        self.text_area.yview(tk.END)

    def update_server_menu(self, *args):
        async def fetch_guilds():
            await bot.wait_until_ready()
            server_names = [guild.name for guild in bot.guilds]
            self.server_menu['menu'].delete(0, 'end')
            for name in server_names:
                self.server_menu['menu'].add_command(label=name, command=tk._setit(self.server_var, name))
            self.update_channel_menu()

        asyncio.run_coroutine_threadsafe(fetch_guilds(), bot.loop)

    def update_channel_menu(self, *args):
        channel_names = []
        server_name = self.server_var.get()
        for guild in bot.guilds:
            if guild.name == server_name:
                for channel in guild.text_channels:
                    channel_names.append(channel.name)
        self.channel_menu['menu'].delete(0, 'end')
        for name in channel_names:
            self.channel_menu['menu'].add_command(label=name, command=tk._setit(self.channel_var, name))

# Discord bot events
@bot.event
async def on_ready():
    gui.log_message(f'Logged in as {bot.user}')
    gui.list_chattable_areas()
    for guild in bot.guilds:
        gui.log_message(f'Connected to server: {guild.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    gui.log_message(f'{message.guild.name} - {message.channel.name} - {message.author}: {message.content}')
    gui.log_conversation(f'{message.guild.name} - {message.channel.name} - {message.author}: {message.content}')
    await bot.process_commands(message)

# Main function
if __name__ == "__main__":
    root = tk.Tk()
    gui = BotGUI(root)
    root.mainloop()