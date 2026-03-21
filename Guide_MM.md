# Facebook Page Messenger အတွက် AI Auto Reply Bot တည်ဆောက်ခြင်း လမ်းညွှန်

Facebook Page တွင် Customer များ၏ မေးမြန်းချက်များကို AI (OpenAI GPT) အသုံးပြု၍ အလိုအလျောက် ဖြေကြားပေးနိုင်သော Auto Reply Bot တစ်ခု တည်ဆောက်ရန်အတွက် လိုအပ်သော အဆင့်များကို အောက်ပါအတိုင်း အသေးစိတ် ရှင်းလင်းထားပါသည်။

## အပိုင်း (၁): Meta Developer Account နှင့် App ဖန်တီးခြင်း

Facebook Page ၏ Messenger ကို AI နှင့် ချိတ်ဆက်ရန် **Meta Developer Account** လိုအပ်ပါသည်။

၁။ [Meta for Developers](https://developers.facebook.com/) သို့ သွား၍ သင်၏ Facebook Account ဖြင့် Log in ဝင်ပါ။
၂။ ညာဘက်အပေါ်ထောင့်ရှိ **"My Apps"** (သို့မဟုတ် Get Started) ကို နှိပ်ပါ။
၃။ **"Create App"** ခလုတ်ကို နှိပ်ပါ။
၄။ App Type ရွေးချယ်ရန် ပေါ်လာပါက **"Other"** ကို ရွေးချယ်ပြီး Next နှိပ်ပါ။ ထို့နောက် **"Business"** ကို ရွေးချယ်ပါ။
၅။ App Name နေရာတွင် သင်၏ Bot နာမည် (ဥပမာ - "My Page AI Bot") ကို ထည့်ပါ။ App Contact Email ထည့်သွင်းပြီး **"Create app"** ကို နှိပ်ပါ။
၆။ App ဖန်တီးပြီးပါက App Dashboard သို့ ရောက်ရှိသွားပါမည်။

## အပိုင်း (၂): Messenger Product ထည့်သွင်းခြင်း

၁။ App Dashboard ၏ အောက်ဘက်ရှိ **"Add products to your app"** အပိုင်းတွင် **"Messenger"** ကို ရှာ၍ **"Set up"** ကို နှိပ်ပါ။
၂။ ဘယ်ဘက် Menu တွင် Messenger အောက်ရှိ **"Messenger API Settings"** သို့ ရောက်သွားပါမည်။

## အပိုင်း (၃): Facebook Page ချိတ်ဆက်ခြင်း နှင့် Access Token ရယူခြင်း

၁။ Messenger Settings စာမျက်နှာရှိ **"Access Tokens"** အပိုင်းတွင် **"Add or Remove Pages"** ခလုတ်ကို နှိပ်ပါ။
၂။ သင်၏ Facebook Page ကို ရွေးချယ်၍ ချိတ်ဆက် (Connect) ပါ။
၃။ ချိတ်ဆက်ပြီးပါက Page အမည်ဘေးရှိ **"Generate Token"** ခလုတ်ကို နှိပ်ပါ။
၄။ ထွက်လာသော **Page Access Token** အရှည်ကြီးကို Copy ကူး၍ လုံခြုံသောနေရာတွင် မှတ်ထားပါ။ (Bot Code ထဲတွင် အသုံးပြုရန် ဖြစ်သည်)

## အပိုင်း (၄): Bot Code ကို Server တွင် Run ခြင်း (သို့မဟုတ် Local တွင် Run ခြင်း)

Webhooks ချိတ်ဆက်ရန်အတွက် သင်၏ Bot Code သည် အင်တာနက်ပေါ်တွင် အလုပ်လုပ်နေသော (Public URL ရှိသော) Server တစ်ခု လိုအပ်ပါသည်။ 

*မှတ်ချက် - ဤလမ်းညွှန်တွင်ပါသော Code များသည် Python (Flask) ဖြင့် ရေးသားထားပါသည်။*

၁။ ပေးထားသော Code Folder (`fb-messenger-ai-bot`) ကို သင်၏ Server (ဥပမာ - Render, Railway, Heroku သို့မဟုတ် ကိုယ်ပိုင် VPS) သို့ တင်ပါ။
၂။ Environment Variables (`.env`) များကို အောက်ပါအတိုင်း သတ်မှတ်ပါ-
   - `PAGE_ACCESS_TOKEN` = အပိုင်း (၃) တွင် ရရှိခဲ့သော Token
   - `VERIFY_TOKEN` = "my_verify_token_123" (သင်ကြိုက်ရာ ပြောင်းနိုင်သည်)
   - `OPENAI_API_KEY` = သင်၏ OpenAI API Key
၃။ Server ကို Run လိုက်ပါ။ သင်၏ Server URL (ဥပမာ - `https://my-ai-bot.onrender.com`) ကို မှတ်ထားပါ။

## အပိုင်း (၅): Webhook ချိတ်ဆက်ခြင်း

Facebook မှ Message ဝင်လာတိုင်း သင်၏ Server သို့ လာရောက်ပြောကြားရန် Webhook ချိတ်ဆက်ရပါမည်။

၁။ Meta Developer Dashboard ရှိ Messenger Settings စာမျက်နှာသို့ ပြန်သွားပါ။
၂။ **"Webhooks"** အပိုင်းကို ရှာ၍ **"Add Callback URL"** ကို နှိပ်ပါ။
၃။ **Callback URL** နေရာတွင် သင်၏ Server URL အနောက်တွင် `/webhook` ထည့်၍ ရေးပါ (ဥပမာ - `https://my-ai-bot.onrender.com/webhook`)။
၄။ **Verify Token** နေရာတွင် အပိုင်း (၄) တွင် သတ်မှတ်ခဲ့သော Token (ဥပမာ - "my_verify_token_123") ကို ထည့်ပါ။
၅။ **"Verify and Save"** ကို နှိပ်ပါ။ (Server Run နေမှသာ အောင်မြင်ပါမည်)
၆။ အောင်မြင်သွားပါက Webhook အပိုင်းရှိ **"Manage"** (သို့မဟုတ် Add Subscriptions) ကို နှိပ်ပြီး **`messages`** နှင့် **`messaging_postbacks`** ကို အမှန်ခြစ် (Tick) ပေးပါ။

## အပိုင်း (၆): Bot ကို စမ်းသပ်ခြင်း

၁။ သင်၏ Facebook Page သို့ သွား၍ သာမန် User တစ်ယောက်အနေဖြင့် Message ပို့ကြည့်ပါ။
၂။ AI မှ အလိုအလျောက် ပြန်လည်ဖြေကြားပေးမည် ဖြစ်ပါသည်။
၃။ Bot ၏ အဖြေပုံစံကို ပြောင်းလဲလိုပါက Code ထဲရှိ `SYSTEM_PROMPT` ကို ပြင်ဆင်နိုင်ပါသည်။

---

### အရေးကြီးသော မှတ်ချက်များ

- **App Review:** လက်ရှိအချိန်တွင် Bot သည် သင်၏ Developer Account နှင့် Page Admin များကိုသာ ဖြေကြားပေးမည် ဖြစ်ပါသည်။ အခြားသော Public User များအားလုံးကို ဖြေကြားပေးနိုင်ရန် App Dashboard မှတစ်ဆင့် **"App Review"** တင်ရန် လိုအပ်ပါသည်။
- **pages_messaging Permission:** App Review တင်ရာတွင် `pages_messaging` permission ကို တောင်းခံရပါမည်။
- **OpenAI Usage:** OpenAI API အသုံးပြုမှုအတွက် ကုန်ကျစရိတ် (Credits) ရှိနိုင်ပါသည်။

*လိုအပ်သော Code များကို `fb-messenger-ai-bot` ဖိုင်တွဲ (Folder) အတွင်းတွင် အပြည့်အစုံ ရေးသားပေးထားပါသည်။*
