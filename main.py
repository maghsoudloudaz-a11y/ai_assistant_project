from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from datetime import datetime
import json
import os
import random
from typing import Dict
import requests

app = FastAPI(title="AI Assistant Pro", version="7.5")  # نسخه آپدیت شده

DATA_FILE = "memory.json"
DEEPSEEK_API_KEY = "sk-4d03f4a7973b443b8f9aff41fa139ab5"

# سیستم حافظه
def load_data():
    default_data = {
        "last_visitor": "", 
        "total_visits": 0,
        "visit_history": [],
        "user_profiles": {},
        "language": "persian",
        "content_history": [],
        "chat_history": []
    }
    
    if not os.path.exists(DATA_FILE):
        save_data(default_data)
        return default_data
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for key in default_data:
                if key not in data:
                    data[key] = default_data[key]
            return data
    except Exception:
        return default_data

def save_data(data: Dict):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# سیستم هوش مصنوعی پیشرفته + DeepSeek
class AdvancedAI:
    def __init__(self, deepseek_api_key: str):
        self.deepseek_api_key = deepseek_api_key
        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"
        self.translations = {
            "persian": {
                "greetings": [
                    "سلام {name}! خوش اومدی 👋",
                    "درود {name}! چطور می‌تونم کمک کنم؟",
                    "عه {name}! خوشحالم می‌بینمت 😊"
                ],
                "content_types": {
                    "instagram": "پست اینستاگرام",
                    "email": "ایمیل",
                    "story": "داستان کوتاه", 
                    "poem": "شعر",
                    "idea": "ایده خلاقانه",
                    "code": "کد برنامه‌نویسی",
                    "article": "مقاله کوتاه",
                    "advice": "مشاوره تخصصی"
                }
            },
            "english": {
                "greetings": [
                    "Hello {name}! Welcome 👋",
                    "Hi {name}! How can I help you?",
                    "Hey {name}! Nice to see you 😊"
                ],
                "content_types": {
                    "instagram": "Instagram Post",
                    "email": "Email",
                    "story": "Short Story",
                    "poem": "Poem",
                    "idea": "Creative Idea",
                    "code": "Programming Code",
                    "article": "Short Article",
                    "advice": "Expert Advice"
                }
            },
            "turkish": {
                "greetings": [
                    "Merhaba {name}! Hoş geldin 👋",
                    "Selam {name}! Nasıl yardımcı olabilirim?",
                    "Ayy {name}! Seni görmek güzel 😊"
                ],
                "content_types": {
                    "instagram": "Instagram Gönderisi",
                    "email": "E-posta",
                    "story": "Kısa Hikaye",
                    "poem": "Şiir",
                    "idea": "Yaratıcı Fikir",
                    "code": "Programlama Kodu",
                    "article": "Kısa Makale",
                    "advice": "Uzman Tavsiyesi"
                }
            },
            "arabic": {
                "greetings": [
                    "مرحباً {name}! أهلاً وسهلاً 👋",
                    "سلام {name}! كيف يمكنني مساعدتك؟",
                    "أهلا {name}! يسعدني رؤيتك 😊"
                ],
                "content_types": {
                    "instagram": "منشور إنستغرام",
                    "email": "بريد إلكتروني",
                    "story": "قصة قصيرة",
                    "poem": "قصيدة",
                    "idea": "فكرة إبداعية",
                    "code": "كود برمجة",
                    "article": "مقالة قصيرة",
                    "advice": "نصيحة خبيرة"
                }
            }
        }
    
    def get_greeting(self, name: str, language: str = "persian") -> str:
        lang_data = self.translations.get(language, self.translations["persian"])
        return random.choice(lang_data["greetings"]).format(name=name)
    
    def get_system_prompt(self, language: str) -> str:
        """سیستم پرامپت برای هر زبان"""
        prompts = {
            "persian": "شما یک دستیار هوشمند و مفید هستید که به زبان فارسی پاسخ می‌دهید. پاسخ‌های کامل و مفید ارائه دهید.",
            "english": "You are a helpful and intelligent assistant that responds in English. Provide complete and helpful responses.",
            "turkish": "Türkçe yanıt veren yardımsever ve akıllı bir asistansınız. Eksiksiz ve yardımcı yanıtlar verin.",
            "arabic": "أنت مساعد ذكي ومفيد يرد باللغة العربية. قدم ردودًا كاملة ومفيدة."
        }
        return prompts.get(language, prompts["persian"])
    
    def deepseek_chat(self, message: str, language: str = "persian") -> str:
        """اتصال به DeepSeek API برای پاسخ‌های هوشمند"""
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            system_message = self.get_system_prompt(language)
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 8000,  # افزایش به 8000 توکن برای محتوای طولانی
                "stream": False
            }
            
            response = requests.post(self.deepseek_url, json=data, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"DeepSeek Error: {e}")
            return None
    
    def smart_chat(self, message: str, language: str = "persian") -> str:
        """سیستم چت ترکیبی: اول DeepSeek، سپس سیستم قدیمی"""
        
        # اول سعی کن از DeepSeek جواب بگیری
        deepseek_response = self.deepseek_chat(message, language)
        if deepseek_response:
            return deepseek_response
        
        # اگر DeepSeek جواب نداد، از سیستم قدیمی استفاده کن
        message_lower = message.lower()
        
        responses = {
            "persian": {
                "introduction": """🤖 **دستیار هوشمند پیشرفته نسخه 7.5**

سلام! من یک دستیار هوشمند هستم که با FastAPI و Python ساخته شدم و از DeepSeek قدرت گرفته‌ام!

**قابلیت‌های من:**
• 💬 چت هوشمند با قابلیت درک کامل
• 💻 تولید کد برنامه‌نویسی (پایتون، جاوااسکریپت، HTML)
• 📝 نوشتن مقاله، داستان، شعر و محتوای متنی
• 🎨 تولید پست اینستاگرام و ایمیل
• 💼 مشاوره کسب‌وکار و استارتاپ
• 🌍 پشتیبانی از ۴ زبان (فارسی، انگلیسی، ترکی، عربی)
• 🧠 حافظه و تاریخچه مکالمات

**چطور می‌تونم کمک کنم؟**""",
                "programming": "💻 **بخش برنامه‌نویسی**\nمی‌تونم کدهای پایتون، جاوااسکریپت و HTML براتون بنویسم. چه پروژه‌ای در نظر دارید؟",
                "content": "📝 **بخش تولید محتوا**\nمی‌تونم مقاله، پست اینستاگرام، داستان، شعر و ایده‌های خلاقانه تولید کنم. چه نوع محتوایی نیاز دارید؟",
                "business": "💼 **بخش مشاوره**\nمی‌تونم در زمینه کسب‌وکار، استارتاپ و بازاریابی راهنماییتون کنم.",
                "stats": self.get_system_stats,
                "capabilities": "🚀 **قابلیت‌های کامل:**\n• چت هوشمند با DeepSeek\n• کدنویسی حرفه‌ای\n• تولید محتوا\n• مشاوره تخصصی\n• پشتیبانی ۴ زبانه\n• سیستم حافظه شخصی\n\nچه کاری براتون انجام بدم؟",
                "default": "🤔 سوال جالبی پرسیدید! با قابلیت جدید DeepSeek می‌تونم به صورت هوشمند به سوالاتتون پاسخ بدم."
            }
        }
        
        lang_responses = responses.get(language, responses["persian"])
        
        if any(word in message_lower for word in ["خودتو", "معرفی", "کی هستی", "تو کی", "چه کار", "کارایی", "قابلیت"]):
            return lang_responses["introduction"]
        elif any(word in message_lower for word in ["کد", "برنامه", "پایتون", "جاوااسکریپت", "html", "کدنویسی"]):
            return lang_responses["programming"]
        elif any(word in message_lower for word in ["محتوا", "مقاله", "نوشتن", "داستان", "شعر", "پست"]):
            return lang_responses["content"]
        elif any(word in message_lower for word in ["کسب‌وکار", "بیزینس", "استارتاپ", "مشاوره"]):
            return lang_responses["business"]
        elif any(word in message_lower for word in ["آمار", "stat", "تعداد", "کاربر"]):
            return lang_responses["stats"]()
        elif any(word in message_lower for word in ["چه کار", "چیکار", "توانایی", "قابلیت"]):
            return lang_responses["capabilities"]
        else:
            return lang_responses["default"]
    
    def get_system_stats(self) -> str:
        """آمار سیستم"""
        data = load_data()
        return f"""📊 **آمار سیستم:**

• 👥 تعداد کل بازدیدها: {data.get('total_visits', 0)}
• 💬 تعداد مکالمات: {len(data.get('chat_history', []))}
• 📝 محتوای تولید شده: {len(data.get('content_history', []))}
• 👤 کاربران منحصر به فرد: {len(data.get('user_profiles', {}))}
• 🌍 زبان‌های پشتیبانی: فارسی، انگلیسی، ترکی، عربی

**وضعیت:** ✅ فعال با قابلیت DeepSeek"""
    
    def generate_advanced_content(self, content_type: str, topic: str, language: str = "persian") -> Dict:
        """تولید محتوای پیشرفته"""
        
        # اول سعی کن از DeepSeek استفاده کنی
        prompt = f"لطفا یک {self.translations[language]['content_types'][content_type]} درباره {topic} بنویسید. محتوای کامل و مفید ارائه دهید."
        deepseek_content = self.deepseek_chat(prompt, language)
        
        if deepseek_content:
            return {
                "content_type": self.translations[language]["content_types"][content_type],
                "topic": topic,
                "generated_content": deepseek_content,
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "source": "deepseek"
            }
        
        # اگر DeepSeک جواب نداد، از سیستم قدیمی استفاده کن
        templates = {
            "code": {
                "persian": [f"""کد پایتون برای {topic}:

```python
def main():
    print("سلام دنیا! این کد برای {topic} هست")
    return "موفقیت آمیز"

if __name__ == "__main__":
    main()
```"""],
                "english": [f"""Python code for {topic}:

```python
def main():
    print("Hello World! This code is for {topic}")
    return "Success"

if __name__ == "__main__":
    main()
```"""]
            },
            "article": {
                "persian": [f"""مقاله درباره {topic}

# {topic} - بررسی جامع

این مقاله به بررسی موضوع {topic} می‌پردازد. {topic} یکی از موضوعات مهم در دنیای امروز است.

## نتیجه‌گیری
{topic} می‌تواند تاثیر زیادی بر آینده داشته باشد."""],
                "english": [f"""Article about {topic}

# {topic} - Comprehensive Analysis

This article examines the topic of {topic}. {topic} is one of the important subjects in today's world.

## Conclusion
{topic} can have a significant impact on the future."""]
            }
        }
        
        content_list = templates.get(content_type, {}).get(language, [f"محتوای {content_type} درباره {topic}"])
        generated_content = random.choice(content_list) if content_list else f"محتوای {content_type} درباره {topic}"
        
        return {
            "content_type": self.translations[language]["content_types"][content_type],
            "topic": topic,
            "generated_content": generated_content,
            "language": language,
            "timestamp": datetime.now().isoformat(),
            "source": "fallback"
        }

