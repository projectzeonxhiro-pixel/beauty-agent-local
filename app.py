import streamlit as st
import json
import re
from pathlib import Path
from datetime import date, datetime
from collections import Counter
from statistics import mean

# =========================================================
# 基本設定
# =========================================================
st.set_page_config(
    page_title="Beauty Agent Local",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path("beauty_agent_data")
DATA_DIR.mkdir(exist_ok=True)

DIARY_FILE = DATA_DIR / "diary_entries.json"
PRODUCTS_FILE = DATA_DIR / "products_local.json"

# =========================================================
# データ永続化
# =========================================================
def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def ensure_products_db():
    if PRODUCTS_FILE.exists():
        return
    # ローカル簡易DB（サンプル名）
    sample_products = [
        {
            "name": "モイストバランス化粧水 A",
            "category": "化粧水",
            "price": 1400,
            "skin_types": ["乾燥", "混合", "敏感", "普通"],
            "concerns": ["乾燥", "赤み"],
            "fragrance": "無香料",
            "features": ["保湿", "低刺激", "毎日使いやすい"],
            "keywords": ["glycerin", "hyaluronic acid", "panthenol"],
            "description": "保湿重視のベーシック化粧水。ゆらぎやすい日に使いやすい設計。",
        },
        {
            "name": "スージングエッセンス B",
            "category": "美容液",
            "price": 2200,
            "skin_types": ["敏感", "混合", "普通"],
            "concerns": ["赤み", "乾燥"],
            "fragrance": "無香料",
            "features": ["整肌", "しっとり", "夜向け"],
            "keywords": ["niacinamide", "allantoin", "centella"],
            "description": "赤みが気になる時の整肌サポート向け。保湿とバランスを両立。",
        },
        {
            "name": "ライトジェルローション C",
            "category": "乳液",
            "price": 1600,
            "skin_types": ["脂性", "混合", "普通"],
            "concerns": ["ベタつき", "毛穴"],
            "fragrance": "無香料",
            "features": ["軽い使用感", "ベタつきにくい", "朝向け"],
            "keywords": ["niacinamide", "zinc", "glycerin"],
            "description": "さっぱり系の保湿。朝のメイク前にも使いやすい軽さ。",
        },
        {
            "name": "バリアクリーム D",
            "category": "クリーム",
            "price": 2400,
            "skin_types": ["乾燥", "敏感", "普通"],
            "concerns": ["乾燥", "赤み"],
            "fragrance": "無香料",
            "features": ["バリア感", "夜向け", "乾燥対策"],
            "keywords": ["ceramide", "cholesterol", "squalane"],
            "description": "乾燥しやすい時期の仕上げ保湿に。夜の保護ケア向け。",
        },
        {
            "name": "クリアケア美容液 E",
            "category": "美容液",
            "price": 2800,
            "skin_types": ["脂性", "混合", "普通"],
            "concerns": ["毛穴", "ベタつき"],
            "fragrance": "無香料",
            "features": ["毛穴ケア", "なめらか", "部分使いしやすい"],
            "keywords": ["niacinamide", "bha", "salicylic acid"],
            "description": "ベタつき・毛穴が気になる時の部分ケア向け。頻度調整推奨。",
        },
        {
            "name": "ミルククレンザー F",
            "category": "クレンジング",
            "price": 1800,
            "skin_types": ["乾燥", "敏感", "普通", "混合"],
            "concerns": ["乾燥", "赤み"],
            "fragrance": "無香料",
            "features": ["やさしい洗浄", "しっとり", "摩擦を抑えやすい"],
            "keywords": ["mild surfactant", "glycerin"],
            "description": "メイクが軽い日に向くやさしめクレンジング。",
        },
        {
            "name": "ジェルクレンザー G",
            "category": "洗顔",
            "price": 1200,
            "skin_types": ["脂性", "混合", "普通"],
            "concerns": ["ベタつき", "毛穴"],
            "fragrance": "無香料",
            "features": ["すっきり", "朝夜使いやすい", "軽い泡立ち"],
            "keywords": ["mild surfactant", "zinc"],
            "description": "余分な皮脂感を落としつつ乾燥しにくいバランス型。",
        },
        {
            "name": "UVミルク H",
            "category": "日焼け止め",
            "price": 2100,
            "skin_types": ["敏感", "乾燥", "混合", "普通"],
            "concerns": ["赤み", "乾燥"],
            "fragrance": "無香料",
            "features": ["日中保護", "毎日向け", "しっとり"],
            "keywords": ["uv", "ceramide", "glycerin"],
            "description": "日中の保護重視。乾燥しやすい肌にも使いやすい想定。",
        },
        {
            "name": "ノンフレグランス保湿ミスト I",
            "category": "ミスト",
            "price": 1300,
            "skin_types": ["乾燥", "混合", "敏感", "普通"],
            "concerns": ["乾燥", "赤み"],
            "fragrance": "無香料",
            "features": ["手軽", "持ち運び", "メイク上からOK"],
            "keywords": ["panthenol", "glycerin", "allantoin"],
            "description": "外出先の乾燥対策に使いやすい保湿ミスト。",
        },
        {
            "name": "バランス化粧水 J（微香）",
            "category": "化粧水",
            "price": 1500,
            "skin_types": ["普通", "混合"],
            "concerns": ["ベタつき", "乾燥"],
            "fragrance": "香りあり",
            "features": ["リフレッシュ感", "軽め", "朝向け"],
            "keywords": ["glycerin", "niacinamide"],
            "description": "香りを楽しみたい方向けの軽め保湿。",
        },
    ]
    save_json(PRODUCTS_FILE, sample_products)

ensure_products_db()

# =========================================================
# UIスタイル（女性向け・上品）
# =========================================================
def inject_ui_style():
    st.markdown("""
    <style>
    :root{
      --bg: #070b16;
      --bg2:#0c1224;
      --panel: rgba(255,255,255,0.05);
      --panel-strong: rgba(255,255,255,0.08);
      --stroke: rgba(255,255,255,0.10);
      --text: #F5F7FB;
      --muted: #B8BED0;
      --accent: #FF5D8F;
      --accent2:#B36BFF;
      --shadow: 0 18px 45px rgba(0,0,0,.35);
    }

    .stApp {
      color: var(--text);
      background:
        radial-gradient(1200px 600px at 12% 8%, rgba(255,93,143,0.12), transparent 60%),
        radial-gradient(1000px 540px at 88% 12%, rgba(179,107,255,0.12), transparent 60%),
        radial-gradient(900px 500px at 50% 95%, rgba(58,123,255,0.08), transparent 65%),
        linear-gradient(180deg, #060913 0%, #070b16 45%, #060a14 100%);
    }

    header[data-testid="stHeader"] { background: rgba(0,0,0,0); }
    [data-testid="stDecoration"] { display:none; }

    .block-container{
      padding-top: 1rem;
      padding-bottom: 2rem;
      max-width: 1320px;
    }

    section[data-testid="stSidebar"]{
      background:
        linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02)),
        linear-gradient(180deg, #0A0F1C 0%, #0A1020 100%);
      border-right: 1px solid rgba(255,255,255,0.06);
    }

    .side-card{
      background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.03));
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 20px;
      padding: 16px 16px 14px;
      box-shadow: 0 14px 35px rgba(0,0,0,.28);
      margin-bottom: 14px;
    }
    .side-card-title{
      font-size: 1.05rem;
      font-weight: 800;
      margin-bottom: .25rem;
      letter-spacing: .01em;
    }
    .side-card-sub{
      color: #B8BED0;
      font-size: .86rem;
      line-height: 1.4;
    }

    div[data-baseweb="select"] > div,
    .stTextArea textarea,
    .stTextInput input,
    div[data-testid="stNumberInput"] input,
    input[type="date"] {
      background: rgba(8,12,24,.75) !important;
      border: 1px solid rgba(255,255,255,0.10) !important;
      border-radius: 14px !important;
      color: #F4F7FF !important;
    }

    .stTextArea textarea::placeholder,
    .stTextInput input::placeholder {
      color: #9AA3BC !important;
    }

    span[data-baseweb="tag"]{
      background: rgba(255,255,255,0.08) !important;
      border: 1px solid rgba(255,255,255,0.08) !important;
      border-radius: 999px !important;
      color: #F4F7FF !important;
    }

    div[data-testid="stNumberInput"] button{
      border-radius: 12px !important;
      border: 1px solid rgba(255,255,255,.10) !important;
      background: rgba(255,255,255,.04) !important;
      color: white !important;
    }

    .stSlider [data-baseweb="slider"] > div > div {
      background: linear-gradient(90deg, rgba(255,93,143,.95), rgba(179,107,255,.95)) !important;
    }
    .stSlider [role="slider"]{
      border: 2px solid white !important;
      box-shadow: 0 0 0 6px rgba(255,93,143,.12);
    }

    .stButton > button{
      border-radius: 14px !important;
      border: 1px solid rgba(255,255,255,.10) !important;
      background: linear-gradient(135deg, #FF5D8F 0%, #FF4D78 45%, #B36BFF 100%) !important;
      color: white !important;
      font-weight: 800 !important;
      padding: 0.72rem 1rem !important;
      box-shadow: 0 10px 24px rgba(255,93,143,.22);
      transition: all .15s ease;
    }
    .stButton > button:hover{
      transform: translateY(-1px);
      filter: brightness(1.05);
      box-shadow: 0 14px 28px rgba(255,93,143,.28);
    }

    .stTabs [data-baseweb="tab-list"]{
      gap: 8px;
      background: rgba(255,255,255,.02);
      border: 1px solid rgba(255,255,255,.06);
      border-radius: 16px;
      padding: 6px;
    }
    .stTabs [data-baseweb="tab"]{
      height: 44px;
      border-radius: 12px;
      color: #DDE3F4;
      font-weight: 700;
      padding: 0 14px;
    }
    .stTabs [aria-selected="true"]{
      background: linear-gradient(135deg, rgba(255,93,143,.16), rgba(179,107,255,.14)) !important;
      border: 1px solid rgba(255,255,255,.10) !important;
      color: #FFFFFF !important;
    }

    .hero-card{
      position: relative;
      overflow: hidden;
      padding: 24px 28px;
      border-radius: 26px;
      background:
        radial-gradient(380px 180px at 10% 10%, rgba(255,93,143,.18), transparent 70%),
        radial-gradient(420px 200px at 90% 15%, rgba(179,107,255,.16), transparent 75%),
        linear-gradient(135deg, rgba(255,255,255,.05), rgba(255,255,255,.03));
      border: 1px solid rgba(255,255,255,.08);
      box-shadow: 0 18px 44px rgba(0,0,0,.30);
      margin-bottom: 16px;
    }

    .hero-badge{
      display:inline-flex;
      align-items:center;
      gap:8px;
      padding:6px 12px;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.12);
      background: rgba(255,93,143,.10);
      color:#FFD8E6;
      font-weight:700;
      font-size:.83rem;
      margin-bottom:10px;
    }

    .hero-title{
      font-size: clamp(1.8rem, 2.8vw, 3rem);
      line-height: 1.08;
      font-weight: 900;
      margin: 0 0 10px 0;
      letter-spacing:-.015em;
    }

    .hero-sub{
      color: #C7CEE0;
      font-size: .96rem;
      line-height: 1.6;
      margin-bottom: 12px;
    }

    .chip-row{
      display:flex;
      flex-wrap:wrap;
      gap:8px;
    }
    .chip{
      border-radius:999px;
      padding:8px 12px;
      background: rgba(255,255,255,.04);
      border:1px solid rgba(255,255,255,.08);
      color:#EDEFFD;
      font-weight:600;
      font-size:.86rem;
    }

    .metric-card{
      padding: 18px 20px;
      border-radius: 18px;
      background: linear-gradient(180deg, rgba(255,255,255,.035), rgba(255,255,255,.02));
      border: 1px solid rgba(255,255,255,.07);
      box-shadow: 0 14px 28px rgba(0,0,0,.18);
      min-height: 124px;
      margin-bottom: 8px;
    }
    .metric-label{
      color: #B8BED0;
      font-weight: 700;
      font-size: .9rem;
      margin-bottom: 8px;
    }
    .metric-value{
      font-size: 2rem;
      line-height:1.1;
      font-weight: 900;
      letter-spacing:-.02em;
      margin-bottom: 6px;
    }
    .metric-foot{
      color:#C7CEE0;
      font-size:.86rem;
    }

    .section-card{
      padding: 20px 22px;
      border-radius: 20px;
      background: linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.02));
      border: 1px solid rgba(255,255,255,.07);
      box-shadow: 0 12px 24px rgba(0,0,0,.16);
      margin-top: 14px;
      margin-bottom: 12px;
    }
    .section-title{
      font-size: 1.95rem;
      font-weight: 900;
      letter-spacing:-.02em;
      margin: 0 0 8px 0;
      line-height:1.15;
    }
    .section-sub{
      color: #B8BED0;
      margin-bottom: 12px;
      line-height:1.55;
      font-size:.95rem;
    }

    .result-card{
      border-radius: 16px;
      border: 1px solid rgba(255,255,255,.08);
      background: rgba(255,255,255,.03);
      padding: 14px 16px;
      margin: 10px 0;
    }
    .result-title{
      font-size: 1rem;
      font-weight: 800;
      margin-bottom: 8px;
    }

    .soft-note{
      color:#C7CEE0;
      font-size:.9rem;
      line-height:1.55;
    }

    .product-card{
      border-radius: 16px;
      border: 1px solid rgba(255,255,255,.08);
      background: linear-gradient(180deg, rgba(255,255,255,.035), rgba(255,255,255,.02));
      padding: 14px 16px;
      margin-bottom: 12px;
      box-shadow: 0 10px 20px rgba(0,0,0,.14);
    }
    .product-name{
      font-size: 1.02rem;
      font-weight: 800;
      margin-bottom: 4px;
    }
    .product-meta{
      color:#C7CEE0;
      font-size:.88rem;
      margin-bottom: 8px;
    }
    .pill{
      display:inline-block;
      margin: 2px 6px 2px 0;
      padding: 4px 10px;
      border-radius: 999px;
      border:1px solid rgba(255,255,255,.08);
      background: rgba(255,255,255,.04);
      font-size: .82rem;
      color:#E8ECFA;
    }

    div[data-testid="stAlert"]{
      border-radius: 16px !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      background: rgba(255,255,255,.03) !important;
    }

    @media (max-width: 900px){
      .hero-card { padding: 18px 16px; border-radius: 20px; }
      .hero-title { font-size: 2rem; }
      .metric-card { min-height: 110px; }
      .section-title { font-size: 1.55rem; }
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# UIヘルパー
# =========================================================
def ui_hero(profile_summary: dict):
    skin = profile_summary.get("skin_type", "未設定")
    concerns = profile_summary.get("concerns", [])
    concerns_txt = "・".join(concerns) if concerns else "未設定"
    fragrance = profile_summary.get("fragrance", "未設定")
    budget = int(profile_summary.get("budget", 5000))
    am_min = int(profile_summary.get("am_min", 3))
    pm_min = int(profile_summary.get("pm_min", 10))

    st.markdown(f"""
    <div class="hero-card">
      <div class="hero-badge">💄 streamlitApp・ローカル保存対応</div>
      <div class="hero-title">Beauty Agent Local<br>女性向けセルフケアWeb版</div>
      <div class="hero-sub">
        API不要 / ローカル保存 / 成分チェック・肌日記・傾向・ルーティン・症状別テンプレ・ローカル商品提案
      </div>
      <div class="chip-row">
        <div class="chip">肌タイプ: {skin}</div>
        <div class="chip">悩み: {concerns_txt}</div>
        <div class="chip">香り: {fragrance}</div>
        <div class="chip">予算: ¥{budget:,}</div>
        <div class="chip">朝 {am_min}分 / 夜 {pm_min}分</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def ui_metric_card(label: str, value: str, foot: str = ""):
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      <div class="metric-foot">{foot}</div>
    </div>
    """, unsafe_allow_html=True)

def ui_section_start(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="section-card">
      <div class="section-title">{title}</div>
      <div class="section-sub">{subtitle}</div>
    """, unsafe_allow_html=True)

def ui_section_end():
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# ドメインロジック
# =========================================================
def normalize_text(s: str) -> str:
    return s.strip().lower()

def parse_ingredients(text: str):
    if not text:
        return []
    parts = re.split(r"[,、\n;/]+", text)
    cleaned = [p.strip() for p in parts if p.strip()]
    return cleaned

def ingredient_check(ingredient_list):
    lower = [normalize_text(x) for x in ingredient_list]

    patterns = {
        "香料": ["fragrance", "parfum", "perfume", "aroma"],
        "香料アレルゲン（精油由来含む）": [
            "limonene", "linalool", "citral", "citronellol", "geraniol", "eugenol",
            "farnesol", "coumarin", "hexyl cinnamal", "benzyl alcohol",
            "alpha-isomethyl ionone", "hydroxycitronellal"
        ],
        "乾燥しやすいアルコール": ["alcohol denat", "ethanol", "sd alcohol", "isopropyl alcohol"],
        "整肌・保湿サポート成分": [
            "glycerin", "butylene glycol", "bg", "panthenol", "allantoin",
            "centella", "madecassoside", "ceramide", "hyaluronic acid", "sodium hyaluronate", "squalane"
        ],
        "注目成分（目的ケア系）": [
            "niacinamide", "retinol", "retinal", "salicylic acid", "bha",
            "azelaic", "tranexamic", "ascorbic", "vitamin c"
        ],
    }

    hits = {k: [] for k in patterns.keys()}
    for ing in ingredient_list:
        ing_l = normalize_text(ing)
        for category, keys in patterns.items():
            for kw in keys:
                if kw in ing_l:
                    hits[category].append(ing)
                    break

    # 重複除去
    hits = {k: list(dict.fromkeys(v)) for k, v in hits.items()}

    notes = []
    if hits["香料"] or hits["香料アレルゲン（精油由来含む）"]:
        notes.append("香料/香料アレルゲンの可能性。敏感な方はパッチテスト推奨。")
    if hits["乾燥しやすいアルコール"]:
        notes.append("乾燥しやすい時期・赤みが出やすい時は使用感を見て頻度調整。")
    if not notes:
        notes.append("大きな注意カテゴリは少なめ（ルールベース判定）。最終判断は製品ラベル・メーカー情報を優先。")

    summary_categories = [k for k, v in hits.items() if v]
    return {
        "summary_categories": summary_categories,
        "hits": hits,
        "notes": notes,
    }

def load_diary_entries():
    data = load_json(DIARY_FILE, [])
    # 保険: list 以外を弾く
    return data if isinstance(data, list) else []

def add_diary_entry(entry: dict):
    entries = load_diary_entries()
    entries.append(entry)
    # 日付順に並べる（新しい順）
    entries.sort(key=lambda x: x.get("date", ""), reverse=True)
    save_json(DIARY_FILE, entries)

def delete_diary_entry(index: int):
    entries = load_diary_entries()
    if 0 <= index < len(entries):
        entries.pop(index)
        save_json(DIARY_FILE, entries)

def build_trend_summary(entries):
    if not entries:
        return {
            "count": 0, "avg_sleep": None, "avg_stress": None,
            "top_symptoms": [], "flags": [], "timeline": []
        }

    sleeps = [e.get("sleep_hours") for e in entries if isinstance(e.get("sleep_hours"), (int, float))]
    stresses = [e.get("stress") for e in entries if isinstance(e.get("stress"), (int, float))]

    symptom_counter = Counter()
    timeline = []
    for e in sorted(entries, key=lambda x: x.get("date", "")):
        for s in e.get("symptoms", []):
            symptom_counter[s] += 1
        timeline.append({
            "date": e.get("date"),
            "sleep": e.get("sleep_hours"),
            "stress": e.get("stress"),
        })

    avg_sleep = round(mean(sleeps), 1) if sleeps else None
    avg_stress = round(mean(stresses), 1) if stresses else None
    top_symptoms = symptom_counter.most_common(5)

    flags = []
    if avg_sleep is not None and avg_sleep < 6:
        flags.append("睡眠が短め傾向。乾燥・赤み・くすみが気になる日は睡眠優先で。")
    if avg_stress is not None and avg_stress >= 4:
        flags.append("ストレス高め傾向。刺激の少ないシンプルケア中心が安全。")
    if symptom_counter.get("赤み", 0) >= 2:
        flags.append("赤み記録が複数回。香料・角質ケア・摩擦の頻度を見直すと◎。")
    if symptom_counter.get("乾燥", 0) >= 2:
        flags.append("乾燥記録が複数回。洗いすぎと保湿の量/タイミングを見直すと◎。")
    if symptom_counter.get("ベタつき", 0) >= 2:
        flags.append("ベタつき記録が複数回。重い油分の重ねすぎを減らすと◎。")

    return {
        "count": len(entries),
        "avg_sleep": avg_sleep,
        "avg_stress": avg_stress,
        "top_symptoms": top_symptoms,
        "flags": flags,
        "timeline": timeline,
    }

def generate_routine(profile):
    skin_type = profile.get("skin_type", "未設定")
    concerns = set(profile.get("concerns", []))
    fragrance = profile.get("fragrance", "無香料希望")
    budget = int(profile.get("budget", 5000))
    am_min = int(profile.get("am_min", 3))
    pm_min = int(profile.get("pm_min", 10))

    # 共通方針
    style = []
    if "敏感" in skin_type or "赤み" in concerns:
        style.append("低刺激・摩擦少なめ")
    if "乾燥" in concerns or "乾燥" in skin_type:
        style.append("保湿重視")
    if "ベタつき" in concerns or "脂性" in skin_type:
        style.append("軽め保湿")
    if "毛穴" in concerns:
        style.append("部分ケアを少量")
    if fragrance == "無香料希望":
        style.append("無香料優先")
    if budget <= 4000:
        style.append("アイテム数は絞る")
    if not style:
        style.append("基本の保湿とUVを継続")

    # 朝ルーティン
    morning = []
    # 時短設計
    if am_min <= 3:
        morning = [
            ("洗顔/ぬるま湯", "0.5〜1分", "皮脂・汗を軽くリセット"),
            ("化粧水", "0.5分", "水分補給"),
            ("乳液 or ジェル", "0.5分", "うるおいキープ"),
            ("日焼け止め", "1分", "日中の保護"),
        ]
    else:
        morning = [
            ("洗顔", "1分", "やさしく汚れオフ"),
            ("化粧水", "1分", "水分補給"),
            ("美容液（必要時）", "0.5〜1分", "悩みに合わせる"),
            ("乳液/クリーム", "1分", "保湿のフタ"),
            ("日焼け止め", "1分", "毎日固定"),
        ]

    # 夜ルーティン
    if pm_min <= 6:
        night = [
            ("クレンジング/洗顔", "2分", "落とし残しを減らす"),
            ("化粧水", "1分", "保湿の土台"),
            ("乳液/クリーム", "2分", "保護"),
        ]
    else:
        night = [
            ("クレンジング", "2分", "メイク・UVオフ"),
            ("洗顔", "1分", "やさしく仕上げ"),
            ("化粧水", "1分", "水分補給"),
            ("美容液（悩み別）", "1〜2分", "必要な時だけ"),
            ("乳液/クリーム", "1〜2分", "保湿・保護"),
        ]
        if "乾燥" in concerns:
            night.append(("乾燥部位に重ね保湿", "0.5分", "頬・口周り中心"))
        if "赤み" in concerns:
            night.append(("刺激ケアはお休み判断", "0.5分", "悪化時は攻めない"))
        if "ベタつき" in concerns:
            night.append(("Tゾーン量調整", "0.5分", "塗りすぎ防止"))

    caution = []
    if "赤み" in concerns:
        caution.append("ピーリング/スクラブ/熱いお湯は控えめ")
    if "乾燥" in concerns:
        caution.append("洗いすぎ・拭き取りすぎ注意")
    if "ベタつき" in concerns:
        caution.append("重いクリームを全顔に塗りすぎない")
    if not caution:
        caution.append("新しいアイテムは一度に増やしすぎない")

    return {
        "style": style,
        "morning": morning,
        "night": night,
        "caution": caution
    }

def symptom_templates():
    return {
        "乾燥": {
            "point": "まず“水分＋保護”を優先。攻めのケアは一旦ひかえめ。",
            "avoid": ["熱いお湯", "ゴシゴシ拭く", "角質ケアのやりすぎ"],
            "morning": ["ぬるま湯 or やさしい洗顔", "化粧水", "乳液/クリーム", "日焼け止め"],
            "night": ["クレンジング（必要時）", "やさしい洗顔", "化粧水", "美容液（保湿系）", "クリーム重ね"],
            "tips": ["頬・口周りは重ね塗り", "空調の強い場所はミスト併用"]
        },
        "赤み": {
            "point": "刺激を減らして“落ち着かせる”方向。シンプルケア優先。",
            "avoid": ["香料が強いもの", "ピーリング系の多用", "摩擦", "高温のシャワー"],
            "morning": ["ぬるま湯中心", "低刺激化粧水", "保湿", "日焼け止め"],
            "night": ["やさしい洗浄", "低刺激保湿", "必要最低限のアイテム数"],
            "tips": ["新規アイテムはパッチテスト", "赤みが強い/痛み/腫れは皮膚科へ"]
        },
        "ベタつき": {
            "point": "“落としすぎない”＋“軽い保湿”がコツ。皮脂だけ狙い撃ちしない。",
            "avoid": ["強すぎる洗浄の連発", "アルコール強めの使いすぎ", "重い油分の重ねすぎ"],
            "morning": ["洗顔", "軽め化粧水", "ジェル/軽乳液", "日焼け止め"],
            "night": ["クレンジング/洗顔", "化粧水", "必要なら美容液", "軽め保湿（Tゾーン量調整）"],
            "tips": ["乾燥由来の皮脂増加もある", "ベタつく部位だけ量調整"]
        },
    }

def score_product(product, profile):
    score = 0
    reasons = []

    skin = profile["skin_type"]
    concerns = profile["concerns"]
    fragrance = profile["fragrance"]
    budget = profile["budget"]

    if skin in product.get("skin_types", []):
        score += 3
        reasons.append("肌タイプ一致")
    elif skin == "未設定":
        score += 1

    matched_concerns = [c for c in concerns if c in product.get("concerns", [])]
    if matched_concerns:
        score += 2 * len(matched_concerns)
        reasons.append(f"悩み一致: {'・'.join(matched_concerns)}")

    p_fragrance = product.get("fragrance", "無香料")
    if fragrance == "無香料希望":
        if p_fragrance == "無香料":
            score += 3
            reasons.append("無香料優先")
        else:
            score -= 2
    elif fragrance == "香りありOK":
        if p_fragrance == "香りあり":
            score += 1
            reasons.append("香りありOK")
    else:
        score += 1  # こだわらない

    price = int(product.get("price", 0))
    if price <= budget:
        score += 2
        reasons.append("予算内")
    else:
        over = price - budget
        if over <= 500:
            score += 0
            reasons.append("予算少し超え")
        else:
            score -= 3

    return score, reasons

def recommend_products(profile, products, selected_category="すべて"):
    scored = []
    for p in products:
        if selected_category != "すべて" and p.get("category") != selected_category:
            continue
        score, reasons = score_product(p, profile)
        if score >= 1:
            scored.append((score, reasons, p))
    scored.sort(key=lambda x: (x[0], -int(x[2].get("price", 0))), reverse=True)
    return scored

# =========================================================
# アプリ本体
# =========================================================
def main():
    inject_ui_style()

    # セッション初期値
    if "skin_type" not in st.session_state:
        st.session_state.skin_type = "未設定"
    if "concerns" not in st.session_state:
        st.session_state.concerns = []
    if "fragrance_pref" not in st.session_state:
        st.session_state.fragrance_pref = "無香料希望"
    if "budget" not in st.session_state:
        st.session_state.budget = 5000
    if "am_min" not in st.session_state:
        st.session_state.am_min = 3
    if "pm_min" not in st.session_state:
        st.session_state.pm_min = 10

    diary_entries = load_diary_entries()
    trend = build_trend_summary(diary_entries)

    # ---------------- Sidebar ----------------
    with st.sidebar:
        st.markdown("""
        <div class="side-card">
          <div class="side-card-title">⚙️ プロフィール</div>
          <div class="side-card-sub">あなた向けに提案をやさしく最適化します</div>
        </div>
        """, unsafe_allow_html=True)

        st.session_state.skin_type = st.selectbox(
            "肌タイプ",
            ["未設定", "乾燥", "脂性", "混合", "普通", "敏感"],
            index=["未設定", "乾燥", "脂性", "混合", "普通", "敏感"].index(st.session_state.skin_type)
            if st.session_state.skin_type in ["未設定", "乾燥", "脂性", "混合", "普通", "敏感"] else 0
        )

        concern_options = ["乾燥", "赤み", "ベタつき", "毛穴", "くすみ", "ニキビ", "ゆらぎ"]
        st.session_state.concerns = st.multiselect(
            "悩み",
            concern_options,
            default=[c for c in st.session_state.concerns if c in concern_options],
            placeholder="Choose options"
        )

        st.session_state.fragrance_pref = st.selectbox(
            "香りの好み",
            ["無香料希望", "こだわらない", "香りありOK"],
            index=["無香料希望", "こだわらない", "香りありOK"].index(st.session_state.fragrance_pref)
            if st.session_state.fragrance_pref in ["無香料希望", "こだわらない", "香りありOK"] else 0
        )

        st.session_state.budget = int(st.number_input(
            "月予算（円）",
            min_value=0, max_value=50000, value=int(st.session_state.budget), step=500
        ))

        st.session_state.am_min = int(st.slider("朝ケア時間（分）", 1, 20, int(st.session_state.am_min)))
        st.session_state.pm_min = int(st.slider("夜ケア時間（分）", 1, 30, int(st.session_state.pm_min)))

        st.markdown("---")
        st.caption("※ ローカル保存のため、Streamlit Cloudでは再起動時にデータが消える場合があります。")

    profile = {
        "skin_type": st.session_state.skin_type,
        "concerns": st.session_state.concerns,
        "fragrance": st.session_state.fragrance_pref,
        "budget": st.session_state.budget,
        "am_min": st.session_state.am_min,
        "pm_min": st.session_state.pm_min,
    }

    # ---------------- Main Header ----------------
    ui_hero(profile)

    c1, c2, c3 = st.columns(3)
    with c1:
        ui_metric_card("記録件数", f"{trend['count']}件", "毎日1行でもOK")
    with c2:
        ui_metric_card("平均睡眠", f"{trend['avg_sleep']}時間" if trend["avg_sleep"] is not None else "未記録", "肌のゆらぎと一緒に見やすい")
    with c3:
        ui_metric_card("平均ストレス", f"{trend['avg_stress']}/5" if trend["avg_stress"] is not None else "未記録", "生活要因の振り返り用")

    tabs = st.tabs([
        "成分チェック",
        "肌日記（保存/一覧）",
        "傾向メモ",
        "朝/夜ルーティン",
        "症状別テンプレ",
        "ローカル商品提案"
    ])

    # =====================================================
    # 1) 成分チェック
    # =====================================================
    with tabs[0]:
        ui_section_start(
            "成分チェック（ルールベース簡易）",
            "成分を貼るだけで、香料・香料アレルゲン・乾燥しやすいアルコールなどをざっくり確認できます。"
        )

        ing_text = st.text_area(
            "成分を貼り付け（カンマ区切り / 改行OK）",
            value="",
            placeholder="Water, Glycerin, Niacinamide, Fragrance, Limonene",
            height=140,
            key="ing_text_area",
            label_visibility="collapsed"
        )

        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            run_check = st.button("チェックする", use_container_width=True, key="btn_check_ingredients")

        if run_check:
            items = parse_ingredients(ing_text)
            if not items:
                st.warning("成分を入力してからチェックしてね。")
            else:
                result = ingredient_check(items)

                if result["summary_categories"]:
                    st.markdown(
                        f"""
                        <div class="result-card">
                          <div class="result-title">要点</div>
                          <div class="soft-note">検出カテゴリ → {' / '.join(result['summary_categories'])}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.success("大きな注意カテゴリは少なめです（ルールベース判定）。")

                for category, hits in result["hits"].items():
                    if hits:
                        st.markdown(
                            f'<div class="result-card"><div class="result-title">{category}</div></div>',
                            unsafe_allow_html=True
                        )
                        st.write("・" + "\n・".join(hits))

                st.markdown("### 注意点")
                for n in result["notes"]:
                    st.write(f"- {n}")

                st.caption("※ これはルールベースの簡易チェックです。最終判断は製品ラベル・メーカー情報・専門家確認を優先。")

        ui_section_end()

    # =====================================================
    # 2) 肌日記（保存/一覧）
    # =====================================================
    with tabs[1]:
        sub_tabs = st.tabs(["保存", "一覧"])

        # --- 保存 ---
        with sub_tabs[0]:
            ui_section_start(
                "肌日記を保存",
                "睡眠・ストレス・症状・使ったものを記録して、傾向を見やすくします。"
            )

            with st.form("diary_form", clear_on_submit=False):
                d_col1, d_col2 = st.columns([1, 1])
                with d_col1:
                    diary_date = st.date_input("日付", value=date.today())
                with d_col2:
                    cycle = st.selectbox("体調メモ（任意）", ["未設定", "通常", "疲れ気味", "生理前/中", "寝不足", "外出多め"])

                symptoms = st.multiselect(
                    "症状（複数OK）",
                    ["乾燥", "赤み", "ベタつき", "毛穴", "ニキビ", "かゆみ", "ヒリつき", "くすみ"],
                    default=[]
                )

                c_sleep, c_stress = st.columns(2)
                with c_sleep:
                    sleep_hours = st.slider("睡眠（時間）", 0.0, 12.0, 6.0, 0.5)
                with c_stress:
                    stress = st.slider("ストレス（1〜5）", 1, 5, 3)

                products_used = st.text_input("使用したもの（任意）", placeholder="例：化粧水、美容液、日焼け止め")
                notes = st.text_area("メモ（任意）", placeholder="例：今日は乾燥しやすく、頬が少し赤かった", height=90)

                saved = st.form_submit_button("日記を保存", use_container_width=True)

            if saved:
                entry = {
                    "date": str(diary_date),
                    "cycle": cycle,
                    "symptoms": symptoms,
                    "sleep_hours": float(sleep_hours),
                    "stress": int(stress),
                    "products_used": products_used.strip(),
                    "notes": notes.strip(),
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                }
                add_diary_entry(entry)
                st.success("日記を保存しました。")
                st.rerun()

            ui_section_end()

        # --- 一覧 ---
        with sub_tabs[1]:
            ui_section_start(
                "日記一覧",
                "保存した記録を確認・削除できます。"
            )

            entries = load_diary_entries()
            if not entries:
                st.info("日記はまだありません。")
            else:
                for i, e in enumerate(entries):
                    symptoms_txt = " / ".join(e.get("symptoms", [])) if e.get("symptoms") else "なし"
                    st.markdown(
                        f"""
                        <div class="result-card">
                          <div class="result-title">📅 {e.get('date','-')}　|　症状: {symptoms_txt}</div>
                          <div class="soft-note">
                            睡眠: {e.get('sleep_hours','-')}時間 / ストレス: {e.get('stress','-')}/5 / 体調メモ: {e.get('cycle','未設定')}
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if e.get("products_used"):
                        st.write(f"**使用**: {e.get('products_used')}")
                    if e.get("notes"):
                        st.write(f"**メモ**: {e.get('notes')}")
                    cdel1, cdel2 = st.columns([1, 6])
                    with cdel1:
                        if st.button("削除", key=f"del_{i}"):
                            delete_diary_entry(i)
                            st.success("削除しました。")
                            st.rerun()
                    st.markdown("---")

                # バックアップDL
                st.download_button(
                    "日記データをJSONでダウンロード",
                    data=json.dumps(entries, ensure_ascii=False, indent=2),
                    file_name="beauty_diary_backup.json",
                    mime="application/json",
                    use_container_width=True
                )

            ui_section_end()

    # =====================================================
    # 3) 傾向メモ
    # =====================================================
    with tabs[2]:
        ui_section_start(
            "簡易傾向メモ",
            "記録から、睡眠・ストレス・よく出る症状をざっくり把握します。"
        )

        entries = load_diary_entries()
        trend = build_trend_summary(entries)

        if trend["count"] == 0:
            st.info("日記データはまだありません。まずは1件保存してみてね。")
        else:
            st.markdown("### サマリー")
            st.write(f"- 記録件数: **{trend['count']}件**")
            st.write(f"- 平均睡眠: **{trend['avg_sleep']}時間**" if trend["avg_sleep"] is not None else "- 平均睡眠: 未記録")
            st.write(f"- 平均ストレス: **{trend['avg_stress']}/5**" if trend["avg_stress"] is not None else "- 平均ストレス: 未記録")

            if trend["top_symptoms"]:
                top_text = " / ".join([f"{name}({cnt})" for name, cnt in trend["top_symptoms"][:5]])
                st.write(f"- よく出る症状: {top_text}")
            else:
                st.write("- よく出る症状: まだ記録なし")

            if trend["flags"]:
                st.markdown("### 見立てメモ（簡易）")
                for f in trend["flags"]:
                    st.write(f"- {f}")

            if trend["timeline"]:
                st.markdown("### 記録の時系列（表）")
                st.dataframe(trend["timeline"], use_container_width=True)

        ui_section_end()

    # =====================================================
    # 4) 朝/夜ルーティン
    # =====================================================
    with tabs[3]:
        ui_section_start(
            "朝/夜ルーティン自動作成（ローカル）",
            "プロフィールに合わせて、時短も考慮した無理のないルーティンを提案します。"
        )

        routine = generate_routine(profile)

        st.markdown("### 提案の方向性")
        for s in routine["style"]:
            st.write(f"- {s}")

        col_am, col_pm = st.columns(2)

        with col_am:
            st.markdown("### ☀️ 朝ルーティン")
            for step, minutes, purpose in routine["morning"]:
                st.markdown(
                    f"""
                    <div class="result-card">
                      <div class="result-title">{step} <span style="font-size:.85rem;color:#B8BED0;">（{minutes}）</span></div>
                      <div class="soft-note">{purpose}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col_pm:
            st.markdown("### 🌙 夜ルーティン")
            for step, minutes, purpose in routine["night"]:
                st.markdown(
                    f"""
                    <div class="result-card">
                      <div class="result-title">{step} <span style="font-size:.85rem;color:#B8BED0;">（{minutes}）</span></div>
                      <div class="soft-note">{purpose}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("### 注意ポイント")
        for c in routine["caution"]:
            st.write(f"- {c}")

        ui_section_end()

    # =====================================================
    # 5) 症状別テンプレ
    # =====================================================
    with tabs[4]:
        ui_section_start(
            "症状別テンプレ提案（乾燥 / 赤み / ベタつき）",
            "今日の症状に合わせて、考え方・避けたいこと・朝夜の流れを確認できます。"
        )

        tpls = symptom_templates()
        selected = st.multiselect(
            "症状を選択（複数OK）",
            ["乾燥", "赤み", "ベタつき"],
            default=profile["concerns"] if profile["concerns"] else []
        )

        if not selected:
            st.info("症状を選ぶとテンプレを表示します。")
        else:
            for s in selected:
                t = tpls[s]
                st.markdown(
                    f"""
                    <div class="result-card">
                      <div class="result-title">🩺 {s} テンプレ</div>
                      <div class="soft-note">{t['point']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**朝**")
                    for x in t["morning"]:
                        st.write(f"- {x}")
                    st.markdown("**避けたいこと**")
                    for x in t["avoid"]:
                        st.write(f"- {x}")
                with c2:
                    st.markdown("**夜**")
                    for x in t["night"]:
                        st.write(f"- {x}")
                    st.markdown("**コツ**")
                    for x in t["tips"]:
                        st.write(f"- {x}")

                st.markdown("---")

            st.warning("強い赤み・痛み・腫れ・化膿・急な悪化がある場合は皮膚科へ。")

        ui_section_end()

    # =====================================================
    # 6) ローカル商品提案
    # =====================================================
    with tabs[5]:
        ui_section_start(
            "ローカル商品提案（サンプルDB）",
            "プロフィールに合わせてローカルJSONから候補を提案します。実在商品名に差し替えればそのまま使えます。"
        )

        products = load_json(PRODUCTS_FILE, [])
        if not products:
            st.info("ローカル商品DBが空です。beauty_agent_data/products_local.json を確認してね。")
            ui_section_end()
        else:
            categories = ["すべて"] + sorted(list({p.get("category", "その他") for p in products}))
            selected_category = st.selectbox("カテゴリで絞る", categories)

            recs = recommend_products(profile, products, selected_category=selected_category)

            if not recs:
                st.info("条件に合う候補が少ないです。香り/予算/カテゴリをゆるめると出やすいです。")
            else:
                st.markdown(f"### おすすめ候補（{min(len(recs), 8)}件表示）")
                for score, reasons, p in recs[:8]:
                    pills = ""
                    for ft in p.get("features", []):
                        pills += f'<span class="pill">{ft}</span>'
                    reason_pills = ""
                    for r in reasons:
                        reason_pills += f'<span class="pill">{r}</span>'

                    st.markdown(
                        f"""
                        <div class="product-card">
                          <div class="product-name">{p.get('name','-')}</div>
                          <div class="product-meta">
                            {p.get('category','-')} / ¥{int(p.get('price',0)):,} / 香り: {p.get('fragrance','-')} / スコア: {score}
                          </div>
                          <div style="margin-bottom:8px;">{pills}</div>
                          <div class="soft-note" style="margin-bottom:8px;">{p.get('description','')}</div>
                          <div>{reason_pills}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            with st.expander("ローカル商品DBの使い方（編集ポイント）"):
                st.code(
                    """beauty_agent_data/products_local.json を編集すれば、あなた用の商品候補に差し替えできます。

主な項目:
- name: 商品名
- category: 化粧水 / 美容液 / 乳液 / クリーム / 洗顔 / 日焼け止め など
- price: 価格
- skin_types: 対応肌タイプ一覧
- concerns: 対応悩み一覧
- fragrance: 無香料 / 香りあり
- features: 表示用タグ
- description: 説明文""",
                    language="text"
                )

        ui_section_end()

    # footer
    st.markdown("---")
    st.caption("Beauty Agent Local（オフライン簡易モード） / 成分チェックはルールベースの補助判定です。")

if __name__ == "__main__":
    main()