# Twilio SMS & WhatsApp Bot Setup

Our FastAPI backend now has a built-in webhook (`POST /sms`) designed to process incoming messages from Twilio and respond via text message. 

To connect this to a real phone number so you can text your AI agent, follow these steps.

## 1. Create a Twilio Account
1. Go to [Twilio.com](https://www.twilio.com/) and sign up for a free trial account.
2. Verify your email and personal phone number (Twilio requires this to prevent spam on free accounts).
3. On the console dashboard, click **"Get a trial phone number"**. Twilio will assign you a free temporary US phone number.

## 2. Deploy the Updates
Before Twilio can talk to your bot, the new `/sms` endpoint needs to be live on your server.
1. Commit the changes we just made to `main.py` and `requirements.txt`.
2. Push them to GitHub.
3. Railway will automatically detect the new commit and rebuild your FastAPI app. Wait for the deploy to finish.

## 3. Connect the Webhook (SMS)
1. Go back to your Twilio Console.
2. Navigate to **Phone Numbers** > **Manage** > **Active numbers**.
3. Click on your newly assigned Twilio phone number.
4. Scroll down to the **"Messaging"** section.
5. Find the setting that says **"A MESSAGE COMES IN"**.
6. Change the dropdown to **Webhook**.
7. Paste your Railway API URL with the new `/sms` path appended. 
   - *Example:* `https://week2-agentforge-production-abcd.up.railway.app/sms`
8. Set the HTTP method to **HTTP POST**.
9. Click **Save** at the bottom of the page.

## 4. Test It Out!
Pull out your actual cell phone and send a text message to your Twilio phone number:
> *"Hi! Is it safe to take ibuprofen and aspirin at the same time?"*

Within a few seconds, Twilio will forward that text to your Railway API, the LangChain agent will process it, and you'll receive a text message back from your AI assistant!

---

## Bonus: WhatsApp Setup
Twilio also allows you to hook this exact same endpoint up to WhatsApp using their "WhatsApp Sandbox".
1. In the Twilio Console, go to **Messaging** > **Try it out** > **Send a WhatsApp message**.
2. Follow the on-screen instructions to join the Sandbox (usually sending a specific code like `join [word]` to their WhatsApp number).
3. Go to the **Sandbox settings** tab.
4. Set the **"WHEN A MESSAGE COMES IN"** URL to your exact same Railway `/sms` URL.
5. Save, and now you can chat with your agent via WhatsApp!