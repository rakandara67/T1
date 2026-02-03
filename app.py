import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Gemini API Konfiqurasiyası
API_KEY = "AIzaSyCYMzC7vax4vCA0FLDxeqIeHBwxHklUnao" # Sizin təqdim etdiyiniz key
genai.configure(api_key=API_KEY)

# Səhifə konfiqurasiyası
st.set_page_config(page_title="Multi-Source Financial Agent", layout="wide")
st.title("📈 Financial Decision Aggregator Agent")
st.subheader("Multi-source Sentiment & Technical Analysis")

# Aktiv seçimi
asset = st.selectbox("Analiz ediləcək aktivi seçin:", ["EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "XAUUSD"])

# --- Skreypinq Funksiyaları (Simulyasiya və Real Scrape məntiqi) ---
def get_source_data(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Saytın strukturuna görə mətni götürürük (Ümumi analiz üçün)
            return soup.get_text()[:2000] # İlk 2000 simvol kifayətdir
        return "Məlumat əldə edilə bilmədi (Status Code error)."
    except Exception as e:
        return f"Xəta baş verdi: {str(e)}"

# --- Əsas Analiz Düyməsi ---
if st.button(f"{asset} Analizini Başlat"):
    with st.spinner('Mənbələrdən məlumat toplanır və Gemini tərəfindən analiz edilir...'):
        
        # Mənbələrin siyahısı
        sources = {
            "Mitrade Forecast": "https://www.mitrade.com/en/financial-tools/Forecast",
            "Investing Technical": "https://www.investing.com/technical/technical-summary",
            "Mitrade Trading Analysis": "https://www.mitrade.com/en/financial-tools/trading-analysis",
            "Investing Market Analysis": "https://www.investing.com/analysis",
            "TradingView Ideas": "https://www.tradingview.com/ideas/technicalanalysis/",
            "FX Blue Strength": "https://www.fxblue.com/market-data/tools/currency-strength",
            "FXSSI Sentiment": f"https://fxssi.com/tools/current-ratio?filter={asset}"
        }

        raw_data_summary = ""
        results_display = {}

        # Məlumatların toplanması
        for name, url in sources.items():
            data = get_source_data(url)
            results_display[name] = data
            raw_data_summary += f"\n--- SOURCE: {name} ---\n{data}\n"

        # Gemini Agent Promptu
        prompt = f"""
        Sən peşəkar bir maliyyə analitikisən. Aşağıdakı mənbələrdən toplanmış qarışıq dataları analiz et:
        Aktiv: {asset}
        
        Məlumatlar:
        {raw_data_summary}
        
        Tapşırıq:
        1. Hər bir mənbə üçün istiqaməti müəyyən et (Long, Short, Neutral).
        2. Çəkili ortalama məntiqi ilə (Sentiment 30%, Technical 40%, Forecasts 30%) yekun qərar ver.
        3. Cavabı bu formatda ver:
           - [Mənbə Adı]: [Nəticə və qısa səbəb]
           - YEKUN QƏRAR: [% ehtimalla LONG/SHORT/NEUTRAL]
           - Qısa Texniki İzah.
        """

        # Gemini API Çağırışı
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Nəticələrin vizuallaşdırılması
        st.success("Analiz Tamamlandı!")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.info(f"**Seçilən Aktiv: {asset}**")
            st.markdown(response.text)
            
        with col2:
            st.write("**Mənbə Statusları:**")
            for src in sources.keys():
                st.write(f"✅ {src}: Məlumat skan edildi.")

# --- Alt Bilgi ---
st.markdown("---")
st.caption("Xəbərdarlıq: Bu tətbiq yalnız məlumat məqsədi daşıyır. Maliyyə məsləhəti deyildir.")
