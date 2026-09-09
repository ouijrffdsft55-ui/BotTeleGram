// bot.js - Chỉ chứa lệnh /hello và /kick
const express = require('express');
const TelegramBot = require('node-telegram-bot-api');
const dotenv = require('dotenv');
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const token = process.env.BOT_TOKEN;

if (!token) {
    console.error('FATAL: BOT_TOKEN chưa được đặt');
    process.exit(1);
}

const bot = new TelegramBot(token, { polling: true });

// ============ LỆNH /HELLO ============
bot.onText(/\/hello/, (msg) => {
    const chatId = msg.chat.id;
    const from = msg.from;
    const firstName = from.first_name || 'bạn';
    const userId = from.id;
    const messageId = msg.message_id;
    
    bot.sendMessage(chatId, `Xin chào <a href="tg://user?id=${userId}">${firstName}</a>! 👋`, {
        parse_mode: 'HTML',
        reply_to_message_id: messageId
    });
});

// ============ LỆNH /KICK ============
bot.onText(/\/kick/, async (msg) => {
    const chatId = msg.chat.id;
    const from = msg.from;
    
    // Kiểm tra nếu có reply_to_message (tag người cần kick)
    if (!msg.reply_to_message) {
        return bot.sendMessage(chatId, '❌ Vui lòng reply vào tin nhắn của người cần kick và gõ /kick');
    }
    
    const targetId = msg.reply_to_message.from.id;
    const targetName = msg.reply_to_message.from.first_name || 'người dùng';
    
    try {
        // Kiểm tra bot có quyền admin
        const botMember = await bot.getChatMember(chatId, bot.options.username);
        if (!botMember.can_restrict_members) {
            return bot.sendMessage(chatId, '❌ Bot cần quyền admin để kick thành viên.');
        }
        
        // Kiểm tra người dùng có quyền admin
        const userMember = await bot.getChatMember(chatId, from.id);
        if (!userMember.can_restrict_members && userMember.status !== 'creator') {
            return bot.sendMessage(chatId, '❌ Bạn cần quyền admin để sử dụng lệnh này.');
        }
        
        // Thực hiện kick
        await bot.kickChatMember(chatId, targetId);
        await bot.sendMessage(chatId, `✅ Đã kick <a href="tg://user?id=${targetId}">${targetName}</a> khỏi nhóm.`, {
            parse_mode: 'HTML'
        });
        
        // Unban để cho phép họ tham gia lại sau (nếu muốn)
        await bot.unbanChatMember(chatId, targetId);
        
    } catch (error) {
        bot.sendMessage(chatId, `❌ Lỗi: ${error.message}`);
    }
});

// ============ SERVER EXPRESS ============
app.get('/', (req, res) => {
    res.send('Bot đang chạy...');
});

app.listen(PORT, () => {
    console.log(`✅ Server đang chạy trên port ${PORT}`);
    console.log(`✅ Bot đã khởi động với lệnh /hello và /kick`);
});
