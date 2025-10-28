"""
Telegram Channel Reporter Userbot - ENHANCED VERSION
Railway/Cloud Deployment Ready with Advanced Progress Tracking
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
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

# Configure logging with more detail
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ChannelReporterBot:
    """Advanced Automated Channel Reporter with Enhanced Progress Tracking"""
    
    def __init__(self):
        # Load from environment variables
        self.api_id = int(os.getenv('API_ID', '0'))
        self.api_hash = os.getenv('API_HASH', '')
        self.phone_number = os.getenv('PHONE_NUMBER', '')
        self.session_string = os.getenv('SESSION_STRING', '')
        
        # Admin IDs who can control the bot
        admin_ids = os.getenv('ADMIN_IDS', '')
        self.admin_ids = [int(id.strip()) for id in admin_ids.split(',') if id.strip()]
        
        self.client = None
        
        # Enhanced Statistics with detailed tracking
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'started': datetime.now(),
            'today_reports': 0,
            'last_reset': datetime.now().date(),
            'session_reports': []  # Track recent reports
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
        
        # Progress tracking settings
        self.PROGRESS_UPDATE_INTERVAL = 1  # Update every report (can be changed to 5, 10, etc.)
    
    def is_admin(self, user_id):
        """Check if user is admin"""
        return user_id in self.admin_ids
    
    def reset_daily_stats(self):
        """Reset daily statistics if new day"""
        today = datetime.now().date()
        if today > self.stats['last_reset']:
            self.stats['today_reports'] = 0
            self.stats['last_reset'] = today
            logger.info("📅 Daily statistics reset")
    
    async def start(self):
        """Initialize the bot"""
        logger.info("🚀 Starting Enhanced Channel Reporter Bot...")
        
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
        
        # Create client with StringSession
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
            """Start command with enhanced menu"""
            if not self.is_admin(event.sender_id):
                return
            
            self.reset_daily_stats()
            uptime = datetime.now() - self.stats['started']
            hours = int(uptime.total_seconds() // 3600)
            mins = int((uptime.total_seconds() % 3600) // 60)
            
            menu = f"""
🤖 **Enhanced Channel Reporter Bot v2.0**

📊 **Status:**
• Online: ✅ Active
• Uptime: {hours}h {mins}m
• Total Reports: {self.stats['total']}
• Today's Reports: {self.stats['today_reports']}/50
• Success Rate: {(self.stats['success']/max(self.stats['total'],1)*100):.1f}%

**📋 Commands:**
• `/report @channel spam` - Single report
• `/bulk spam 50` - Bulk report (specify count)
• `/auto spam` - Interactive bulk mode
• `/stats` - Detailed statistics
• `/help` - Full command guide

**⚡ Quick Report (Reply to message):**
• `/spam` `/fake` `/violence` `/copyright`

**✨ New Features:**
• Live progress tracking
• Detailed logging
• Smart retry logic
• Daily limits tracking

