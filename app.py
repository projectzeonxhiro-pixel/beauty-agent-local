import json
import re
from pathlib import Path
from datetime import datetime, date
from collections import Counter
import streamlit as st

# =========================
# 基本設定
# =========================
st.set_page_config(
    page_title="Beauty Agent Local",
    page_icon="💄",
    layout="wide",
)

DATA_DIR = Path("beauty_agent_data")
JOURNAL_FILE = DATA_DIR / "journal.jsonl"
PROFILE_FILE = DATA_DIR / "profile.json"
PRODUCTS_FILE = DATA_DIR / "products_local.json"


# =========================
# データ準備
# =========================
def ensure_data_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not JOURNAL_FILE.exists():
        JOURNAL_FILE.write_text("", encoding="utf-8")

    if not PROFILE_FILE.exists():
        default_profile = {
            "skin_type": "未設定",
            "concerns": [],
            "fragrance_preference": "未設定",
            "budget_monthly_jpy": 5000,
            "morning_minutes": 3,
            "night_minutes": 10,
        }
        PROFILE_FILE.write_text(
            json.dumps(default_profile, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    if not PRODUCTS_FILE.exists():
        # サンプル（実在商品名はあとで入れ替えOK）
        sample_products = [
            {
                "id": "l01",
                "name": "やさしい保湿化粧水（サンプル）",
                "category": "化粧水",
                "price_jpy": 1200,
                "fragrance_free": True,
                "tags": ["乾燥", "赤み", "低刺激", "保湿"],
                "memo": "まずはしっとり系の土台づくりに"
            },
            {
                "id": "s01",
                "name": "シンプル美容液（ナイアシンアミド配合・サンプル）",
                "category": "美容液",
                "price_jpy": 1800,
                "fragrance_free": True,
                "tags": ["毛穴", "くすみ", "ベタつき", "整肌"],
                "memo": "夜に少量から試す"
            },
            {
                "id": "c01",
                "name": "こっくり保湿クリーム（サンプル）",
                "category": "クリーム",
                "price_jpy": 1500,
                "fragrance_free": True,
                "tags": ["乾燥", "バリア", "夜ケア"],
                "memo": "乾燥しやすい日に"
            },
            {
                "id": "g01",
                "name": "さっぱり保湿ジェル（サンプル）",
                "category": "ジェル",
                "price_jpy": 1300,
                "fragrance_free": True,
                "tags": ["ベタつき", "軽め", "朝ケア"],
                "memo": "皮脂が気になる朝向け"
            },
        ]
        PRODUCTS_FILE.write_text(
            json.dumps(sample_products, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def load_profile() -> dict:
    ensure_data_files()
    try:
        return json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {
            "skin_type": "未設定",
            "concerns": [],
            "fragrance_preference": "未設定",
            "budget_monthly_jpy": 5000,
            "morning_minutes": 3,
            "night_minutes": 10,
        }


def save_profile(profile: dict) -> None:
    PROFILE_FILE.write_text(
        json.dumps(profile, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_products() -> list[dict]:
    ensure_data_files()
    try:
        data = json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def append_journal(entry: dict) -> None:
    ensure_data_files()
    with JOURNAL_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_journals() -> list[dict]:
    ensure_data_files()
    rows: list[dict] = []
    if not JOURNAL_FILE.exists():
        return rows

    with JOURNAL_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


# =========================
# 成分チェック（ルールベース）
# =========================
FRAGRANCE_ALLERGENS = {
    "limonene", "linalool", "citral", "geraniol", "eugenol",
    "citronellol", "hexyl cinnamal", "benzyl alcohol",
    "benzyl salicylate", "coumarin", "farnesol"
}

def normalize_ingredients(text: str) -> list[str]:
    if not text.strip():
        return []
    parts = re.split(r"[,\n、，・;/]+", text)
    return [p.strip() for p in parts if p.strip()]

def ingredient_check(ingredients_text: str) -> dict:
    items = normalize_ingredients(ingredients_text)
    lower_items = [x.lower() for x in items]

    found = []
    notes = []

    # 香料系
    if any(x in {"fragrance", "parfum", "perfume", "香料"} for x in lower_items):
        found.append("香料")

    # 精油由来アレルゲン
    hit_allergens = [orig for orig, low in zip(items, lower_items) if low in FRAGRANCE_ALLERGENS]
    if hit_allergens:
        found.append("香料アレルゲン（精油由来を含む）")

    # ナイアシンアミド
    if any(("niacinamide" in x) or ("ナイアシンアミド" in x) for x in lower_items):
        found.append("ナイアシンアミド")

    # 乾燥/刺激になりやすい可能性（ルールベース）
    if any(("alcohol denat" in x) or ("変性アルコール" in x) for x in lower_items):
        found.append("変性アルコール（人によって刺激になりうる）")

    if "香料" in found or "香料アレルゲン（精油由来を含む）" in found:
        notes.append("香料/香料アレルゲンの可能性。敏感な方はパッチテスト推奨。")

    if "ナイアシンアミド" in found:
        notes.append("ナイアシンアミド配合。人によっては刺激を感じることがあるため少量から。")

    if not notes:
        notes.append("これはルールベースの簡易チェックです。最終判断は製品ラベル・メーカー情報・専門家確認を優先。")

    return {
        "items": items,
        "found_categories": found,
        "notes": notes,
    }


# =========================
# 肌日記分析
# =========================
def summarize_journals(rows: list[dict]) -> dict:
    if not rows:
        return {
            "count": 0,
            "avg_sleep": None,
            "avg_stress": None,
            "top_symptoms": [],
        }

    sleeps = []
    stresses = []
    symptom_counter = Counter()

    for r in rows:
        sh = r.get("sleep_hours")
        stv = r.get("stress")
        if isinstance(sh, (int, float)):
            sleeps.append(float(sh))
        if isinstance(stv, (int, float)):
            stresses.append(float(stv))

        for s in r.get("symptoms", []):
            if s:
                symptom_counter[s] += 1

    return {
        "count": len(rows),
        "avg_sleep": round(sum(sleeps) / len(sleeps), 1) if sleeps else None,
        "avg_stress": round(sum(stresses) / len(stresses), 1) if stresses else None,
        "top_symptoms": symptom_counter.most_common(5),
    }


# =========================
# テンプレ提案
# =========================
SYMPTOM_TEMPLATES = {
    "乾燥": {
        "朝": [
            "ぬるま湯洗顔（こすらない）",
            "化粧水（手でやさしく）",
            "保湿美容液（少量）",
            "乳液 or クリームでフタ",
            "日中の乾燥が強ければ保湿を追い足し",
        ],
        "夜": [
            "やさしく洗顔",
            "化粧水",
            "保湿美容液",
            "クリームをやや多め",
            "乾燥部位だけ重ね塗り",
        ],
        "ポイント": [
            "熱すぎるお湯を避ける",
            "摩擦を減らす",
            "急に攻めた成分を増やしすぎない",
        ],
    },
    "赤み": {
        "朝": [
            "刺激を減らした洗顔（または水洗い）",
            "シンプルな保湿化粧水",
            "低刺激保湿",
            "日中は紫外線・摩擦対策",
        ],
        "夜": [
            "クレンジング/洗顔を短時間で",
            "しみる製品は中止",
            "保湿中心で整える",
            "症状が強い日は新製品を使わない",
        ],
        "ポイント": [
            "香料・精油・強い角質ケアを一旦休む",
            "強い赤み・痛み・腫れは皮膚科へ",
        ],
    },
    "ベタつき": {
        "朝": [
            "洗顔で皮脂をやさしく落とす",
            "軽めの化粧水",
            "必要なら軽めの美容液",
            "ジェル/乳液を少量",
            "テカりやすい部位は塗りすぎない",
        ],
        "夜": [
            "クレンジング/洗顔を丁寧に",
            "さっぱり系〜中間の保湿",
            "乾燥を感じる部位は部分保湿",
            "皮脂が多くても保湿ゼロは避ける",
        ],
        "ポイント": [
            "落としすぎると逆に皮脂が増えることがある",
            "重い油分を顔全体に塗りすぎない",
        ],
    },
}


# =========================
# ルーティン自動作成（ローカル）
# =========================
def build_routine(
    symptoms: list[str],
    concerns: list[str],
    morning_minutes: int,
    night_minutes: int,
    budget_monthly: int,
    fragrance_pref: str,
) -> dict:
    # ベース
    morning = []
    night = []
    caution = []

    # 共通
    morning.append("洗顔（やさしく / 30〜60秒）")
    morning.append("化粧水")
    morning.append("保湿（乳液 or ジェル）")
    morning.append("日中のUV対策（必須）")

    night.append("クレンジング/洗顔")
    night.append("化粧水")
    night.append("美容液（必要なとき）")
    night.append("保湿（乳液/クリーム）")

    # 症状反映
    sset = set(symptoms)
    if "乾燥" in sset:
        morning.insert(2, "保湿美容液（少量）")
        night.append("乾燥部位の重ね塗り")
        caution.append("熱いお湯・摩擦を避ける")
    if "赤み" in sset:
        caution.append("刺激を感じる製品は中止")
        caution.append("香料・精油・ピーリングは一旦控える")
    if "ベタつき" in sset:
        morning = [x for x in morning if x != "保湿（乳液 or ジェル）"] + ["軽め保湿（塗りすぎない）"]
        caution.append("落としすぎによる乾燥に注意")

    # 悩み反映（ざっくり）
    cset = set(concerns)
    if "毛穴" in cset:
        night.insert(-1, "毛穴悩み向け美容液（刺激があれば隔日）")
    if "くすみ" in cset:
        night.insert(-1, "くすみ向け美容液（夜中心・少量から）")

    # 時間制約
    if morning_minutes <= 3:
        morning = [
            "洗顔（短時間）",
            "化粧水",
            "保湿（1品で完結でもOK）",
            "UV対策",
        ]
    elif morning_minutes <= 5:
        morning = morning[:4]

    if night_minutes <= 5:
        night = [
            "クレンジング/洗顔",
            "化粧水",
            "保湿",
        ]
    elif night_minutes <= 10:
        night = night[:4]

    # 予算感コメント
    budget_note = (
        f"月予算 {budget_monthly:,}円："
        + ("まずは洗顔・保湿・UVの基本優先" if budget_monthly <= 3000
           else "基本＋美容液1本までが現実的" if budget_monthly <= 7000
           else "基本＋美容液複数の組み合わせも検討可")
    )

    if fragrance_pref == "無香料希望":
        caution.append("無香料/香料フリー表示を優先して選ぶ")

    # 重複削除（順序維持）
    def dedup(seq: list[str]) -> list[str]:
        seen = set()
        out = []
        for x in seq:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    return {
        "morning": dedup(morning),
        "night": dedup(night),
        "caution": dedup(caution),
        "budget_note": budget_note,
    }


# =========================
# ローカル商品提案
# =========================
def recommend_products_local(
    products: list[dict],
    symptoms: list[str],
    concerns: list[str],
    fragrance_pref: str,
    budget_monthly: int,
) -> list[dict]:
    keywords = set(symptoms + concerns)
    scored = []

    for p in products:
        score = 0
        tags = set(p.get("tags", []))

        # タグ一致
        score += len(tags & keywords) * 3

        # 無香料希望
        if fragrance_pref == "無香料希望" and p.get("fragrance_free") is True:
            score += 2

        # 予算感（ざっくり）
        price = p.get("price_jpy", 999999)
        if isinstance(price, int):
            if budget_monthly <= 3000 and price <= 1500:
                score += 2
            elif budget_monthly <= 7000 and price <= 3000:
                score += 1
            elif budget_monthly > 7000:
                score += 1

        scored.append((score, p))

    # スコア降順 → 価格昇順
    scored.sort(key=lambda x: (-x[0], x[1].get("price_jpy", 999999)))
    return [p for _, p in scored[:8]]


# =========================
# UI
# =========================
ensure_data_files()

st.title("💄 Beauty Agent Local（オフライン簡易モード Web版）")
st.caption("API不要 / ローカル保存 / 成分チェック・日記・傾向・ルーティン・症状別テンプレ・ローカル商品提案")

with st.sidebar:
    st.header("⚙️ プロフィール")
    profile = load_profile()

    skin_type = st.selectbox(
        "肌タイプ",
        ["未設定", "乾燥肌", "脂性肌", "混合肌", "敏感肌", "普通肌"],
        index=["未設定", "乾燥肌", "脂性肌", "混合肌", "敏感肌", "普通肌"].index(profile.get("skin_type", "未設定"))
        if profile.get("skin_type", "未設定") in ["未設定", "乾燥肌", "脂性肌", "混合肌", "敏感肌", "普通肌"]
        else 0,
    )

    concerns = st.multiselect(
        "悩み",
        ["乾燥", "赤み", "ベタつき", "毛穴", "くすみ", "ニキビ", "敏感さ"],
        default=profile.get("concerns", []),
    )

    fragrance_pref = st.selectbox(
        "香りの好み",
        ["未設定", "無香料希望", "香りOK"],
        index=["未設定", "無香料希望", "香りOK"].index(profile.get("fragrance_preference", "未設定"))
        if profile.get("fragrance_preference", "未設定") in ["未設定", "無香料希望", "香りOK"]
        else 0,
    )

    budget_monthly = st.number_input(
        "月予算（円）", min_value=0, max_value=50000,
        value=int(profile.get("budget_monthly_jpy", 5000)), step=500
    )
    morning_minutes = st.slider("朝ケア時間（分）", 1, 15, int(profile.get("morning_minutes", 3)))
    night_minutes = st.slider("夜ケア時間（分）", 1, 30, int(profile.get("night_minutes", 10)))

    if st.button("プロフィール保存", use_container_width=True):
        new_profile = {
            "skin_type": skin_type,
            "concerns": concerns,
            "fragrance_preference": fragrance_pref,
            "budget_monthly_jpy": int(budget_monthly),
            "morning_minutes": int(morning_minutes),
            "night_minutes": int(night_minutes),
        }
        save_profile(new_profile)
        st.success("プロフィールを保存しました。")

tabs = st.tabs([
    "成分チェック",
    "肌日記（保存/一覧）",
    "傾向メモ",
    "朝/夜ルーティン",
    "症状別テンプレ",
    "ローカル商品提案",
])

# ---- Tab 1: 成分チェック
with tabs[0]:
    st.subheader("成分チェック（ルールベース簡易）")
    ing_text = st.text_area(
        "成分を貼り付け（カンマ区切り / 改行OK）",
        height=140,
        placeholder="Water, Glycerin, Niacinamide, Fragrance, Limonene"
    )
    if st.button("チェックする", type="primary"):
        result = ingredient_check(ing_text)
        if not result["items"]:
            st.warning("成分を入力してください。")
        else:
            if result["found_categories"]:
                st.success("要点: 検出カテゴリ → " + " / ".join(result["found_categories"]))
            else:
                st.info("要点: 特記事項は検出されませんでした（簡易ルール）")

            with st.expander("入力成分（正規化後）", expanded=False):
                st.write(result["items"])

            st.markdown("### 注意点")
            for n in result["notes"]:
                st.write(f"- {n}")

            st.caption("最終判断は製品ラベル・メーカー情報・専門家確認を優先してください。")

# ---- Tab 2: 肌日記
with tabs[1]:
    st.subheader("肌日記（保存 / 一覧）")

    col1, col2 = st.columns(2)
    with col1:
        entry_date = st.date_input("日付", value=date.today())
        symptoms = st.multiselect("症状", ["乾燥", "赤み", "ベタつき", "ニキビ", "かゆみ", "ヒリつき"])
        sleep_hours = st.number_input("睡眠時間（h）", min_value=0.0, max_value=24.0, value=6.0, step=0.5)
        stress = st.slider("ストレス（0-5）", 0, 5, 2)
    with col2:
        used_items = st.text_input("使用アイテム（自由入力）", placeholder="例: 化粧水, 美容液")
        condition_note = st.text_area("メモ", height=120, placeholder="例: 今日は乾燥強め。新しい美容液を少量だけ使用。")

    if st.button("日記を保存", type="primary"):
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "date": str(entry_date),
            "symptoms": symptoms,
            "sleep_hours": float(sleep_hours),
            "stress": int(stress),
            "used_items": [x.strip() for x in re.split(r"[、,，/]+", used_items) if x.strip()],
            "note": condition_note.strip(),
        }
        append_journal(entry)
        st.success("日記を保存しました。")

    st.markdown("---")
    rows = load_journals()

    if not rows:
        st.info("日記はまだありません。")
    else:
        st.write(f"件数: {len(rows)}")
        # 新しい順に表示
        for r in sorted(rows, key=lambda x: (x.get("date", ""), x.get("timestamp", "")), reverse=True)[:30]:
            with st.container(border=True):
                st.markdown(f"**{r.get('date', '-') }**")
                st.write(f"症状: {', '.join(r.get('symptoms', [])) or 'なし'}")
                st.write(f"睡眠: {r.get('sleep_hours', '-') } 時間")
                st.write(f"ストレス: {r.get('stress', '-') } / 5")
                st.write(f"使用: {', '.join(r.get('used_items', [])) or 'なし'}")
                if r.get("note"):
                    st.write(f"メモ: {r['note']}")

# ---- Tab 3: 傾向メモ
with tabs[2]:
    st.subheader("最近の肌日記から傾向を見る")
    rows = load_journals()

    if not rows:
        st.info("日記データはまだありません。")
    else:
        # 直近N件
        n = st.slider("分析件数", 1, min(100, len(rows)), min(10, len(rows)))
        recent = sorted(rows, key=lambda x: (x.get("date", ""), x.get("timestamp", "")), reverse=True)[:n]
        summary = summarize_journals(recent)

        st.markdown("### 簡易傾向メモ")
        st.write(f"- 記録件数: {summary['count']}件")
        st.write(f"- 平均睡眠: {summary['avg_sleep']}時間" if summary["avg_sleep"] is not None else "- 平均睡眠: データなし")
        st.write(f"- 平均ストレス: {summary['avg_stress']}/5" if summary["avg_stress"] is not None else "- 平均ストレス: データなし")

        if summary["top_symptoms"]:
            st.write("- よく出る症状: " + " / ".join([f"{k}({v})" for k, v in summary["top_symptoms"]]))
        else:
            st.write("- よく出る症状: データなし")

        st.warning("強い赤み・痛み・腫れ・化膿・急な悪化がある場合は皮膚科へ。")

# ---- Tab 4: ルーティン自動作成
with tabs[3]:
    st.subheader("朝/夜ルーティン自動作成（ローカル）")
    profile = load_profile()

    default_symptoms = []
    default_concerns = profile.get("concerns", [])

    col1, col2 = st.columns(2)
    with col1:
        routine_symptoms = st.multiselect(
            "現在の症状",
            ["乾燥", "赤み", "ベタつき", "ニキビ", "ヒリつき"],
            default=default_symptoms
        )
        routine_concerns = st.multiselect(
            "悩み（追加）",
            ["毛穴", "くすみ", "ニキビ", "敏感さ", "乾燥"],
            default=default_concerns
        )
    with col2:
        routine_budget = st.number_input("月予算（円）", 0, 50000, int(profile.get("budget_monthly_jpy", 5000)), step=500)
        routine_morning = st.slider("朝の時間（分）", 1, 15, int(profile.get("morning_minutes", 3)))
        routine_night = st.slider("夜の時間（分）", 1, 30, int(profile.get("night_minutes", 10)))
        routine_fragrance = st.selectbox("香り希望", ["未設定", "無香料希望", "香りOK"],
                                         index=["未設定", "無香料希望", "香りOK"].index(profile.get("fragrance_preference", "未設定"))
                                         if profile.get("fragrance_preference", "未設定") in ["未設定", "無香料希望", "香りOK"]
                                         else 0)

    if st.button("ルーティン作成", type="primary"):
        plan = build_routine(
            symptoms=routine_symptoms,
            concerns=routine_concerns,
            morning_minutes=int(routine_morning),
            night_minutes=int(routine_night),
            budget_monthly=int(routine_budget),
            fragrance_pref=routine_fragrance,
        )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🌞 朝ルーティン")
            for i, step in enumerate(plan["morning"], 1):
                st.write(f"{i}. {step}")
        with c2:
            st.markdown("### 🌙 夜ルーティン")
            for i, step in enumerate(plan["night"], 1):
                st.write(f"{i}. {step}")

        st.markdown("### 💰 予算メモ")
        st.info(plan["budget_note"])

        if plan["caution"]:
            st.markdown("### ⚠️ 注意点")
            for c in plan["caution"]:
                st.write(f"- {c}")

# ---- Tab 5: 症状別テンプレ
with tabs[4]:
    st.subheader("症状別テンプレ提案（乾燥 / 赤み / ベタつき）")
    target = st.selectbox("症状を選ぶ", ["乾燥", "赤み", "ベタつき"])
    t = SYMPTOM_TEMPLATES[target]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🌞 朝")
        for i, x in enumerate(t["朝"], 1):
            st.write(f"{i}. {x}")
    with c2:
        st.markdown("### 🌙 夜")
        for i, x in enumerate(t["夜"], 1):
            st.write(f"{i}. {x}")

    st.markdown("### ポイント")
    for x in t["ポイント"]:
        st.write(f"- {x}")

# ---- Tab 6: ローカル商品提案
with tabs[5]:
    st.subheader("ローカル商品DBからおすすめ提案（オフライン）")
    st.caption("※ 価格・在庫・最新成分・口コミは自動取得しません。手元の products_local.json を参照します。")

    profile = load_profile()
    products = load_products()

    c1, c2 = st.columns(2)
    with c1:
        rec_symptoms = st.multiselect("症状", ["乾燥", "赤み", "ベタつき", "ニキビ", "敏感さ"])
        rec_concerns = st.multiselect("悩み", ["毛穴", "くすみ", "乾燥", "赤み", "ベタつき"])
    with c2:
        rec_fragrance = st.selectbox("香り条件", ["未設定", "無香料希望", "香りOK"],
                                     index=["未設定", "無香料希望", "香りOK"].index(profile.get("fragrance_preference", "未設定"))
                                     if profile.get("fragrance_preference", "未設定") in ["未設定", "無香料希望", "香りOK"]
                                     else 0)
        rec_budget = st.number_input("月予算（円）", 0, 50000, int(profile.get("budget_monthly_jpy", 5000)), step=500)

    if st.button("おすすめを見る", type="primary"):
        if not products:
            st.warning("products_local.json が空です。")
        else:
            recs = recommend_products_local(
                products=products,
                symptoms=rec_symptoms,
                concerns=rec_concerns,
                fragrance_pref=rec_fragrance,
                budget_monthly=int(rec_budget),
            )
            if not recs:
                st.info("条件に合う候補が見つかりませんでした。")
            else:
                for p in recs:
                    with st.container(border=True):
                        st.markdown(f"**{p.get('name', '商品名未設定')}**")
                        st.write(f"カテゴリ: {p.get('category', '-')}")
                        st.write(f"価格目安: {p.get('price_jpy', '-')}円")
                        st.write(f"無香料: {'はい' if p.get('fragrance_free') else 'いいえ/不明'}")
                        tags = p.get("tags", [])
                        if tags:
                            st.write("タグ: " + " / ".join(tags))
                        if p.get("memo"):
                            st.write("メモ: " + p["memo"])

st.markdown("---")
st.caption("免責: 本アプリは学習・記録補助のローカルツールです。医療判断ではありません。症状が強い/長引く場合は皮膚科へ。")