# ایجاد نمونه AI
advanced_ai = AdvancedAI(DEEPSEEK_API_KEY)

# 🔥 رابط کاربری اصلی
@app.get("/", response_class=HTMLResponse)
def read_ui():
    return """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>AI Assistant Pro v7.5 - 4 Languages</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
            }
            .container {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 {
                color: #4a5568;
                text-align: center;
                margin-bottom: 30px;
            }
            .tab-container {
                display: flex;
                margin-bottom: 20px;
                border-bottom: 2px solid #e2e8f0;
                flex-wrap: wrap;
            }
            .tab {
                padding: 12px 20px;
                cursor: pointer;
                border: none;
                background: none;
                font-size: 14px;
                border-bottom: 3px solid transparent;
            }
            .tab.active {
                border-bottom: 3px solid #4a5568;
                font-weight: bold;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }
            .input-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            input, select, button, textarea {
                width: 100%;
                padding: 12px;
                margin: 5px 0;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 16px;
                box-sizing: border-box;
            }
            button {
                background: #4a5568;
                color: white;
                border: none;
                cursor: pointer;
                transition: background 0.3s;
            }
            button:hover {
                background: #2d3748;
            }
            .result {
                background: #f7fafc;
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
                border-right: 4px solid #4a5568;
                white-space: pre-line;
            }
            .code-block {
                background: #2d3748;
                color: #e2e8f0;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
                overflow-x: auto;
                font-family: 'Courier New', monospace;
            }
            .ai-badge {
                background: #48bb78;
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                margin-right: 8px;
            }
            .language-badge {
                background: #ed8936;
                color: white;
                padding: 2px 6px;
                border-radius: 8px;
                font-size: 10px;
                margin-right: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI Assistant Pro v7.5 
                <span class="ai-badge">DeepSeek</span>
                <span class="language-badge">4 Languages</span>
            </h1>
            
            <div class="tab-container">
                <button class="tab active" onclick="openTab('chat')">💬 Smart Chat</button>
                <button class="tab" onclick="openTab('code')">💻 Code</button>
                <button class="tab" onclick="openTab('content')">📝 Content</button>
                <button class="tab" onclick="openTab('api')">🔧 APIs</button>
            </div>
            
            <!-- تب چت -->
            <div id="chat" class="tab-content active">
                <div class="input-group">
                    <label>Your Message:</label>
                    <textarea id="chatMessage" rows="3" placeholder="Ask me anything..."></textarea>
                </div>
                
                <div class="input-group">
                    <label>Language:</label>
                    <select id="chatLanguage">
                        <option value="persian">🇮🇷 فارسی (Persian)</option>
                        <option value="english">🇺🇸 English</option>
                        <option value="turkish">🇹🇷 Türkçe (Turkish)</option>
                        <option value="arabic">🇸🇦 العربية (Arabic)</option>
                    </select>
                </div>
                
                <button onclick="smartChat()">💬 Send Message</button>
                <div id="chatResult" class="result"></div>
            </div>
            
            <!-- تب کد -->
            <div id="code" class="tab-content">
                <div class="input-group">
                    <label>Code Topic:</label>
                    <input type="text" id="codeTopic" placeholder="e.g., calculator, sorting, website...">
                </div>
                
                <div class="input-group">
                    <label>Language:</label>
                    <select id="codeLanguage">
                        <option value="persian">🇮🇷 فارسی (Persian)</option>
                        <option value="english">🇺🇸 English</option>
                        <option value="turkish">🇹🇷 Türkçe (Turkish)</option>
                        <option value="arabic">🇸🇦 العربية (Arabic)</option>
                    </select>
                </div>
                
                <button onclick="generateCode()">💻 Generate Python Code</button>
                <div id="codeResult" class="result"></div>
            </div>
            
            <!-- تب محتوا -->
            <div id="content" class="tab-content">
                <div class="input-group">
                    <label>Content Type:</label>
                    <select id="contentType">
                        <option value="article">Article</option>
                        <option value="instagram">Instagram Post</option>
                        <option value="email">Email</option>
                        <option value="advice">Advice</option>
                        <option value="story">Short Story</option>
                        <option value="poem">Poem</option>
                    </select>
                </div>
                
                <div class="input-group">
                    <label>Topic:</label>
                    <input type="text" id="contentTopic" placeholder="e.g., AI, programming...">
                </div>
                
                <div class="input-group">
                    <label>Language:</label>
                    <select id="contentLanguage">
                        <option value="persian">🇮🇷 فارسی (Persian)</option>
                        <option value="english">🇺🇸 English</option>
                        <option value="turkish">🇹🇷 Türkçe (Turkish)</option>
                        <option value="arabic">🇸🇦 العربية (Arabic)</option>
                    </select>
                </div>
                
                <button onclick="generateContent()">🎨 Generate Content</button>
                <div id="contentResult" class="result"></div>
            </div>
            
            <!-- تب API -->
            <div id="api" class="tab-content">
                <div style="display: grid; gap: 10px;">
                    <a href="/docs" style="display: block; background: #edf2f7; padding: 15px; border-radius: 8px; text-decoration: none; color: #4a5568; text-align: center;">
                        📚 Full API Documentation
                    </a>
                    <a href="/api/stats" style="display: block; background: #edf2f7; padding: 15px; border-radius: 8px; text-decoration: none; color: #4a5568; text-align: center;">
                        📊 System Statistics
                    </a>
                    <a href="/api/languages" style="display: block; background: #edf2f7; padding: 15px; border-radius: 8px; text-decoration: none; color: #4a5568; text-align: center;">
                        🌍 Supported Languages
                    </a>
                </div>
            </div>
        </div>

        <script>
            function openTab(tabName) {
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                document.getElementById(tabName).classList.add('active');
                event.currentTarget.classList.add('active');
            }
            
            async function smartChat() {
                const message = document.getElementById('chatMessage').value;
                const language = document.getElementById('chatLanguage').value;
                
                if (!message) {
                    alert('Please enter your message');
                    return;
                }
                
                try {
                    document.getElementById('chatResult').innerHTML = '⏳ Processing with DeepSeek...';
                    
                    const response = await fetch(`/api/advanced/chat?message=${encodeURIComponent(message)}&language=${language}`);
                    
                    if (!response.ok) {
                        throw new Error('Server connection error');
                    }
                    
                    const data = await response.json();
                    document.getElementById('chatResult').innerHTML = `
                        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <strong>👤 You:</strong> ${message}
                        </div>
                        <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <strong>🤖 Assistant:</strong> ${data.response}
                        </div>
                        <small style="color: #666;">🕒 ${new Date().toLocaleTimeString()}</small>
                    `;
                    
                } catch (error) {
                    document.getElementById('chatResult').innerHTML = `
                        <div style="color: red; background: #ffebee; padding: 10px; border-radius: 5px;">
                            ❌ Error: ${error.message}
                        </div>
                    `;
                }
            }
            
            async function generateCode() {
                const topic = document.getElementById('codeTopic').value;
                const language = document.getElementById('codeLanguage').value;
                
                if (!topic) {
                    alert('Please enter code topic');
                    return;
                }
                
                try {
                    document.getElementById('codeResult').innerHTML = '⏳ Generating code with DeepSeek...';
                    
                    const response = await fetch(`/api/generate-content/code?topic=${encodeURIComponent(topic)}&language=${language}`);
                    const data = await response.json();
                    
                    let codeContent = data.generated_content;
                    // پاک کردن markdown code blocks
                    codeContent = codeContent.replace(/```python|```/g, '');
                    
                    document.getElementById('codeResult').innerHTML = `
                        <h4>💻 Python Code for "${topic}"</h4>
                        <div class="code-block">${codeContent}</div>
                        <small>Source: ${data.source === 'deepseek' ? 'DeepSeek AI' : 'Backup System'}</small>
                    `;
                    
                } catch (error) {
                    document.getElementById('codeResult').innerHTML = `<div style="color: red;">❌ Error generating code</div>`;
                }
            }
            
            async function generateContent() {
                const contentType = document.getElementById('contentType').value;
                const topic = document.getElementById('contentTopic').value;
                const language = document.getElementById('contentLanguage').value;
                
                if (!topic) {
                    alert('Please enter content topic');
                    return;
                }
                
                try {
                    document.getElementById('contentResult').innerHTML = '⏳ Generating content with DeepSeek...';
                    
                    const response = await fetch(`/api/generate-content/${contentType}?topic=${encodeURIComponent(topic)}&language=${language}`);
                    const data = await response.json();
                    
                    document.getElementById('contentResult').innerHTML = `
                        <h4>📝 ${data.content_type} - "${topic}"</h4>
                        <div style="background: white; padding: 15px; border-radius: 5px; border: 1px solid #ddd; white-space: pre-line;">
                            ${data.generated_content}
                        </div>
                        <small>Source: ${data.source === 'deepseek' ? 'DeepSeek AI' : 'Backup System'}</small>
                    `;
                    
                } catch (error) {
                    document.getElementById('contentResult').innerHTML = `<div style="color: red;">❌ Error generating content</div>`;
                }
            }
        </script>
    </body>
    </html>
    """