Bot is ready! 🚀
            """
            await event.reply(menu)
        
        @self.client.on(events.NewMessage(pattern=r'/report (@\w+|\S+) (\w+)'))
        async def report_command(event):
            """Report single channel with enhanced feedback"""
            if not self.is_admin(event.sender_id):
                return
            
            try:
                parts = event.text.split()
                if len(parts) < 3:
                    await event.reply("❌ Usage: `/report @channel reason`\n\nExample: `/report @spamchannel spam`")
                    return
                
                channel = parts[1]
                reason = parts[2].lower()
                
                if reason not in self.REASONS:
                    reasons_list = ', '.join(f'`{r}`' for r in self.REASONS.keys())
                    await event.reply(f"❌ Invalid reason.\n\n**Available reasons:**\n{reasons_list}")
                    return
                
                # Enhanced status message
                start_time = datetime.now()
                status = await event.reply(
                    f"🔄 **Initiating Report**\n\n"
                    f"🎯 Target: `{channel}`\n"
                    f"⚠️ Reason: {self.REASONS[reason][0]}\n"
                    f"📊 Progress: Connecting...\n"
                    f"⏳ Please wait..."
                )
                
                logger.info(f"\n{'═'*70}")
                logger.info(f"📍 SINGLE REPORT REQUEST")
                logger.info(f"{'═'*70}")
                logger.info(f"🎯 Channel: {channel}")
                logger.info(f"⚠️ Reason: {self.REASONS[reason][0]}")
                logger.info(f"👤 Requested by: {event.sender_id}")
                logger.info(f"🕐 Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'─'*70}")
                
                # Update status: Resolving
                await status.edit(
                    f"🔄 **Processing Report**\n\n"
                    f"🎯 Target: `{channel}`\n"
                    f"⚠️ Reason: {self.REASONS[reason][0]}\n"
                    f"📊 Progress: Resolving channel...\n"
                    f"⏳ Processing..."
                )
                
                logger.info(f"🔍 Resolving channel entity...")
                
                # Report the channel
                success = await self.report_channel(channel, self.REASONS[reason][1])
                
                elapsed = (datetime.now() - start_time).total_seconds()
                
                if success:
                    logger.info(f"✅ REPORT SUCCESSFUL")
                    logger.info(f"⏱️ Time taken: {elapsed:.2f}s")
                    logger.info(f"📊 Total reports: {self.stats['total']}")
                    logger.info(f"✅ Success count: {self.stats['success']}")
                    logger.info(f"{'═'*70}\n")
                    
                    await status.edit(
                        f"✅ **Report Successful!**\n\n"
                        f"🎯 Target: `{channel}`\n"
                        f"⚠️ Reason: {self.REASONS[reason][0]}\n"
                        f"⏱️ Time: {elapsed:.2f}s\n"
                        f"📊 Total: {self.stats['total']} | Today: {self.stats['today_reports']}\n"
                        f"✅ Success Rate: {(self.stats['success']/self.stats['total']*100):.1f}%\n\n"
                        f"💡 Report submitted to Telegram"
                    )
                else:
                    logger.info(f"❌ REPORT FAILED")
                    logger.info(f"⏱️ Time taken: {elapsed:.2f}s")
                    logger.info(f"{'═'*70}\n")
                    
                    await status.edit(
                        f"❌ **Report Failed**\n\n"
                        f"🎯 Target: `{channel}`\n"
                        f"⚠️ Reason: {self.REASONS[reason][0]}\n"
                        f"⏱️ Time: {elapsed:.2f}s\n\n"
                        f"**Possible Issues:**\n"
                        f"• Channel not found or invalid\n"
                        f"• Already reported recently\n"
                        f"• Rate limit reached (max 50/day)\n"
                        f"• Network connectivity issue\n\n"
                        f"💡 Try again after a few minutes"
                    )
                    
            except Exception as e:
                logger.error(f"❌ Error in report command: {str(e)}", exc_info=True)
                await event.reply(f"❌ **Error occurred:**\n`{str(e)}`")
        
        @self.client.on(events.NewMessage(pattern=r'/bulk (\w+)(?:\s+(\d+))?'))
        async def bulk_command(event):
            """Enhanced bulk mode with count specification"""
            if not self.is_admin(event.sender_id):
                return
            
            try:
                parts = event.text.split()
                reason = parts[1].lower()
                count = int(parts[2]) if len(parts) > 2 else None
                
                if reason not in self.REASONS:
                    reasons_list = ', '.join(f'`{r}`' for r in self.REASONS.keys())
                    await event.reply(f"❌ Invalid reason.\n\n**Available reasons:**\n{reasons_list}")
                    return
                
                count_text = f" (expecting {count} channels)" if count else ""
                
                await event.reply(
                    f"📋 **Bulk Mode Activated**\n\n"
                    f"⚠️ Reason: {self.REASONS[reason][0]}{count_text}\n\n"
                    f"**Send your channel list:**\n"
                    f"```\n@channel1\n@channel2\nt.me/channel3\nhttps://t.me/channel4\n```\n\n"
                    f"**Features:**\n"
                    f"✅ Live progress updates\n"
                    f"✅ Detailed success/fail tracking\n"
                    f"✅ Time estimates\n"
                    f"✅ Comprehensive summary\n\n"
                    f"💬 Reply with your list when ready!"
                )
                
                # Store state
                if not hasattr(self.client, 'bulk_modes'):
                    self.client.bulk_modes = {}
                
                self.client.bulk_modes[event.sender_id] = {
                    'reason': reason,
                    'expected_count': count,
                    'timestamp': datetime.now()
                }
                
            except Exception as e:
                await event.reply(f"❌ Error: {str(e)}")
        
        @self.client.on(events.NewMessage(pattern='/auto'))
        async def auto_command(event):
            """Interactive auto mode"""
            if not self.is_admin(event.sender_id):
                return
            
            await event.reply(
                f"🤖 **Auto Report Mode**\n\n"
                f"This will guide you through bulk reporting.\n\n"
                f"**Step 1:** Choose reason\n"
                f"Reply with: `spam`, `fake`, `violence`, etc.\n\n"
                f"**Step 2:** Send channel list\n"
                f"**Step 3:** Confirm and start\n\n"
                f"💡 Type `/cancel` to exit"
            )
        
        @self.client.on(events.NewMessage)
        async def bulk_list_handler(event):
            """Handle bulk channel list with validation"""
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
            invalid_lines = []
            
            for line_num, line in enumerate(text.split('\n'), 1):
                line = line.strip()
                if line and not line.startswith('/'):
                    cleaned = self.clean_channel(line)
                    if cleaned:
                        channels.append(cleaned)
                    else:
                        invalid_lines.append((line_num, line))
            
            if not channels:
                await event.reply("❌ No valid channels found in your list.\n\nPlease send channel usernames or links.")
                return
            
            # Get reason and clear bulk mode
            bulk_data = self.client.bulk_modes[event.sender_id]
            del self.client.bulk_modes[event.sender_id]
            
            # Validate count if specified
            expected = bulk_data.get('expected_count')
            if expected and len(channels) != expected:
                warning = f"\n⚠️ Expected {expected} channels, got {len(channels)}"
            else:
                warning = ""
            
            # Show confirmation
            confirmation = await event.reply(
                f"📋 **Channels Parsed**\n\n"
                f"✅ Valid: {len(channels)}\n"
                f"❌ Invalid: {len(invalid_lines)}{warning}\n\n"
                f"⚠️ Reason: {self.REASONS[bulk_data['reason']][0]}\n"
                f"⏱️ Est. Time: ~{len(channels) * 8}s ({len(channels) * 8 // 60}m)\n\n"
                f"🚀 Starting bulk report..."
            )
            
            await asyncio.sleep(2)  # Brief pause
            
            # Start reporting with enhanced tracking
            reason_class = self.REASONS[bulk_data['reason']][1]
            await self.bulk_report_enhanced(event, channels, reason_class, confirmation)
        
        @self.client.on(events.NewMessage(pattern='/stats'))
        async def stats_command(event):
            """Show detailed statistics"""
            if not self.is_admin(event.sender_id):
                return
            
            self.reset_daily_stats()
            
            uptime = datetime.now() - self.stats['started']
            hours = int(uptime.total_seconds() // 3600)
            mins = int((uptime.total_seconds() % 3600) // 60)
            
            success_rate = 0
            if self.stats['total'] > 0:
                success_rate = (self.stats['success'] / self.stats['total']) * 100
            
            # Recent activity
            recent = "No recent activity"
            if self.stats['session_reports']:
                recent_list = self.stats['session_reports'][-5:]
                recent = "\n".join([f"• {r['time'].strftime('%H:%M')} - {r['channel']} ({'✅' if r['success'] else '❌'})" 
                                   for r in recent_list])
            
            stats = f"""
