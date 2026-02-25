import streamlit as st
import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

# =========================
# 基本設定
# =========================
st.set_page_config(
    page_title="Beauty Agent Local",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "beauty_agent_data"
DATA_DIR.mkdir(exist_ok=True)
DIARY_FILE = DATA_DIR / "skin_diary.json"
PRODUCTS_FILE = DATA_DIR / "products_local.json"


# =========================
# データ入出力
# =========================
def load_json(path: Path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def save_json(path: Path, data):
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# 見た目（女性向け・上品系）
# =========================
def inject_ui_style():
    st.markdown(
        """
<style>
:root{
  --bg:#0f1017;
  --panel:#171a24;
  --panel2:#1f2330;
  --soft:#252a39;
  --line:#2b3143;
  --txt:#f4f6fb;
  --muted:#b6bfd4;
  --pink:#ff5c8a;
  --pink2:#ff7aa4;
  --rose:#ffb8cc;
  --lav:#c9b7ff;
  --mint:#9fe3d4;
  --warn:#ffc36b;
}

html, body, [class*="css"] {
  font-family: "Inter", "Segoe UI", "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
}

.stApp {
  background:
    radial-gradient(1000px 500px at 90% -10%, rgba(255, 92, 138, 0.12), transparent 60%),
    radial-gradient(900px 450px at -10% 10%, rgba(201, 183, 255, 0.10), transparent 55%),
    linear-gradient(180deg, #0e1018 0%, #0b0d14 100%);
  color: var(--txt);
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #171926 0%, #131522 100%);
  border-right: 1px solid rgba(255,255,255,0.06);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label {
  color: var(--txt);
}

.block-container{
  padding-top: 1.2rem;
  padding-bottom: 2rem;
  max-width: 1200px;
}

.hero-card{
  background:
    linear-gradient(135deg, rgba(255,92,138,0.10), rgba(201,183,255,0.10)),
    rgba(22,24,34,0.75);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 22px;
  padding: 22px 24px;
  box-shadow: 0 10px 35px rgba(0,0,0,0.28);
  margin-bottom: 14px;
}

.hero-badge{
  display:inline-block;
  font-size: 12px;
  color:#ffe4ec;
  background: rgba(255,92,138,0.18);
  border: 1px solid rgba(255,122,164,0.35);
  padding: 4px 10px;
  border-radius: 999px;
  margin-bottom: 10px;
}

.hero-title{
  font-weight: 800;
  font-size: 40px;
  line-height: 1.15;
  letter-spacing: -0.02em;
  margin: 6px 0 10px;
  color: #ffffff;
}

.hero-sub{
  color: var(--muted);
  font-size: 15px;
  margin-bottom: 8px;
}

.chips{
  display:flex;
  flex-wrap:wrap;
  gap:8px;
  margin-top:8px;
}
.chip{
  display:inline-block;
  background: rgba(255,255,255,0.04);
  border:1px solid rgba(255,255,255,0.08);
  color:#dfe5f6;
  padding:6px 10px;
  border-radius:999px;
  font-size:12px;
}

/* セクションカード */
.section-card{
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.015));
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 18px;
  padding: 18px;
  margin-bottom: 12px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.18);
}
.section-title{
  font-size: 28px;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 6px;
}
.section-desc{
  color: var(--muted);
  font-size: 14px;
  margin-bottom: 10px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{
  gap: 8px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  padding: 8px;
  border-radius: 14px;
}
.stTabs [data-baseweb="tab"]{
  height: 42px;
  border-radius: 10px;
  color: #dce2f3;
  padding: 0 14px;
  font-weight: 600;
  background: transparent;
}
.stTabs [aria-selected="true"]{
  background: linear-gradient(135deg, rgba(255,92,138,0.18), rgba(201,183,255,0.16)) !important;
  border: 1px solid rgba(255,122,164,0.25) !important;
  color: #fff !important;
}

/* 入力系 */
.stTextArea textarea,
.stTextInput input,
.stNumberInput input{
  background: #171b27 !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  color: #f4f6fb !important;
  border-radius: 12px !important;
}
.stSelectbox > div > div,
.stMultiSelect > div > div{
  background: #171b27 !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 12px !important;
}
.stSlider [data-baseweb="slider"]{
  padding-top: .2rem;
}

/* ボタン */
.stButton > button, .stDownloadButton > button {
  background: linear-gradient(135deg, var(--pink), var(--pink2)) !important;
  color: white !important;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 700 !important;
  padding: 0.55rem 1rem !important;
  box-shadow: 0 10px 25px rgba(255,92,138,0.26);
}
.stButton > button:hover {
  filter: brightness(1.04);
  transform: translateY(-1px);
}

/* secondary風ボタン（横並び時の2個目以降も少し馴染ませる） */
.secondary-btn{
  background: rgba(255,255,255,0.04);
  border:1px solid rgba(255,255,255,0.08);
  color:#e9edf8;
  padding:10px 12px;
  border-radius:12px;
}

/* metric card */
.metric-card{
  background: rgba(255,255,255,0.03);
  border:1px solid rgba(255,255,255,0.06);
  border-radius:16px;
  padding:14px;
  min-height: 92px;
}
.metric-label{
  color: var(--muted);
  font-size: 13px;
  margin-bottom: 6px;
}
.metric-value{
  font-weight: 800;
  font-size: 24px;
}
.metric-sub{
  color: #d7dded;
  font-size: 12px;
  margin-top: 4px;
}

/* result / alert */
.result-box{
  background: linear-gradient(180deg, rgba(255,92,138,0.07), rgba(255,92,138,0.03));
  border: 1px solid rgba(255,122,164,0.22);
  border-radius: 14px;
  padding: 14px 16px;
  margin-top: 10px;
}
.note-box{
  background: rgba(159,227,212,0.06);
  border: 1px solid rgba(159,227,212,0.20);
  border-radius: 14px;
  padding: 12px 14px;
}
.warn-box{
  background: rgba(255,195,107,0.06);
  border:1px solid rgba(255,195,107,0.24);
  border-radius:14px;
  padding: 12px 14px;
}
.soft-line{
  border-top:1px solid rgba(255,255,255,0.06);
  margin: 12px 0;
}

/* diary list card */
.diary-card{
  background: rgba(255,255,255,0.025);
  border:1px solid rgba(255,255,255,0.07);
  border-radius: 14px;
  padding: 12px;
  margin-bottom: 10px;
}
.diary-date{
  font-weight:700;
  margin-bottom:6px;
}
.diary-meta{
  color: var(--muted);
  font-size: 13px;
  margin-bottom: 6px;
}
.diary-tags{
  display:flex; flex-wrap:wrap; gap:6px; margin-top:6px;
}
.diary-tag{
  font-size:12px;
  border-radius:999px;
  padding:4px 8px;
  background: rgba(201,183,255,0.08);
  border:1px solid rgba(201,183,255,0.18);
}

/* product card */
.product-card{
  background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
  border:1px solid rgba(255,255,255,0.07);
  border-radius: 16px;
  padding: 14px;
  height: 100%;
}
.product-name{
  font-weight: 700;
  font-size: 16px;
  margin-bottom: 6px;
}
.product-meta{
  color: var(--muted);
  font-size: 13px;
  margin-bottom: 8px;
}
.product-reason{
  font-size: 13px;
  color: #e6ebf7;
}

/* Sidebar profile title */
.sidebar-card{
  background: rgba(255,255,255,0.03);
  border:1px solid rgba(255,255,255,0.06);
  border-radius:16px;
  padding: 12px 12px 4px;
  margin-bottom: 12px;
}
.sidebar-title{
  font-weight: 800;
  font-size: 18px;
  margin-bottom: 8px;
}
.sidebar-desc{
  color: var(--muted);
  font-size: 12px;
  margin-bottom: 6px;
}
</style>
        """,
        unsafe_allow_html=True,
    )


# =========================
# ルールベース成分チェック
# =========================
FRAGRANCE_WORDS = {
    "fragrance", "parfum", "perfume", "香料"
}
ALLERGEN_WORDS = {
    "limonene", "linalool", "citral", "geraniol", "citronellol",
    "eugenol", "farnesol", "benzyl alcohol", "benzyl salicylate",
    "hexyl cinnamal", "coumarin", "精油"
}
DRYING_ALCOHOLS = {
    "alcohol", "ethanol", "sd alcohol", "isopropyl alcohol", "変性アルコール"
}
ACTIVES_GOOD = {
    "niacinamide": "ナイアシンアミド（肌荒れ・皮脂バランス・透明感ケアで人気）",
    "glycerin": "グリセリン（保湿の基本成分）",
    "ceramide": "セラミド（バリアサポート）",
    "hyaluronic acid": "ヒアルロン酸（保水）",
    "panthenol": "パンテノール（整肌）",
    "allantoin": "アラントイン（整肌）",
    "cica": "CICA系（整肌）",
    "centella asiatica": "ツボクサエキス（整肌）",
    "salicylic acid": "サリチル酸（角質・毛穴ケア）",
    "azelaic acid": "アゼライン酸（肌荒れ・皮脂ケアで注目）",
    "retinol": "レチノール（夜のエイジングケアで人気）",
    "vitamin c": "ビタミンC系（透明感・毛穴ケア）",
    "ascorbic": "ビタミンC誘導体系の可能性"
}


def parse_ingredients(text: str):
    if not text:
        return []
    # カンマ、改行、スラッシュ、全角読点などで分割
    parts = re.split(r"[,，/\n]+", text)
    items = [p.strip() for p in parts if p.strip()]
    return items


def ingredient_check(text: str):
    items = parse_ingredients(text)
    normalized = [i.lower() for i in items]

    detected = []
    cautions = []
    good_points = []

    # 検出カテゴリ
    found_fragrance = any(any(w in x for w in FRAGRANCE_WORDS) for x in normalized)
    found_allergen = any(any(w in x for w in ALLERGEN_WORDS) for x in normalized)
    found_alcohol = any(any(w in x for w in DRYING_ALCOHOLS) for x in normalized)

    if found_allergen:
        detected.append("香料アレルゲン（精油由来含む）")
        cautions.append("香料/香料アレルゲンの可能性。敏感な方はパッチテスト推奨。")
    if found_fragrance and "香料アレルゲン（精油由来含む）" not in detected:
        detected.append("香料")
        cautions.append("香り付き製品の可能性。赤みが出やすい時は無香料を優先。")
    if found_alcohol:
        detected.append("乾燥しやすいアルコール")
        cautions.append("乾燥・しみやすさがある時は刺激になりやすい可能性。")

    for key, jp in ACTIVES_GOOD.items():
        if any(key in x for x in normalized):
            good_points.append(jp)

    # 注意レベル（簡易）
    level_score = len(detected)
    if level_score >= 3:
        level = "高"
        level_color = "#ff9b9b"
    elif level_score == 2:
        level = "中"
        level_color = "#ffd58a"
    else:
        level = "低"
        level_color = "#a4f0cf"

    return {
        "items": items,
        "detected": detected,
        "cautions": cautions,
        "good_points": list(dict.fromkeys(good_points)),
        "level": level,
        "level_color": level_color,
    }


# =========================
# 日記
# =========================
def load_diaries():
    data = load_json(DIARY_FILE, [])
    return data if isinstance(data, list) else []


def save_diary(entry: dict):
    diaries = load_diaries()
    diaries.insert(0, entry)  # 新しい順
    save_json(DIARY_FILE, diaries)


def summarize_diary(diaries):
    if not diaries:
        return {
            "count": 0,
            "avg_sleep": None,
            "avg_stress": None,
            "top_symptoms": [],
            "message": "日記データはまだありません。"
        }

    sleep_vals = [d.get("sleep_hours") for d in diaries if isinstance(d.get("sleep_hours"), (int, float))]
    stress_vals = [d.get("stress") for d in diaries if isinstance(d.get("stress"), (int, float))]

    symptom_counter = Counter()
    for d in diaries:
        for s in d.get("symptoms", []):
            symptom_counter[s] += 1

    avg_sleep = round(sum(sleep_vals) / len(sleep_vals), 1) if sleep_vals else None
    avg_stress = round(sum(stress_vals) / len(stress_vals), 1) if stress_vals else None
    top_symptoms = symptom_counter.most_common(5)

    return {
        "count": len(diaries),
        "avg_sleep": avg_sleep,
        "avg_stress": avg_stress,
        "top_symptoms": top_symptoms,
        "message": "簡易傾向メモを表示しています（診断ではありません）。"
    }


# =========================
# 症状テンプレ / ルーティン
# =========================
SYMPTOM_TEMPLATES = {
    "乾燥": [
        "洗いすぎを避ける（朝はぬるま湯のみも検討）",
        "化粧水は“回数を分けて”やさしく重ねる",
        "保湿美容液 → 乳液/クリームで水分を逃がしにくくする",
        "香料・アルコールが強い日は使用点数を減らす",
        "室内乾燥が強い日は加湿・温度調整もセットで"
    ],
    "赤み": [
        "新規アイテムは1つずつ試す（同時導入しない）",
        "摩擦を減らす（コットン・タオル圧を弱く）",
        "無香料・低刺激を優先し、攻めケアは一旦お休み",
        "しみる日は保湿中心に切り替える",
        "赤みが強く続く/悪化する場合は皮膚科へ相談"
    ],
    "ベタつき": [
        "皮脂が気になる日も保湿をゼロにしない",
        "さっぱり化粧水＋軽めの保湿でバランスを取る",
        "毛穴ケアはやりすぎ注意（乾燥で逆に皮脂が増えることも）",
        "日中は皮脂取り紙より“軽くティッシュオフ”を優先",
        "夜は落とし残しを避ける（やさしく丁寧に）"
    ],
}

def build_routine(profile: dict):
    skin_type = profile.get("skin_type", "未設定")
    concerns = profile.get("concerns", [])
    fragrance = profile.get("fragrance_pref", "未設定")
    am_min = int(profile.get("am_minutes", 3))
    pm_min = int(profile.get("pm_minutes", 10))

    morning = []
    night = []

    # 朝
    if am_min <= 3:
        morning = ["洗顔（またはぬるま湯）", "化粧水", "保湿（乳液/ジェル）", "日焼け止め"]
    elif am_min <= 7:
        morning = ["洗顔", "化粧水", "美容液（1種）", "保湿", "日焼け止め"]
    else:
        morning = ["洗顔", "化粧水（2回に分けて）", "美容液（目的別1〜2種）", "保湿", "日焼け止め", "必要なら下地"]

    # 夜
    if pm_min <= 5:
        night = ["クレンジング/洗顔", "化粧水", "保湿"]
    elif pm_min <= 12:
        night = ["クレンジング/洗顔", "化粧水", "美容液（1種）", "乳液/クリーム"]
    else:
        night = ["クレンジング", "洗顔", "化粧水", "美容液（整肌/毛穴など）", "保湿", "ポイントケア（必要時）"]

    # 肌タイプ補正
    if "乾燥" in skin_type:
        morning.insert(min(2, len(morning)), "保湿美容液（しっとり系）")
        night.insert(min(3, len(night)), "保湿美容液（セラミド/ヒアルロン酸系）")
    if "脂性" in skin_type or "混合" in skin_type:
        night.append("ベタつきやすい日はクリーム量を調整")
    if "敏感" in skin_type:
        morning.append("刺激を感じる日は手順を減らして保湿優先")
        night.append("新規成分は毎日使わず様子見")

    # 悩み補正
    if "毛穴" in concerns:
        night.append("毛穴ケア成分は週2〜3回から（やりすぎ注意）")
    if "赤み" in concerns:
        night.append("赤みがある日は攻めケアを休んで整肌中心")
    if "乾燥" in concerns:
        morning.append("日中乾燥する日はミストより保湿の見直し")
    if "ベタつき" in concerns:
        morning.append("ベタつく日も薄く保湿を入れてバランス調整")

    # 香りの好み補正
    notes = []
    if fragrance == "無香料":
        notes.append("無香料優先で選ぶと、赤み・刺激のリスク管理がしやすいです。")
    elif fragrance == "香りありOK":
        notes.append("香り付きOKでも、肌が揺らぐ日は無香料へ切り替えるのがおすすめです。")

    return morning, night, notes


# =========================
# ローカル商品DB（柔軟対応）
# =========================
def fallback_products():
    return [
        {
            "name": "うるおい化粧水（無香料）",
            "category": "化粧水",
            "price": 1500,
            "skin_types": ["乾燥肌", "敏感肌", "混合肌"],
            "concerns": ["乾燥", "赤み"],
            "fragrance": "無香料",
            "reason": "やさしい使用感を想定した保湿重視の基本アイテム"
        },
        {
            "name": "バランシング美容液",
            "category": "美容液",
            "price": 2200,
            "skin_types": ["混合肌", "脂性肌"],
            "concerns": ["ベタつき", "毛穴"],
            "fragrance": "無香料",
            "reason": "皮脂バランスを意識した軽めの使い心地"
        },
        {
            "name": "しっとり保湿クリーム",
            "category": "クリーム",
            "price": 2800,
            "skin_types": ["乾燥肌", "敏感肌"],
            "concerns": ["乾燥", "赤み"],
            "fragrance": "無香料",
            "reason": "乾燥しやすい日のフタ役として使いやすい"
        },
        {
            "name": "軽やか乳液ジェル",
            "category": "乳液",
            "price": 1800,
            "skin_types": ["混合肌", "脂性肌", "普通肌"],
            "concerns": ["ベタつき"],
            "fragrance": "香りありOK",
            "reason": "重たくなりにくい保湿の中間アイテム"
        },
        {
            "name": "やさしめ洗顔フォーム",
            "category": "洗顔",
            "price": 1200,
            "skin_types": ["敏感肌", "混合肌", "普通肌"],
            "concerns": ["赤み", "ベタつき"],
            "fragrance": "無香料",
            "reason": "洗いすぎを避けたい人向けのベースアイテム"
        },
    ]


def normalize_product_item(item):
    if not isinstance(item, dict):
        return None
    # よくあるキー揺れ吸収
    name = item.get("name") or item.get("商品名") or item.get("title")
    category = item.get("category") or item.get("カテゴリ") or "未分類"
    price = item.get("price") or item.get("価格") or item.get("price_jpy") or 0
    try:
        price = int(price)
    except Exception:
        price = 0

    skin_types = item.get("skin_types") or item.get("肌タイプ") or item.get("target_skin") or []
    concerns = item.get("concerns") or item.get("悩み") or item.get("targets") or []
    fragrance = item.get("fragrance") or item.get("香り") or ("無香料" if item.get("fragrance_free") else "未設定")
    reason = item.get("reason") or item.get("おすすめ理由") or item.get("description") or "ローカルDB登録商品"

    if isinstance(skin_types, str):
        skin_types = re.split(r"[,，/・ ]+", skin_types.strip()) if skin_types.strip() else []
    if isinstance(concerns, str):
        concerns = re.split(r"[,，/・ ]+", concerns.strip()) if concerns.strip() else []

    if not name:
        return None

    return {
        "name": str(name),
        "category": str(category),
        "price": price,
        "skin_types": [s for s in skin_types if s],
        "concerns": [c for c in concerns if c],
        "fragrance": str(fragrance),
        "reason": str(reason),
    }


def load_products():
    raw = load_json(PRODUCTS_FILE, [])
    products = []

    if isinstance(raw, list):
        for x in raw:
            p = normalize_product_item(x)
            if p:
                products.append(p)

    if not products:
        products = fallback_products()

    return products


def recommend_products(profile: dict, limit=6):
    products = load_products()
    skin_type = profile.get("skin_type", "未設定")
    concerns = set(profile.get("concerns", []))
    fragrance_pref = profile.get("fragrance_pref", "未設定")
    budget = int(profile.get("budget", 5000))

    ranked = []
    for p in products:
        score = 0
        reasons = []

        if p["price"] <= budget:
            score += 3
            reasons.append("予算内")
        elif p["price"] <= budget * 1.2:
            score += 1
            reasons.append("予算に近い")

        if any(skin_type in s or s in skin_type for s in p["skin_types"]):
            score += 3
            reasons.append("肌タイプ相性")

        concern_matches = [c for c in p["concerns"] if c in concerns]
        if concern_matches:
            score += 2 + len(concern_matches)
            reasons.append("悩み一致")

        if fragrance_pref == "無香料" and ("無香料" in p["fragrance"] or "fragrance_free" in p["fragrance"].lower()):
            score += 2
            reasons.append("無香料寄り")
        elif fragrance_pref == "香りありOK":
            score += 1  # 制約がゆるい

        ranked.append((score, reasons, p))

    ranked.sort(key=lambda x: (x[0], -x[2]["price"]), reverse=True)
    return ranked[:limit]


# =========================
# セッション状態
# =========================
if "profile" not in st.session_state:
    st.session_state.profile = {
        "skin_type": "未設定",
        "concerns": [],
        "fragrance_pref": "未設定",
        "budget": 5000,
        "am_minutes": 3,
        "pm_minutes": 10,
    }

inject_ui_style()

# =========================
# サイドバー（プロフィール）
# =========================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-card">
          <div class="sidebar-title">⚙️ プロフィール</div>
          <div class="sidebar-desc">あなた向けに提案をやさしく最適化します</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    skin_type = st.selectbox(
        "肌タイプ",
        ["未設定", "乾燥肌", "脂性肌", "混合肌", "敏感肌", "普通肌"],
        index=["未設定", "乾燥肌", "脂性肌", "混合肌", "敏感肌", "普通肌"].index(st.session_state.profile.get("skin_type", "未設定"))
    )

    concerns = st.multiselect(
        "悩み",
        ["乾燥", "赤み", "ベタつき", "毛穴", "くすみ", "ハリ不足"],
        default=st.session_state.profile.get("concerns", [])
    )

    fragrance_pref = st.selectbox(
        "香りの好み",
        ["未設定", "無香料", "香りありOK"],
        index=["未設定", "無香料", "香りありOK"].index(st.session_state.profile.get("fragrance_pref", "未設定"))
    )

    budget = st.number_input(
        "月予算（円）",
        min_value=500,
        max_value=50000,
        step=500,
        value=int(st.session_state.profile.get("budget", 5000))
    )

    am_minutes = st.slider(
        "朝ケア時間（分）",
        min_value=1, max_value=20,
        value=int(st.session_state.profile.get("am_minutes", 3))
    )

    pm_minutes = st.slider(
        "夜ケア時間（分）",
        min_value=3, max_value=30,
        value=int(st.session_state.profile.get("pm_minutes", 10))
    )

    st.session_state.profile = {
        "skin_type": skin_type,
        "concerns": concerns,
        "fragrance_pref": fragrance_pref,
        "budget": budget,
        "am_minutes": am_minutes,
        "pm_minutes": pm_minutes,
    }

    st.markdown('<div class="soft-line"></div>', unsafe_allow_html=True)
    st.caption("※ このアプリはセルフケア補助（簡易）です。医療的診断ではありません。")


# =========================
# ヘッダー（ヒーロー）
# =========================
profile = st.session_state.profile
concerns_display = " / ".join(profile["concerns"]) if profile["concerns"] else "未設定"

st.markdown(
    f"""
    <div class="hero-card">
      <div class="hero-badge">streamlitApp ・ ローカル保存対応</div>
      <div class="hero-title">💄 Beauty Agent Local<br>女性向けセルフケアWeb版</div>
      <div class="hero-sub">API不要 / ローカル保存 / 成分チェック・日記・傾向・ルーティン・症状別テンプレ・ローカル商品提案</div>
      <div class="chips">
        <span class="chip">肌タイプ: {profile["skin_type"]}</span>
        <span class="chip">悩み: {concerns_display}</span>
        <span class="chip">香り: {profile["fragrance_pref"]}</span>
        <span class="chip">予算: ¥{profile["budget"]:,}</span>
        <span class="chip">朝 {profile["am_minutes"]}分 / 夜 {profile["pm_minutes"]}分</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 小さめのKPI風表示
diaries = load_diaries()
summary = summarize_diary(diaries)

k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">記録件数</div>
          <div class="metric-value">{summary["count"]}件</div>
          <div class="metric-sub">毎日1行でもOK</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k2:
    avg_sleep_text = f'{summary["avg_sleep"]}時間' if summary["avg_sleep"] is not None else "未記録"
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">平均睡眠</div>
          <div class="metric-value">{avg_sleep_text}</div>
          <div class="metric-sub">肌のゆらぎと一緒に見やすい</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k3:
    avg_stress_text = f'{summary["avg_stress"]}/5' if summary["avg_stress"] is not None else "未記録"
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">平均ストレス</div>
          <div class="metric-value">{avg_stress_text}</div>
          <div class="metric-sub">生活要因の振り返り用</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# =========================
# タブ構成
# =========================
tabs = st.tabs([
    "成分チェック",
    "肌日記（保存/一覧）",
    "傾向メモ",
    "朝/夜ルーティン",
    "症状別テンプレ",
    "ローカル商品提案",
])

# -------------------------
# 1. 成分チェック
# -------------------------
with tabs[0]:
    st.markdown(
        """
        <div class="section-card">
          <div class="section-title">成分チェック（ルールベース簡易）</div>
          <div class="section-desc">成分を貼るだけで、香料・香料アレルゲン・乾燥しやすいアルコールなどをざっくり確認できます。</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    ing_text = st.text_area(
        "成分を貼り付け（カンマ区切り / 改行OK）",
        height=140,
        placeholder="Water, Glycerin, Niacinamide, Fragrance, Limonene"
    )

    c1, c2 = st.columns([1, 5])
    with c1:
        run_check = st.button("チェックする")
    with c2:
        st.caption("※ 最終判断は製品ラベル・メーカー情報・専門家確認を優先してください。")

    if run_check:
        result = ingredient_check(ing_text)

        st.markdown(
            f"""
            <div class="result-box">
              <b>注意レベル:</b>
              <span style="display:inline-block;margin-left:8px;padding:3px 10px;border-radius:999px;
                           background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
                           color:{result["level_color"]};font-weight:700;">
                {result["level"]}
              </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        if result["detected"]:
            st.markdown("### 検出カテゴリ")
            st.write(" / ".join(result["detected"]))
        else:
            st.success("大きな注意カテゴリは検出されませんでした（簡易チェック）。")

        if result["cautions"]:
            st.markdown("### 注意点")
            for c in result["cautions"]:
                st.markdown(f"- {c}")

        if result["good_points"]:
            st.markdown("### ポジティブポイント（検出成分）")
            for g in result["good_points"]:
                st.markdown(f"- {g}")

        st.markdown(
            """
            <div class="note-box">
              <b>メモ:</b><br>
              これはルールベースの簡易チェックです。肌状態が不安定な日は新規アイテムを増やしすぎず、まず保湿中心で様子を見るのがおすすめです。
            </div>
            """,
            unsafe_allow_html=True
        )


# -------------------------
# 2. 肌日記
# -------------------------
with tabs[1]:
    st.markdown(
        """
        <div class="section-card">
          <div class="section-title">肌日記（保存 / 一覧）</div>
          <div class="section-desc">その日の肌状態と生活要因を記録。あとから「なんで荒れた？」の振り返りがしやすくなります。</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("diary_form", clear_on_submit=False):
        col_a, col_b = st.columns(2)
        with col_a:
            diary_date = st.date_input("日付", datetime.now().date())
            symptoms = st.multiselect("症状", ["乾燥", "赤み", "ベタつき", "毛穴目立ち", "ヒリつき", "ニキビ", "くすみ"])
            sleep_hours = st.slider("睡眠時間（時間）", 0.0, 12.0, 6.0, 0.5)
        with col_b:
            stress = st.slider("ストレス（1〜5）", 1, 5, 3)
            used_items = st.text_input("使ったもの（例: 化粧水 / 美容液 / クリーム）", "")
            note = st.text_area("メモ", height=110, placeholder="例）今日は赤み少し。乾燥あり。新しい美容液を使った。")

        submitted = st.form_submit_button("日記を保存する")

    if submitted:
        entry = {
            "date": str(diary_date),
            "symptoms": symptoms,
            "sleep_hours": sleep_hours,
            "stress": stress,
            "used_items": [x.strip() for x in re.split(r"[,，/・]+", used_items) if x.strip()],
            "note": note.strip(),
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        save_diary(entry)
        st.success("日記を保存しました ✅")

    st.markdown("### 一覧（新しい順）")
    diaries = load_diaries()

    if not diaries:
        st.info("日記はまだありません。まずは1件記録してみましょう。")
    else:
        # 表示件数
        view_count = st.selectbox("表示件数", [5, 10, 20, 50], index=1)
        for d in diaries[:view_count]:
            symptoms_html = "".join([f'<span class="diary-tag">{s}</span>' for s in d.get("symptoms", [])])
            used_html = " / ".join(d.get("used_items", [])) if d.get("used_items") else "未記載"
            note_text = d.get("note", "").replace("<", "＜").replace(">", "＞")
            st.markdown(
                f"""
                <div class="diary-card">
                  <div class="diary-date">🗓️ {d.get("date", "日付未設定")}</div>
                  <div class="diary-meta">睡眠: {d.get("sleep_hours", "-")}時間 / ストレス: {d.get("stress", "-")}/5 / 使用: {used_html}</div>
                  <div>{note_text if note_text else "メモなし"}</div>
                  <div class="diary-tags">{symptoms_html}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


# -------------------------
# 3. 傾向メモ
# -------------------------
with tabs[2]:
    st.markdown(
        """
        <div class="section-card">
          <div class="section-title">傾向メモ（簡易）</div>
          <div class="section-desc">保存した肌日記から、睡眠・ストレス・症状の出やすさをざっくり表示します。</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    diaries = load_diaries()
    summary = summarize_diary(diaries)

    if summary["count"] == 0:
        st.info("日記データはまだありません。先に「肌日記」タブで記録してください。")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f"""
                <div class="metric-card">
                  <div class="metric-label">平均睡眠</div>
                  <div class="metric-value">{summary["avg_sleep"] if summary["avg_sleep"] is not None else "未記録"}{"時間" if summary["avg_sleep"] is not None else ""}</div>
                  <div class="metric-sub">記録 {summary["count"]}件</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                f"""
                <div class="metric-card">
                  <div class="metric-label">平均ストレス</div>
                  <div class="metric-value">{summary["avg_stress"] if summary["avg_stress"] is not None else "未記録"}{" /5" if summary["avg_stress"] is not None else ""}</div>
                  <div class="metric-sub">生活要因の振り返り用</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c3:
            top1 = summary["top_symptoms"][0][0] if summary["top_symptoms"] else "未記録"
            st.markdown(
                f"""
                <div class="metric-card">
                  <div class="metric-label">よく出る症状</div>
                  <div class="metric-value">{top1}</div>
                  <div class="metric-sub">簡易集計</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("### 簡易傾向メモ")
        st.markdown(f"- {summary['message']}")
        if summary["top_symptoms"]:
            symptom_line = " / ".join([f"{k}({v})" for k, v in summary["top_symptoms"]])
            st.markdown(f"- よく出る症状: {symptom_line}")

        # ゆるいアドバイス
        if summary["avg_sleep"] is not None and summary["avg_sleep"] < 6:
            st.markdown("- 平均睡眠がやや短め。肌が揺らぐ時期は、まず保湿と休息を優先すると安定しやすいです。")
        if summary["avg_stress"] is not None and summary["avg_stress"] >= 4:
            st.markdown("- ストレスが高めの記録が多いです。新規アイテム追加より“今のケアをシンプルに整える”方が相性が良い日もあります。")
        if any(s in ["赤み", "ヒリつき"] for s, _ in summary["top_symptoms"]):
            st.markdown("- 赤み/ヒリつきが目立つ時は、香りや刺激が強いものを一時的に減らして様子を見るのがおすすめです。")

        st.markdown(
            """
            <div class="warn-box">
              強い赤み・痛み・腫れ・化膿・急な悪化がある場合は、セルフケアだけで判断せず皮膚科へ相談してください。
            </div>
            """,
            unsafe_allow_html=True
        )


# -------------------------
# 4. 朝/夜ルーティン
# -------------------------
with tabs[3]:
    st.markdown(
        """
        <div class="section-card">
          <div class="section-title">朝 / 夜ルーティン自動作成（ローカル）</div>
          <div class="section-desc">プロフィールに合わせて、続けやすい手順をシンプルに提案します。忙しい日でも回せる構成を優先。</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    morning, night, notes = build_routine(profile)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🌤 朝ルーティン")
        for i, step in enumerate(morning, 1):
            st.markdown(f"{i}. {step}")
    with c2:
        st.markdown("### 🌙 夜ルーティン")
        for i, step in enumerate(night, 1):
            st.markdown(f"{i}. {step}")

    st.markdown("### ひとことアドバイス")
    if notes:
        for n in notes:
            st.markdown(f"- {n}")
    else:
        st.markdown("- 肌が揺らぐ日は、手順を増やすより“しみない・続けられる”を優先すると安定しやすいです。")

    st.markdown(
        """
        <div class="note-box">
          <b>コツ:</b> 新しい美容液を入れる日は、他の条件（洗顔・保湿・生活リズム）をなるべく固定すると相性判断がしやすくなります。
        </div>
        """,
        unsafe_allow_html=True
    )


# -------------------------
# 5. 症状別テンプレ
# -------------------------
with tabs[4]:
    st.markdown(
        """
        <div class="section-card">
          <div class="section-title">症状別テンプレ提案（乾燥 / 赤み / ベタつき）</div>
          <div class="section-desc">“今日はこれ気になる”に合わせて、やることをすぐ確認できるチェックリストです。</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    symptom_choice = st.radio("気になる症状を選ぶ", ["乾燥", "赤み", "ベタつき"], horizontal=True)

    st.markdown(f"### {symptom_choice}の日のケア指針")
    for i, item in enumerate(SYMPTOM_TEMPLATES[symptom_choice], 1):
        st.markdown(f"{i}. {item}")

    if symptom_choice == "赤み":
        st.markdown(
            """
            <div class="warn-box">
              赤みが強い / 熱感がある / 触ると痛い / 長引く場合は、早めに皮膚科相談を。
            </div>
            """,
            unsafe_allow_html=True
        )


# -------------------------
# 6. ローカル商品提案
# -------------------------
with tabs[5]:
    st.markdown(
        """
        <div class="section-card">
          <div class="section-title">ローカル商品提案（DBベース）</div>
          <div class="section-desc">登録しているローカル商品DBから、肌タイプ・悩み・予算・香りの好みに合わせて候補を提案します。</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption("※ 外部API検索ではなく、ローカルDB（products_local.json）を利用します。")
    recs = recommend_products(profile, limit=6)

    if not recs:
        st.info("商品DBが空です。`beauty_agent_data/products_local.json` を確認してください。")
    else:
        cols = st.columns(2)
        for idx, (score, reasons, p) in enumerate(recs):
            with cols[idx % 2]:
                reasons_text = " / ".join(reasons) if reasons else "条件に近い"
                st.markdown(
                    f"""
                    <div class="product-card">
                      <div class="product-name">🧴 {p["name"]}</div>
                      <div class="product-meta">カテゴリ: {p["category"]} / 目安価格: ¥{p["price"]:,} / 香り: {p["fragrance"]}</div>
                      <div class="product-reason"><b>おすすめ理由:</b> {p["reason"]}</div>
                      <div class="diary-tags" style="margin-top:8px;">
                        <span class="diary-tag">スコア {score}</span>
                        <span class="diary-tag">{reasons_text}</span>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown(
        """
        <div class="note-box">
          <b>DB拡張メモ:</b> products_local.json に商品を追加すると、提案の幅が広がります。<br>
          例キー: name / category / price / skin_types / concerns / fragrance / reason
        </div>
        """,
        unsafe_allow_html=True
    )

# フッター
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
st.caption("Beauty Agent Local（オフライン簡易モードWeb版）｜セルフケア補助アプリ")