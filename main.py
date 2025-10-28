"""
Telegram Channel Reporter Userbot
Railway/Cloud Deployment Ready - FIXED VERSION
"""

import asyncio
import logging
import os
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import (
    InputReportReasonSpam,
    InputReportReasonViolence,
    InputReportReasonPornography,
    InputReportReasonChildAbuse,
    InputReportReasonCopyright,
    InputReportReasonFake,
    InputReportReasonIllegalDrugs,
    InputReportReasonOther
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ChannelReporterBot:
    """Automated Channel Reporter for Cloud Deployment"""
    
    def __init__(self):
        # Load from environment variables (Railway)
        self.api_id = int(os.getenv('API_ID', '0'))
        self.api_hash = os.getenv('API_HASH', '')
        self.phone_number = os.getenv('PHONE_NUMBER', '')
        self.session_string = os.getenv('SESSION_STRING', '')
        
        # Admin IDs who can control the bot
        admin_ids = os.getenv('ADMIN_IDS', '')
        self.admin_ids = [int(id.strip()) for id in admin_ids.split(',') if id.strip()]
        
        self.client = None
        
        # Statistics
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'started': datetime.now()
        }
        
        # Report reasons
        self.REASONS = {
            'spam': ('🚫 Spam', InputReportReasonSpam),
            'violence': ('🔴 Violence', InputReportReasonViolence),
            'porn': ('🔞 Pornography', InputReportReasonPornography),
            'child': ('🚨 Child Abuse', InputReportReasonChildAbuse),
            'copyright': ('🏴‍☠️ Copyright', InputReportReasonCopyright),
            'fake': ('📰 Fake News', InputReportReasonFake),
            'drugs': ('💊 Drugs', InputReportReasonIllegalDrugs),
            'other': ('⚙️ Other', InputReportReasonOther)
        }
    
    def is_admin(self, user_id):
        """Check if user is admin"""
        return user_id in self.admin_ids
    
    async def start(self):
        """Initialize the bot"""
        logger.info("🚀 Starting Channel Reporter Bot...")
        
        # Validate environment variables
        if not self.session_string:
            logger.error("❌ SESSION_STRING not found in environment variables!")
            logger.info("Run generate_session.py locally and add SESSION_STRING to Railway")
            return False
        
        if self.api_id == 0 or not self.api_hash:
            logger.error("❌ API_ID or API_HASH not configured!")
            return False
        
        if not self.admin_ids:
            logger.error("❌ ADMIN_IDS not configured!")
            return False
        
        # Create client with StringSession (CRITICAL FOR RAILWAY)
        self.client = TelegramClient(
            StringSession(self.session_string),
            self.api_id,
            self.api_hash
        )
        
        await self.client.connect()
        
        # Check authorization
        if not await self.client.is_user_authorized():
            logger.error("❌ Not authorized! Session string may be invalid.")
            logger.info("Regenerate session: python generate_session.py")
            return False
        
        me = await self.client.get_me()
        logger.info(f"✅ Logged in as: {me.first_name} (@{me.username or 'N/A'})")
        logger.info(f"👥 Admins: {self.admin_ids}")
        logger.info(f"📱 Phone: {self.phone_number}")
        
        # Setup handlers
        self.setup_handlers()
        return True
    
    def setup_handlers(self):
        """Setup message handlers"""
        
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            """Start command"""
            if not self.is_admin(event.sender_id):
                return
            
            uptime = datetime.now() - self.stats['started']
            hours = int(uptime.total_seconds() // 3600)
            
            menu = f"""
🤖 **Channel Reporter Bot**

📊 **Status:** Online ✅
⏱️ **Uptime:** {hours}h
📈 **Reports:** {self.stats['total']}

**Commands:**
`/report @channel spam` - Report single
`/bulk spam` - Start bulk mode
`/stats` - View statistics
`/help` - Show help

**Quick Report:**
Reply to channel message:
`/spam` `/fake` `/violence`

Bot is ready! 🚀
            """
            await event.reply(menu)
        
        @self.client.on(events.NewMessage(pattern=r'/report (@\w+|\S+) (\w+)'))
        async def report_command(event):
            """Report single channel: /report @channel reason"""
            if not self.is_admin(event.sender_id):
                return
            
            try:
                parts = event.text.split()
                if len(parts) < 3:
                    await event.reply("❌ Usage: `/report @channel reason`")
                    return
                
                channel = parts[1]
                reason = parts[2].lower()
                
                if reason not in self.REASONS:
                    await event.reply(f"❌ Invalid reason. Use: {', '.join(self.REASONS.keys())}")
                    return
                
                status = await event.reply(f"🔄 Reporting {channel}...")
                
                success = await self.report_channel(channel, self.REASONS[reason][1])
                
                if success:
                    await status.edit(f"✅ Successfully reported {channel}")
                else:
                    await status.edit(f"❌ Failed to report {channel}")
                    
            except Exception as e:
                await event.reply(f"❌ Error: {str(e)}")
        
        @self.client.on(events.NewMessage(pattern=r'/bulk (\w+)'))
        async def bulk_command(event):
            """Start bulk mode: /bulk reason"""
            if not self.is_admin(event.sender_id):
                return
            
            try:
                reason = event.text.split()[1].lower()
                
                if reason not in self.REASONS:
                    await event.reply(f"❌ Invalid reason. Use: {', '.join(self.REASONS.keys())}")
                    return
                
                await event.reply(
                    f"📋 **Bulk Mode: {self.REASONS[reason][0]}**\n\n"
                    f"Send channel list (one per line):\n"
                    f"```\n@channel1\n@channel2\nt.me/channel3\n```\n\n"
                    f"Reply with list when ready."
                )
                
                # Store state
                if not hasattr(self.client, 'bulk_modes'):
                    self.client.bulk_modes = {}
                
                self.client.bulk_modes[event.sender_id] = {
                    'reason': reason,
                    'timestamp': datetime.now()
                }
            except Exception as e:
                await event.reply(f"❌ Error: {str(e)}")
        
        @self.client.on(events.NewMessage)
        async def bulk_list_handler(event):
            """Handle bulk channel list"""
            if not self.is_admin(event.sender_id):
                return
            
            # Check if in bulk mode
            if not hasattr(self.client, 'bulk_modes'):
                return
            
            if event.sender_id not in self.client.bulk_modes:
                return
            
            # Parse channels
            text = event.text
            if not text or text.startswith('/'):
                return
            
            channels = []
            for line in text.split('\n'):
                line = line.strip()
                if line and not line.startswith('/'):
                    channels.append(self.clean_channel(line))
            
            if not channels:
                return
            
            # Get reason and clear bulk mode
            bulk_data = self.client.bulk_modes[event.sender_id]
            del self.client.bulk_modes[event.sender_id]
            
            # Start reporting
            reason_class = self.REASONS[bulk_data['reason']][1]
            await self.bulk_report(event, channels, reason_class)
        
        @self.client.on(events.NewMessage(pattern='/stats'))
        async def stats_command(event):
            """Show statistics"""
            if not self.is_admin(event.sender_id):
                return
            
            uptime = datetime.now() - self.stats['started']
            hours = int(uptime.total_seconds() // 3600)
            mins = int((uptime.total_seconds() % 3600) // 60)
            
            success_rate = 0
            if self.stats['total'] > 0:
                success_rate = (self.stats['success'] / self.stats['total']) * 100
            
            stats = f"""
📊 **Bot Statistics**

⏱️ **Uptime:** {hours}h {mins}m
📈 **Total Reports:** {self.stats['total']}
✅ **Successful:** {self.stats['success']}
❌ **Failed:** {self.stats['failed']}
📊 **Success Rate:** {success_rate:.1f}%

🕐 **Started:** {self.stats['started'].strftime('%Y-%m-%d %H:%M')}
            """
            await event.reply(stats)
        
        @self.client.on(events.NewMessage(pattern='/help'))
        async def help_command(event):
            """Show help"""
            if not self.is_admin(event.sender_id):
                return
            
            help_text = """
📚 **Help Guide**

**Single Report:**
`/report @channel spam`
`/report t.me/channel fake`

**Bulk Report:**
1. `/bulk spam` (or other reason)
2. Send list of channels
3. Auto-reports all

**Quick Report:**
Reply to channel message:
• `/spam` - Report spam
• `/fake` - Fake news
• `/violence` - Violence
• `/copyright` - Copyright

**Available Reasons:**
spam, violence, porn, child, copyright, fake, drugs, other

**Tips:**
✅ 7-10 sec delay between reports
✅ Max 50 reports/day
✅ Keep bot running 24/7

**Examples:**
`/report @scamchannel spam`
`/bulk fake`
(then send list)
            """
            await event.reply(help_text)
        
        # Quick report commands
        def create_quick_handler(reason_key):
            async def handler(event):
                if not self.is_admin(event.sender_id):
                    return
                if not event.is_reply:
                    await event.reply("⚠️ Reply to a channel message to report")
                    return
                
                try:
                    reply = await event.get_reply_message()
                    if reply.peer_id:
                        status = await event.reply("🔄 Reporting...")
                        entity = await self.client.get_entity(reply.peer_id)
                        success = await self.report_channel(entity, self.REASONS[reason_key][1])
                        
                        if success:
                            await status.edit(f"✅ Reported as {reason_key}!")
                        else:
                            await status.edit("❌ Failed!")
                except Exception as e:
                    await event.reply(f"❌ Error: {str(e)}")
            return handler
        
        # Register quick commands
        self.client.on(events.NewMessage(pattern='/spam'))(create_quick_handler('spam'))
        self.client.on(events.NewMessage(pattern='/fake'))(create_quick_handler('fake'))
        self.client.on(events.NewMessage(pattern='/violence'))(create_quick_handler('violence'))
        self.client.on(events.NewMessage(pattern='/copyright'))(create_quick_handler('copyright'))
        self.client.on(events.NewMessage(pattern='/porn'))(create_quick_handler('porn'))
        self.client.on(events.NewMessage(pattern='/drugs'))(create_quick_handler('drugs'))
    
    async def report_channel(self, channel, reason_class):
        """Report a single channel"""
        try:
            # Get entity
            if isinstance(channel, str):
                entity = await self.client.get_entity(channel)
            else:
                entity = channel
            
            # Send report
            result = await self.client(ReportPeerRequest(
                peer=entity,
                reason=reason_class(),
                message=""
            ))
            
            self.stats['total'] += 1
            
            if result:
                self.stats['success'] += 1
                username = getattr(entity, 'username', 'Unknown')
                logger.info(f"✅ Reported: @{username}")
                return True
            else:
                self.stats['failed'] += 1
                return False
                
        except Exception as e:
            self.stats['total'] += 1
            self.stats['failed'] += 1
            logger.error(f"❌ Report error: {str(e)}")
            return False
    
    async def bulk_report(self, event, channels, reason_class, delay=8):
        """Report multiple channels"""
        total = len(channels)
        progress = await event.reply(
            f"🔄 **Bulk Report Started**\n\n"
            f"📊 Total: {total} channels\n"
            f"⏱️ Estimated: {total * delay}s\n\n"
            f"Processing..."
        )
        
        success_count = 0
        failed_count = 0
        
        for idx, channel in enumerate(channels, 1):
            # Report
            success = await self.report_channel(channel, reason_class)
            
            if success:
                success_count += 1
            else:
                failed_count += 1
            
            # Update progress every 5 reports
            if idx % 5 == 0 or idx == total:
                await progress.edit(
                    f"🔄 **Bulk Report Progress**\n\n"
                    f"📊 {idx}/{total} processed\n"
                    f"✅ Success: {success_count}\n"
                    f"❌ Failed: {failed_count}\n\n"
                    f"{'⏳ Working...' if idx < total else '✅ Complete!'}"
                )
            
            # Delay
            if idx < total:
                await asyncio.sleep(delay)
        
        # Final summary
        await progress.edit(
            f"✅ **Bulk Report Complete!**\n\n"
            f"📊 Total: {total}\n"
            f"✅ Success: {success_count}\n"
            f"❌ Failed: {failed_count}\n"
            f"📈 Rate: {(success_count/total*100):.1f}%"
        )
    
    def clean_channel(self, channel):
        """Clean channel format"""
        channel = channel.strip()
        if channel.startswith('https://t.me/'):
            return '@' + channel.split('/')[-1]
        elif channel.startswith('t.me/'):
            return '@' + channel.split('/')[-1]
        elif not channel.startswith('@'):
            return '@' + channel
        return channel
    
    async def run(self):
        """Run the bot"""
        if await self.start():
            logger.info("✅ Bot is running!")
            logger.info("💬 Send /start to your account to begin")
            await self.client.run_until_disconnected()
        else:
            logger.error("❌ Failed to start bot")


async def main():
    """Main entry point"""
    bot = ChannelReporterBot()
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