📊 **Detailed Statistics**

⏱️ **Uptime:**
• Running: {hours}h {mins}m
• Started: {self.stats['started'].strftime('%Y-%m-%d %H:%M')}

📈 **Reports:**
• Total (All-time): {self.stats['total']}
• Today: {self.stats['today_reports']}/50
• Successful: {self.stats['success']} ✅
• Failed: {self.stats['failed']} ❌
• Success Rate: {success_rate:.1f}%

📅 **Daily Limit:**
• Used: {self.stats['today_reports']}/50
• Remaining: {50 - self.stats['today_reports']}
• Resets: Tomorrow 00:00

🕐 **Recent Activity:**
{recent}

💡 Tip: Keep success rate above 80% for optimal performance
            """
            await event.reply(stats)
        
        @self.client.on(events.NewMessage(pattern='/help'))
        async def help_command(event):
            """Show comprehensive help"""
            if not self.is_admin(event.sender_id):
                return
            
            help_text = """
📚 **Complete Command Guide**

**🎯 Single Report:**
`/report @channel spam`
`/report t.me/username fake`

**📋 Bulk Report (NEW!):**
`/bulk spam 50` - Report 50 channels
`/bulk fake` - Report any number

Then send list:
```
@channel1
@channel2
t.me/channel3
```