# APIهای اصلی
@app.get("/api/advanced/chat")
def smart_chat(message: str, language: str = "persian"):
    response = advanced_ai.smart_chat(message, language)
    
    data = load_data()
    data["chat_history"].append({
        "user_message": message,
        "ai_response": response,
        "language": language,
        "timestamp": datetime.now().isoformat()
    })
    save_data(data)
    
    return {
        "user_message": message,
        "response": response,
        "language": language,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/generate-content/{content_type}")
def generate_content(content_type: str, topic: str, language: str = "persian"):
    valid_types = ["instagram", "email", "story", "poem", "idea", "code", "article", "advice"]
    if content_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid content type")
    
    content_result = advanced_ai.generate_advanced_content(content_type, topic, language)
    
    data = load_data()
    data["content_history"].append(content_result)
    save_data(data)
    
    return content_result

@app.get("/api/stats")
def get_stats():
    data = load_data()
    return {
        "total_visits": data.get("total_visits", 0),
        "total_users": len(data.get("user_profiles", {})),
        "total_content": len(data.get("content_history", [])),
        "total_chats": len(data.get("chat_history", [])),
        "ai_provider": "DeepSeek AI",
        "supported_languages": ["persian", "english", "turkish", "arabic"],
        "status": "Active",
        "version": "7.5"
    }

@app.get("/api/languages")
def list_languages():
    return {
        "supported_languages": [
            {"code": "persian", "name": "فارسی (Persian)", "flag": "🇮🇷"},
            {"code": "english", "name": "English", "flag": "🇺🇸"},
            {"code": "turkish", "name": "Türkçe (Turkish)", "flag": "🇹🇷"},
            {"code": "arabic", "name": "العربية (Arabic)", "flag": "🇸🇦"}
        ],
        "default_language": "persian",
        "ai_capabilities": "Smart chat, code generation, content creation, advice"
    }

# middleware برای ثبت بازدیدها
@app.middleware("http")
async def track_visits(request, call_next):
    data = load_data()
    data["total_visits"] = data.get("total_visits", 0) + 1
    data["visit_history"].append({
        "path": request.url.path,
        "timestamp": datetime.now().isoformat(),
        "method": request.method
    })
    save_data(data)
    
    response = await call_next(request)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)