**⚡ Quick Report:**
Reply to channel message:
• `/spam` - Spam report
• `/fake` - Fake news
• `/violence` - Violence
• `/copyright` - Copyright
• `/porn` - Pornography
• `/drugs` - Illegal drugs

**📊 Information:**
• `/stats` - Detailed statistics
• `/help` - This guide

**📝 Available Reasons:**
`spam`, `violence`, `porn`, `child`, `copyright`, `fake`, `drugs`, `other`

**✨ Features:**
✅ Live progress tracking
✅ Detailed success/fail logs
✅ Smart delay system (7-10s)
✅ Daily limit tracking (50/day)
✅ Comprehensive summaries

**💡 Pro Tips:**
• Wait 8-10 seconds between reports
• Max 50 reports per day recommended
• Check `/stats` regularly
• Keep bot running 24/7 for best results

**Example Workflow:**
1. `/bulk spam 10`
2. Send 10 channel links
3. Watch live progress
4. Get detailed summary

Need help? Check logs for detailed information!
            """
            await event.reply(help_text)
        
        # Quick report commands
        def create_quick_handler(reason_key):
            async def handler(event):
                if not self.is_admin(event.sender_id):
                    return
                if not event.is_reply:
                    await event.reply("⚠️ Please reply to a channel message to report it")
                    return
                
                try:
                    reply = await event.get_reply_message()
                    if reply.peer_id:
                        start_time = datetime.now()
                        entity = await self.client.get_entity(reply.peer_id)
                        channel_name = getattr(entity, 'username', 'Unknown')
                        
                        status = await event.reply(
                            f"⚡ **Quick Report**\n\n"
                            f"🎯 Channel: @{channel_name}\n"
                            f"⚠️ Reason: {self.REASONS[reason_key][0]}\n"
                            f"📊 Status: Processing...\n"
                            f"⏳ Please wait..."
                        )
                        
                        logger.info(f"\n{'─'*70}")
                        logger.info(f"⚡ QUICK REPORT: @{channel_name}")
                        logger.info(f"⚠️ Reason: {self.REASONS[reason_key][0]}")
                        logger.info(f"{'─'*70}")
                        
                        success = await self.report_channel(entity, self.REASONS[reason_key][1])
                        elapsed = (datetime.now() - start_time).total_seconds()
                        
                        if success:
                            logger.info(f"✅ Quick Report SUCCESS ({elapsed:.2f}s)\n")
                            await status.edit(
                                f"✅ **Report Successful!**\n\n"
                                f"🎯 Channel: @{channel_name}\n"
                                f"⚠️ Reason: {self.REASONS[reason_key][0]}\n"
                                f"⏱️ Time: {elapsed:.2f}s\n"
                                f"📊 Total: {self.stats['total']}"
                            )
                        else:
                            logger.info(f"❌ Quick Report FAILED ({elapsed:.2f}s)\n")
                            await status.edit(
                                f"❌ **Report Failed**\n\n"
                                f"🎯 Channel: @{channel_name}\n"
                                f"⚠️ Reason: {self.REASONS[reason_key][0]}\n"
                                f"⏱️ Time: {elapsed:.2f}s\n\n"
                                f"Try again later"
                            )
                        
                except Exception as e:
                    logger.error(f"❌ Quick report error: {str(e)}")
                    await event.reply(f"❌ Error: {str(e)}")
            return handler
        
        # Register quick commands
        for reason_key in ['spam', 'fake', 'violence', 'copyright', 'porn', 'drugs']:
            self.client.on(events.NewMessage(pattern=f'/{reason_key}'))(create_quick_handler(reason_key))
    
    async def report_channel(self, channel, reason_class):
        """Report a single channel with detailed tracking"""
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
            self.stats['today_reports'] += 1
            
            # Track in session
            username = getattr(entity, 'username', 'Unknown')
            
            if result:
                self.stats['success'] += 1
                self.stats['session_reports'].append({
                    'time': datetime.now(),
                    'channel': username,
                    'success': True
                })
                logger.info(f"✅ Report success: @{username}")
                return True
            else:
                self.stats['failed'] += 1
                self.stats['session_reports'].append({
                    'time': datetime.now(),
                    'channel': username,
                    'success': False
                })
                logger.info(f"❌ Report failed: @{username}")
                return False
                
        except Exception as e:
            self.stats['total'] += 1
            self.stats['today_reports'] += 1
            self.stats['failed'] += 1
            logger.error(f"❌ Report error: {str(e)}")
            return False
    
    async def bulk_report_enhanced(self, event, channels, reason_class, progress_msg, delay=8):
        """
        ENHANCED bulk report with detailed live progress tracking
        Updates every single report to keep user informed
        """
        total = len(channels)
        success_count = 0
        failed_count = 0
        success_channels = []
        failed_channels = []
        
        start_time = datetime.now()
        
        # Initial comprehensive message
        logger.info(f"\n{'═'*70}")
        logger.info(f"🚀 BULK REPORT SESSION STARTED")
        logger.info(f"{'═'*70}")
        logger.info(f"📊 Total Channels: {total}")
        logger.info(f"⚠️ Report Reason: {[k for k, v in self.REASONS.items() if v[1] == reason_class][0]}")
        logger.info(f"⏱️ Delay per report: {delay}s")
        logger.info(f"🕐 Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"⏱️ Estimated duration: {total * delay}s ({total * delay // 60}m {total * delay % 60}s)")
        logger.info(f"{'═'*70}\n")
        
        # Update initial message
        await progress_msg.edit(
            f"🚀 **Bulk Report Started!**\n\n"
            f"📊 Total Channels: **{total}**\n"
            f"⏱️ Est. Time: {total * delay // 60}m {total * delay % 60}s\n"
            f"🕐 Started: {start_time.strftime('%H:%M:%S')}\n\n"
            f"{'▱' * 20} 0%\n\n"
            f"⏳ Initializing first report..."
        )
        
        # Process each channel with LIVE updates
        for idx, channel in enumerate(channels, 1):
            current_time = datetime.now()
            elapsed = (current_time - start_time).total_seconds()
            
            # Progress bar
            progress_pct = (idx - 1) / total
            filled = int(progress_pct * 20)
            bar = '▰' * filled + '▱' * (20 - filled)
            
            # Log current report start
            logger.info(f"{'─'*70}")
            logger.info(f"📍 Report #{idx}/{total} ({idx/total*100:.1f}%)")
            logger.info(f"🎯 Channel: {channel}")
            logger.info(f"⏳ Status: Sending report...")
            
            # Update Telegram: Report in progress
            try:
                await progress_msg.edit(
                    f"🔄 **Bulk Report in Progress**\n\n"
                    f"📍 **Current:** [{idx}/{total}] - **{idx/total*100:.1f}%**\n"
                    f"🎯 Reporting: `{channel}`\n\n"
                    f"{bar} {int(progress_pct*100)}%\n\n"
                    f"📊 **Progress:**\n"
                    f"✅ Success: {success_count}\n"
                    f"❌ Failed: {failed_count}\n"
                    f"⏱️ Elapsed: {int(elapsed//60)}m {int(elapsed%60)}s\n\n"
                    f"⏳ Processing report..."
                )
            except:
                pass  # Skip if update too frequent
            
            # REPORT THE CHANNEL
            success = await self.report_channel(channel, reason_class)
            
            # Update stats
            if success:
                success_count += 1
                success_channels.append(channel)
                status_emoji = "✅"
                status_text = "SUCCESS"
                logger.info(f"✅ Result: SUCCESS")
            else:
                failed_count += 1
                failed_channels.append(channel)
                status_emoji = "❌"
                status_text = "FAILED"
                logger.info(f"❌ Result: FAILED")
            
            # Calculate updated stats
            current_success_rate = (success_count / idx) * 100
            avg_time_per_report = elapsed / idx
            remaining_reports = total - idx
            eta_seconds = int(remaining_reports * avg_time_per_report + remaining_reports * delay)
            eta_mins = eta_seconds // 60
            eta_secs = eta_seconds % 60
            
            # Log stats
            logger.info(f"📊 Session Stats: {success_count}✅ {failed_count}❌ | Rate: {current_success_rate:.1f}%")
            logger.info(f"⏱️ Time Stats: {elapsed:.1f}s elapsed | ETA: {eta_mins}m {eta_secs}s")
            
            # Progress bar for completed
            progress_pct = idx / total
            filled = int(progress_pct * 20)
            bar = '▰' * filled + '▱' * (20 - filled)
            
            # Update Telegram with result
            try:
                await progress_msg.edit(
                    f"{status_emoji} **Report #{idx} Complete**\n\n"
                    f"📍 **Progress:** [{idx}/{total}] - **{progress_pct*100:.1f}%**\n"
                    f"🎯 Just reported: `{channel}` - **{status_text}**\n\n"
                    f"{bar} {int(progress_pct*100)}%\n\n"
                    f"📊 **Statistics:**\n"
                    f"✅ Successful: {success_count} ({current_success_rate:.1f}%)\n"
                    f"❌ Failed: {failed_count}\n\n"
                    f"⏱️ **Timing:**\n"
                    f"⏳ Elapsed: {int(elapsed//60)}m {int(elapsed%60)}s\n"
                    f"🕐 ETA: {eta_mins}m {eta_secs}s remaining\n\n"
                    f"{'✅ **ALL COMPLETE!**' if idx == total else f'⏳ Next: Report #{idx+1}/{total}'}"
                )
            except:
                pass  # Skip if message update fails
            
            # Log delay info
            if idx < total:
                logger.info(f"⏸️ Waiting {delay}s before next report...")
                logger.info(f"")  # Empty line for readability
                await asyncio.sleep(delay)
            else:
                logger.info(f"{'─'*70}\n")
        
        # ═══════════════════════════════════════════════════════════
        # FINAL COMPREHENSIVE SUMMARY
        # ═══════════════════════════════════════════════════════════
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        final_success_rate = (success_count / total) * 100
        avg_time = total_duration / total
        
        # Log comprehensive final summary
        logger.info(f"{'═'*70}")
        logger.info(f"✅ BULK REPORT SESSION COMPLETED")
        logger.info(f"{'═'*70}")
        logger.info(f"")
        logger.info(f"📊 SUMMARY:")
        logger.info(f"   • Total Channels: {total}")
        logger.info(f"   • Successful: {success_count} ✅")
        logger.info(f"   • Failed: {failed_count} ❌")
        logger.info(f"   • Success Rate: {final_success_rate:.1f}%")
        logger.info(f"")
        logger.info(f"⏱️ TIMING:")
        logger.info(f"   • Total Duration: {int(total_duration//60)}m {int(total_duration%60)}s")
        logger.info(f"   • Avg per Report: {avg_time:.2f}s")
        logger.info(f"   • Started: {start_time.strftime('%H:%M:%S')}")
        logger.info(f"   • Finished: {end_time.strftime('%H:%M:%S')}")
        logger.info(f"")
        
        # Log successful channels
        if success_channels:
            logger.info(f"✅ SUCCESSFUL REPORTS ({len(success_channels)}):")
            for i, ch in enumerate(success_channels, 1):
                logger.info(f"   {i:3d}. {ch}")
            logger.info(f"")
        
        # Log failed channels
        if failed_channels:
            logger.info(f"❌ FAILED REPORTS ({len(failed_channels)}):")
            for i, ch in enumerate(failed_channels, 1):
                logger.info(f"   {i:3d}. {ch}")
            logger.info(f"")
        
        logger.info(f"{'═'*70}\n")
        
        # Build comprehensive Telegram final message
        final_message = (
            f"✅ **BULK REPORT COMPLETE!**\n\n"
            f"{'▰' * 20} 100%\n\n"
        )
        
        # Summary section
        final_message += (
            f"📊 **SUMMARY:**\n"
            f"• Total: {total} channels\n"
            f"• Successful: {success_count} ✅\n"
            f"• Failed: {failed_count} ❌\n"
            f"• Success Rate: **{final_success_rate:.1f}%**\n\n"
        )
        
        # Timing section
        final_message += (
            f"⏱️ **TIMING:**\n"
            f"• Duration: {int(total_duration//60)}m {int(total_duration%60)}s\n"
            f"• Avg/Report: {avg_time:.2f}s\n"
            f"• Started: {start_time.strftime('%H:%M:%S')}\n"
            f"• Finished: {end_time.strftime('%H:%M:%S')}\n\n"
        )
        
        # Successful channels list (show first 15)
        if success_channels:
            final_message += f"✅ **SUCCESSFUL ({len(success_channels)}):**\n"
            display_success = success_channels[:15]
            for ch in display_success:
                final_message += f"• `{ch}`\n"
            if len(success_channels) > 15:
                final_message += f"• ... and **{len(success_channels) - 15}** more\n"
            final_message += "\n"
        
        # Failed channels list (show all if <= 10, otherwise first 10)
        if failed_channels:
            final_message += f"❌ **FAILED ({len(failed_channels)}):**\n"
            display_failed = failed_channels[:10]
            for ch in display_failed:
                final_message += f"• `{ch}`\n"
            if len(failed_channels) > 10:
                final_message += f"• ... and **{len(failed_channels) - 10}** more\n"
            final_message += "\n"
        
        # Performance indicator
        if final_success_rate >= 90:
            perf_emoji = "🌟"
            perf_text = "Excellent Performance!"
        elif final_success_rate >= 75:
            perf_emoji = "✨"
            perf_text = "Good Performance"
        elif final_success_rate >= 50:
            perf_emoji = "👍"
            perf_text = "Average Performance"
        else:
            perf_emoji = "⚠️"
            perf_text = "Consider retrying failed channels"
        
        final_message += f"{perf_emoji} **{perf_text}**\n\n"
        final_message += f"💡 Use `/stats` for detailed statistics"
        
        # Send final comprehensive message
        await progress_msg.edit(final_message)
        
        # Keep session reports list reasonable
        if len(self.stats['session_reports']) > 100:
            self.stats['session_reports'] = self.stats['session_reports'][-100:]
    
    def clean_channel(self, channel):
        """Clean and validate channel format"""
        channel = channel.strip()
        
        # Remove quotes if present
        channel = channel.strip('"\'')
        
        # Handle various URL formats
        if 'https://t.me/' in channel:
            channel = '@' + channel.split('/')[-1]
        elif 't.me/' in channel:
            channel = '@' + channel.split('/')[-1]
        elif not channel.startswith('@'):
            channel = '@' + channel
        
        # Validate format (basic check)
        if len(channel) < 2 or not channel[1:].replace('_', '').isalnum():
            return None
        
        return channel
    
    async def run(self):
        """Run the bot with graceful error handling"""
        if await self.start():
            logger.info("✅ Enhanced Bot is running!")
            logger.info("💬 Send /start to begin")
            logger.info(f"📊 Progress updates: Every {self.PROGRESS_UPDATE_INTERVAL} report(s)")
            logger.info("🔥 All features enabled!\n")
            
            try:
                await self.client.run_until_disconnected()
            except KeyboardInterrupt:
                logger.info("\n👋 Bot stopped by user")
            except Exception as e:
                logger.error(f"❌ Runtime error: {e}", exc_info=True)
        else:
            logger.error("❌ Failed to start bot - check configuration")


async def main():
    """Main entry point with error handling"""
    try:
        bot = ChannelReporterBot()
        await bot.run()
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        exit(1)
