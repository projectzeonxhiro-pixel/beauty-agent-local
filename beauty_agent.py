import json
import re
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# =========================================================
# ローカル完全版 美容AI（API不要）
# 機能:
# - 成分チェック（ルールベース）
# - 肌日記 保存 / 一覧 / 傾向
# - 症状別テンプレ提案（乾燥/赤み/ベタつき）
# - 朝/夜ルーティン自動作成（ローカル）
# - ローカル商品DBからおすすめ提案（予算/無香料/症状）
# - ルーティン＋商品候補のセット提案
# =========================================================

DATA_DIR = Path("beauty_agent_data")
JOURNAL_PATH = DATA_DIR / "journal.jsonl"
PROFILE_PATH = DATA_DIR / "profile.json"        # 任意: allergies, preferences など
PRODUCTS_PATH = DATA_DIR / "products_local.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# 共通ユーティリティ
# ---------------------------------------------------------
def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

def read_json(path: Path, default: Any):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def write_json(path: Path, data: Any):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def append_jsonl(path: Path, row: Dict[str, Any]):
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows

def print_ai(text: str):
    for line in text.splitlines():
        print("美容AI > " + line)

# ---------------------------------------------------------
# ローカル商品DB（初期データ）
# ※ 実在商品名ではなく、ローカル運用しやすい汎用名テンプレ
#    → 後で自分の使いたい商品に置き換え可能
# ---------------------------------------------------------
def ensure_local_products():
    if PRODUCTS_PATH.exists():
        return

    seed = [
        # 洗顔
        {
            "id": "c01",
            "name": "低刺激ジェル洗顔A",
            "category": "洗顔",
            "price_jpy": 1200,
            "months_last": 1.5,
            "fragrance_free": True,
            "alcohol_free": True,
            "skin_types": ["乾燥", "敏感", "混合"],
            "good_for": ["乾燥", "赤み"],
            "avoid_if": [],
            "notes": "朝夜使いやすい低刺激寄り",
            "tags": ["低刺激", "ジェル", "毎日"]
        },
        {
            "id": "c02",
            "name": "さっぱり泡洗顔B",
            "category": "洗顔",
            "price_jpy": 900,
            "months_last": 1.2,
            "fragrance_free": True,
            "alcohol_free": True,
            "skin_types": ["脂性", "混合"],
            "good_for": ["ベタつき"],
            "avoid_if": ["赤み"],
            "notes": "皮脂が気になる日に向く",
            "tags": ["泡", "さっぱり"]
        },

        # 化粧水
        {
            "id": "t01",
            "name": "しっとり化粧水A",
            "category": "化粧水",
            "price_jpy": 1500,
            "months_last": 1.2,
            "fragrance_free": True,
            "alcohol_free": True,
            "skin_types": ["乾燥", "敏感", "混合"],
            "good_for": ["乾燥", "赤み"],
            "avoid_if": [],
            "notes": "刺激が少ない前提のシンプル保湿",
            "tags": ["保湿", "シンプル"]
        },
        {
            "id": "t02",
            "name": "軽め化粧水B",
            "category": "化粧水",
            "price_jpy": 1200,
            "months_last": 1.2,
            "fragrance_free": True,
            "alcohol_free": True,
            "skin_types": ["脂性", "混合"],
            "good_for": ["ベタつき"],
            "avoid_if": [],
            "notes": "ベタつきやすい人向けの軽い使用感想定",
            "tags": ["軽め", "さっぱり"]
        },

        # 美容液
        {
            "id": "s01",
            "name": "保湿美容液A",
            "category": "美容液",
            "price_jpy": 2200,
            "months_last": 1.5,
            "fragrance_free": True,
            "alcohol_free": True,
            "skin_types": ["乾燥", "敏感", "混合"],
            "good_for": ["乾燥", "赤み"],
            "avoid_if": [],
            "notes": "保湿寄りの毎日使い想定",
            "tags": ["保湿", "毎日"]
        },
        {
            "id": "s02",
            "name": "整肌美容液B（軽め）",
            "category": "美容液",
            "price_jpy": 2500,
            "months_last": 1.5,
            "fragrance_free": True,
            "alcohol_free": True,
            "skin_types": ["脂性", "混合"],
            "good_for": ["ベタつき", "毛穴目立ち"],
            "avoid_if": ["赤み"],
            "notes": "刺激が出やすい人は様子見",
            "tags": ["整肌", "軽め"]
        },

        # 乳液 / クリーム
        {
            "id": "m01",
            "name": "軽い乳液A",
            "category": "乳液",
            "price_jpy": 1600,
            "months_last": 1.5,
            "fragrance_free": True,
            "alcohol_free": True,
            "skin_types": ["混合", "脂性", "乾燥"],
            "good_for": ["ベタつき", "乾燥"],
            "avoid_if": [],
            "notes": "量で調整しやすい",
            "tags": ["軽い", "調整しやすい"]
        },
        {
            "id": "m02",
            "name": "保湿クリームA",
            "category": "クリーム",
            "price_jpy": 1800,
            "months_last": 2.0,
            "fragrance_free": True,
            "alcohol_free": True,
            "skin_types": ["乾燥", "敏感", "混合"],
            "good_for": ["乾燥", "赤み"],
            "avoid_if": ["ベタつき"],
            "notes": "乾燥部位中心の使用向け",
            "tags": ["高保湿", "夜向け"]
        },

        # 日焼け止め
        {
            "id": "u01",
            "name": "低刺激UVミルクA",
            "category": "日焼け止め",
            "price_jpy": 1900,
            "months_last": 1.0,
            "fragrance_free": True,
            "alcohol_free": True,
            "skin_types": ["敏感", "乾燥", "混合"],
            "good_for": ["赤み", "乾燥"],
            "avoid_if": [],
            "notes": "低刺激寄りの想定",
            "tags": ["UV", "低刺激"]
        },
        {
            "id": "u02",
            "name": "軽いUVジェルB",
            "category": "日焼け止め",
            "price_jpy": 1400,
            "months_last": 1.0,
            "fragrance_free": True,
            "alcohol_free": False,
            "skin_types": ["脂性", "混合"],
            "good_for": ["ベタつき"],
            "avoid_if": ["赤み", "乾燥"],
            "notes": "軽い使用感優先。乾燥・赤み時は注意",
            "tags": ["UV", "軽い"]
        }
    ]
    write_json(PRODUCTS_PATH, seed)

def load_products() -> List[Dict[str, Any]]:
    ensure_local_products()
    data = read_json(PRODUCTS_PATH, [])
    return data if isinstance(data, list) else []

# ---------------------------------------------------------
# 成分チェック（ルールベース）
# ---------------------------------------------------------
INGREDIENT_PATTERNS = {
    "retinoid": [
        r"\bretinol\b", r"\bretinal\b", r"\bretinaldehyde\b", r"\bretinyl\b",
        r"\badapalene\b", r"\btretinoin\b"
    ],
    "bha": [r"\bsalicylic acid\b", r"\bbeta hydroxy acid\b"],
    "aha": [r"\bglycolic acid\b", r"\blactic acid\b", r"\bmandelic acid\b", r"\baha\b"],
    "vitamin_c": [
        r"\bascorbic acid\b", r"\bsodium ascorbyl phosphate\b",
        r"\bmagnesium ascorbyl phosphate\b", r"\b3-o-ethyl ascorbic acid\b",
        r"\bascorbyl glucoside\b"
    ],
    "niacinamide": [r"\bniacinamide\b"],
    "benzoyl_peroxide": [r"\bbenzoyl peroxide\b"],
    "fragrance": [r"\bfragrance\b", r"\bparfum\b", r"\bperfume\b"],
    "essential_oil_allergens": [r"\blimonene\b", r"\blinalool\b", r"\bgeraniol\b", r"\bcitral\b", r"\bcitronellol\b", r"\beugenol\b"],
    "drying_alcohol": [r"\balcohol denat\b", r"\bethanol\b", r"\bisopropyl alcohol\b"],
    "physical_exfoliant": [r"\bwalnut shell\b", r"\bapricot kernel powder\b", r"\bscrub\b"],
}

CATEGORY_LABELS = {
    "retinoid": "レチノイド系",
    "bha": "BHA（サリチル酸など）",
    "aha": "AHA（グリコール酸など）",
    "vitamin_c": "ビタミンC系",
    "niacinamide": "ナイアシンアミド",
    "benzoyl_peroxide": "過酸化ベンゾイル",
    "fragrance": "香料",
    "essential_oil_allergens": "香料アレルゲン（精油由来を含む）",
    "drying_alcohol": "乾燥感につながるアルコール候補",
    "physical_exfoliant": "物理スクラブ候補",
}

def _normalize_ingredients(text: str) -> str:
    t = (text or "").lower()
    t = t.replace("、", ",").replace("，", ",").replace(";", ",")
    return t

def analyze_ingredients_rule_based(ingredients_text: str, user_allergies: Optional[List[str]] = None) -> Dict[str, Any]:
    t = _normalize_ingredients(ingredients_text)
    detected: Dict[str, List[str]] = {}

    for tag, patterns in INGREDIENT_PATTERNS.items():
        hits = []
        for p in patterns:
            if re.search(p, t):
                hits.append(p)
        if hits:
            detected[tag] = hits

    allergies = [str(a).strip().lower() for a in (user_allergies or []) if str(a).strip()]
    allergy_hits = [a for a in allergies if a in t]

    cautions: List[str] = []
    notes: List[str] = []

    if "retinoid" in detected:
        cautions.append("レチノイド系の可能性あり。刺激を感じやすい方は夜・低頻度から開始、保湿＋日中UV対策を重視。")
        notes.append("妊娠中・授乳中・治療中は医師/薬剤師に確認。")
    if "aha" in detected or "bha" in detected:
        cautions.append("角質ケア成分（AHA/BHA）の可能性。敏感な時期は頻度を下げ、刺激の強い併用は避ける。")
    if "fragrance" in detected or "essential_oil_allergens" in detected:
        cautions.append("香料/香料アレルゲンの可能性。敏感な方はパッチテスト推奨。")
    if "drying_alcohol" in detected:
        cautions.append("アルコール系の可能性。乾燥肌・敏感肌は使用感を確認。")
    if "benzoyl_peroxide" in detected and "retinoid" in detected:
        cautions.append("過酸化ベンゾイルとレチノイドの併用は刺激が出る人も。分けて使う検討を。")
    if "physical_exfoliant" in detected:
        cautions.append("物理スクラブの可能性。摩擦に注意。赤みが出るなら中止。")
    if allergy_hits:
        cautions.append("登録アレルギー候補と一致する成分文字列を検出。ラベル再確認を。")
    if not detected:
        notes.append("代表的キーワードの検出なし（表記ゆれ・別名で検出漏れの可能性あり）。")

    notes.append("これはルールベースの簡易チェック。最終判断は製品ラベル・メーカー情報・専門家確認を優先。")

    return {
        "detected_categories": sorted(detected.keys()),
        "allergy_matches": allergy_hits,
        "cautions": cautions,
        "notes": notes,
    }

def format_ingredient_result(result: Dict[str, Any]) -> str:
    lines = []
    cats = result.get("detected_categories", [])
    if cats:
        labels = [CATEGORY_LABELS.get(c, c) for c in cats]
        lines.append("要点: 検出カテゴリ → " + " / ".join(labels))
    else:
        lines.append("要点: 特徴的な成分カテゴリは検出されませんでした（簡易判定）")

    if result.get("cautions"):
        lines.append("")
        lines.append("注意点:")
        for c in result["cautions"]:
            lines.append(f"- {c}")

    if result.get("notes"):
        lines.append("")
        lines.append("メモ:")
        for n in result["notes"]:
            lines.append(f"- {n}")

    return "\n".join(lines)

# ---------------------------------------------------------
# 肌日記（保存 / 一覧 / 傾向）
# ---------------------------------------------------------
SYMPTOM_KEYWORDS = [
    "赤み", "乾燥", "かゆみ", "ヒリつき", "ひりつき", "ニキビ", "皮むけ", "つっぱり",
    "ベタつき", "てかり", "毛穴目立ち", "くすみ"
]
PRODUCT_HINTS = ["化粧水", "乳液", "美容液", "クリーム", "洗顔", "クレンジング", "日焼け止め", "パック"]

def parse_journal_text(text: str) -> Dict[str, Any]:
    raw = text.strip()

    sleep_hours = None
    m_sleep = re.search(r"睡眠\s*([0-9]+(?:\.[0-9]+)?)\s*時間", raw)
    if m_sleep:
        try:
            sleep_hours = float(m_sleep.group(1))
        except ValueError:
            pass

    stress = None
    m_stress = re.search(r"ストレス\s*([1-5])", raw)
    if m_stress:
        try:
            stress = int(m_stress.group(1))
        except ValueError:
            pass

    symptoms = []
    for kw in SYMPTOM_KEYWORDS:
        if kw in raw:
            symptoms.append(kw)
    symptoms = list(dict.fromkeys(symptoms))

    products_used = []
    for kw in PRODUCT_HINTS:
        if kw in raw:
            products_used.append(kw)
    products_used = list(dict.fromkeys(products_used))

    summary = raw
    summary = re.sub(r"肌日記(として)?保存して", "", summary)
    summary = re.sub(r"日記として保存して", "", summary)
    summary = re.sub(r"保存して$", "", summary)
    summary = summary.strip(" 。、")

    return {
        "condition_summary": summary if summary else "記録",
        "symptoms": symptoms,
        "products_used": products_used,
        "sleep_hours": sleep_hours,
        "stress_level_1to5": stress,
        "memo": None,
        "date": datetime.now().strftime("%Y-%m-%d"),
    }

def save_skin_journal(entry: Dict[str, Any]) -> Dict[str, Any]:
    row = {
        "id": f"journal_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
        "created_at": now_iso(),
        "date": entry.get("date") or datetime.now().strftime("%Y-%m-%d"),
        "condition_summary": entry.get("condition_summary", "記録"),
        "symptoms": entry.get("symptoms") or [],
        "products_used": entry.get("products_used") or [],
        "sleep_hours": entry.get("sleep_hours"),
        "stress_level_1to5": entry.get("stress_level_1to5"),
        "memo": entry.get("memo"),
    }
    append_jsonl(JOURNAL_PATH, row)
    return row

def list_skin_journal(limit: int = 7) -> List[Dict[str, Any]]:
    n = max(1, min(limit, 30))
    return list(reversed(read_jsonl(JOURNAL_PATH)))[:n]

def journal_summary(entries: List[Dict[str, Any]]) -> str:
    if not entries:
        return "日記データはまだありません。"

    sleep_vals = [e.get("sleep_hours") for e in entries if isinstance(e.get("sleep_hours"), (int, float))]
    stress_vals = [e.get("stress_level_1to5") for e in entries if isinstance(e.get("stress_level_1to5"), int)]

    symptom_count: Dict[str, int] = {}
    for e in entries:
        for s in (e.get("symptoms") or []):
            symptom_count[s] = symptom_count.get(s, 0) + 1

    top_symptoms = sorted(symptom_count.items(), key=lambda x: x[1], reverse=True)[:3]

    lines = ["簡易傾向メモ:"]
    if sleep_vals:
        lines.append(f"- 平均睡眠: {sum(sleep_vals)/len(sleep_vals):.1f}時間（記録 {len(sleep_vals)}件）")
    else:
        lines.append("- 睡眠記録: なし")
    if stress_vals:
        lines.append(f"- 平均ストレス: {sum(stress_vals)/len(stress_vals):.1f}/5（記録 {len(stress_vals)}件）")
    else:
        lines.append("- ストレス記録: なし")
    if top_symptoms:
        lines.append("- よく出る症状: " + " / ".join([f"{k}({v})" for k, v in top_symptoms]))
    else:
        lines.append("- 症状キーワード記録: なし")
    lines.append("- 強い赤み・痛み・腫れ・化膿・急な悪化がある場合は皮膚科へ。")
    return "\n".join(lines)

def format_journal_entries(entries: List[Dict[str, Any]]) -> str:
    if not entries:
        return "日記はまだありません。"

    lines = []
    for e in entries:
        lines.append(f" {e.get('condition_summary', '')}")
        if e.get("symptoms"):
            lines.append(f"  症状: {', '.join(e['symptoms'])}")
        if e.get("products_used"):
            lines.append(f"  使用: {', '.join(e['products_used'])}")
        if e.get("sleep_hours") is not None:
            lines.append(f"  睡眠: {e['sleep_hours']}時間")
        if e.get("stress_level_1to5") is not None:
            lines.append(f"  ストレス: {e['stress_level_1to5']}/5")
        lines.append("")
    return "\n".join(lines).rstrip()

# ---------------------------------------------------------
# 症状正規化・テンプレ提案
# ---------------------------------------------------------
SYMPTOM_ALIASES = {
    "乾燥": ["乾燥", "つっぱり", "皮むけ"],
    "赤み": ["赤み", "ヒリつき", "ひりつき", "かゆみ"],
    "ベタつき": ["ベタつき", "てかり"],
}

def normalize_symptoms_from_text(text: str) -> List[str]:
    found = []
    for canonical, aliases in SYMPTOM_ALIASES.items():
        if any(a in text for a in aliases):
            found.append(canonical)
    return found

def normalize_skin_type_from_text(text: str) -> Optional[str]:
    mapping = {
        "乾燥肌": "乾燥", "乾燥": "乾燥",
        "敏感肌": "敏感", "敏感": "敏感",
        "混合肌": "混合", "混合": "混合",
        "脂性肌": "脂性", "脂性": "脂性", "オイリー": "脂性",
    }
    for k, v in mapping.items():
        if k in text:
            return v
    return None

def get_recent_symptoms_from_journal(limit: int = 7) -> List[str]:
    entries = list_skin_journal(limit=limit)
    count: Dict[str, int] = {"乾燥": 0, "赤み": 0, "ベタつき": 0}
    for e in entries:
        joined = " ".join(e.get("symptoms") or [])
        for s in normalize_symptoms_from_text(joined):
            count[s] += 1
    return [k for k, v in sorted(count.items(), key=lambda x: x[1], reverse=True) if v > 0]

def symptom_template(symptom: str) -> str:
    if symptom == "乾燥":
        return (
            "【乾燥テンプレ】\n"
            "要点:\n- 洗いすぎ・摩擦・高温を避けて保湿を薄く重ねる\n\n"
            "朝:\n- ぬるま湯 or 低刺激洗顔\n- 化粧水\n- 乳液/クリーム\n- 日焼け止め\n\n"
            "夜:\n- クレンジング（必要時のみ）\n- 低刺激洗顔\n- 化粧水\n- 保湿美容液（あれば）\n- クリーム\n\n"
            "注意:\n- 強い角質ケアの連日使用を避ける\n- 熱いお湯を避ける"
        )
    if symptom == "赤み":
        return (
            "【赤みテンプレ】\n"
            "要点:\n- まず刺激を減らす。新規アイテムを増やしすぎない\n\n"
            "朝:\n- ぬるま湯 or 超低刺激洗顔\n- シンプルな化粧水\n- 乳液/クリーム（薄め）\n- 低刺激寄りの日焼け止め\n\n"
            "夜:\n- クレンジング（必要時のみ・短時間）\n- 低刺激洗顔\n- 化粧水\n- シンプル保湿\n\n"
            "注意:\n- スクラブ/強いピーリング/摩擦を避ける"
        )
    if symptom == "ベタつき":
        return (
            "【ベタつきテンプレ】\n"
            "要点:\n- 取りすぎず、軽い保湿でバランス調整\n\n"
            "朝:\n- 洗顔（皮脂が気になる日は使用）\n- 化粧水\n- 軽い保湿\n- 日焼け止め（軽め）\n\n"
            "夜:\n- クレンジング（必要時のみ）\n- 洗顔\n- 化粧水\n- 軽い保湿\n\n"
            "注意:\n- 保湿ゼロにしない\n- 角質ケアは週1〜2回から"
        )
    return f"テンプレ未対応: {symptom}"

def format_symptom_templates(symptoms: List[str]) -> str:
    if not symptoms:
        return "症状が読み取れませんでした。例: 症状別テンプレ 乾燥 / 赤み / ベタつき"
    lines = ["症状別テンプレ提案:", "- 対象: " + " / ".join(symptoms), ""]
    for i, s in enumerate(symptoms):
        if i > 0:
            lines.append("")
        lines.append(symptom_template(s))
    return "\n".join(lines)

# ---------------------------------------------------------
# 朝/夜ルーティン自動作成（ローカル）
# ---------------------------------------------------------
def parse_time_budget(text: str) -> Tuple[int, int]:
    morning = 3
    night = 8
    m1 = re.search(r"朝\s*([0-9]+)\s*分", text)
    m2 = re.search(r"夜\s*([0-9]+)\s*分", text)
    if m1:
        morning = max(1, min(int(m1.group(1)), 30))
    if m2:
        night = max(1, min(int(m2.group(1)), 60))
    return morning, night

def build_morning_steps(symptoms: List[str], minutes: int) -> List[str]:
    dryness = "乾燥" in symptoms
    redness = "赤み" in symptoms
    oily = "ベタつき" in symptoms

    if minutes <= 2:
        return ["ぬるま湯ですすぐ（皮脂多い日は低刺激洗顔）", "軽い保湿", "日焼け止め"]

    steps = []
    steps.append("ぬるま湯 or 低刺激洗顔" if redness else "洗顔（乾燥が強い朝はぬるま湯でも可）")
    steps.append("化粧水")
    if dryness:
        if minutes >= 4:
            steps.append("保湿美容液（あれば）")
        steps.append("乳液 or クリーム")
    elif oily:
        steps.append("軽い保湿（ジェル/軽い乳液）")
    else:
        steps.append("乳液（少量）")
    steps.append("日焼け止め")
    return steps

def build_night_steps(symptoms: List[str], minutes: int) -> List[str]:
    dryness = "乾燥" in symptoms
    redness = "赤み" in symptoms
    oily = "ベタつき" in symptoms

    steps = ["クレンジング（必要な日だけ）", "洗顔（やさしく）", "化粧水"]
    if dryness:
        if minutes >= 8:
            steps.append("保湿美容液")
        steps.append("乳液")
        steps.append("クリーム（乾燥部位中心）")
    elif redness:
        steps.append("シンプル保湿（乳液 or クリーム）")
    elif oily:
        steps.append("軽い保湿（ジェル/軽い乳液）")
        if minutes >= 10:
            steps.append("角質ケアは週1〜2回から（別日・様子見）")
    else:
        steps.append("美容液（任意）")
        steps.append("乳液 or クリーム")
    return steps

def routine_cautions(symptoms: List[str]) -> List[str]:
    cautions = []
    if "赤み" in symptoms:
        cautions += ["赤みがある時は新しい美容液を一気に増やさない。", "スクラブ・強いピーリング・摩擦を避ける。"]
    if "乾燥" in symptoms:
        cautions += ["熱いお湯と洗いすぎに注意。", "保湿は薄く重ねる。"]
    if "ベタつき" in symptoms:
        cautions += ["保湿ゼロにしない。軽い保湿で量を調整。"]
    cautions.append("強い赤み・痛み・腫れ・化膿・急な悪化があれば皮膚科へ。")
    return cautions

def generate_offline_routine(user_text: str) -> Dict[str, Any]:
    morning_min, night_min = parse_time_budget(user_text)
    symptoms = normalize_symptoms_from_text(user_text)
    source = "入力文"

    if not symptoms:
        recent = get_recent_symptoms_from_journal(limit=7)
        symptoms = recent[:2]
        if symptoms:
            source = "最近の日記"
    if not symptoms:
        symptoms = ["乾燥"]
        source = "既定（症状未指定）"

    morning_steps = build_morning_steps(symptoms, morning_min)
    night_steps = build_night_steps(symptoms, night_min)

    return {
        "symptoms": symptoms,
        "symptom_source": source,
        "morning_min": morning_min,
        "night_min": night_min,
        "morning_steps": morning_steps,
        "night_steps": night_steps,
        "cautions": routine_cautions(symptoms),
    }

def format_routine(r: Dict[str, Any]) -> str:
    lines = []
    lines.append("朝/夜ルーティン自動作成（ローカル版）")
    lines.append(f"- 想定症状: {' / '.join(r['symptoms'])}（参照: {r['symptom_source']}）")
    lines.append(f"- 時間目安: 朝{r['morning_min']}分 / 夜{r['night_min']}分")
    lines.append("")
    lines.append("【朝ルーティン】")
    for i, s in enumerate(r["morning_steps"], 1):
        lines.append(f"{i}. {s}")
    lines.append("")
    lines.append("【夜ルーティン】")
    for i, s in enumerate(r["night_steps"], 1):
        lines.append(f"{i}. {s}")
    lines.append("")
    lines.append("【注意点】")
    for c in r["cautions"]:
        lines.append(f"- {c}")
    return "\n".join(lines)

# ---------------------------------------------------------
# ローカル商品おすすめ
# ---------------------------------------------------------
CATEGORY_ORDER = ["洗顔", "化粧水", "美容液", "乳液", "クリーム", "日焼け止め"]

def parse_budget_jpy(text: str) -> Optional[int]:
    m = re.search(r"予算\s*([0-9,]+)\s*円", text)
    if m:
        return int(m.group(1).replace(",", ""))
    m = re.search(r"([0-9,]+)\s*円", text)
    # 「予算」なくても円があれば拾う（誤爆回避弱め）
    if m and ("おすすめ" in text or "商品" in text):
        return int(m.group(1).replace(",", ""))
    return None

def wants_fragrance_free(text: str) -> bool:
    return ("無香料" in text) or ("香料なし" in text) or ("香りなし" in text)

def wants_alcohol_free(text: str) -> bool:
    return ("アルコールなし" in text) or ("アルコールフリー" in text)

def estimate_monthly_cost(item: Dict[str, Any]) -> int:
    price = float(item.get("price_jpy", 0) or 0)
    months = float(item.get("months_last", 1) or 1)
    if months <= 0:
        months = 1
    return round(price / months)

def score_product(item: Dict[str, Any], symptoms: List[str], skin_type: Optional[str], fragrance_free: bool, alcohol_free: bool) -> Tuple[int, List[str]]:
    score = 0
    reasons = []

    if fragrance_free and not item.get("fragrance_free", False):
        return (-999, ["無香料条件に不一致"])
    if alcohol_free and not item.get("alcohol_free", False):
        return (-999, ["アルコールフリー条件に不一致"])

    if skin_type and skin_type in (item.get("skin_types") or []):
        score += 2
        reasons.append(f"肌質相性({skin_type})")

    good_for = item.get("good_for") or []
    avoid_if = item.get("avoid_if") or []

    for s in symptoms:
        if s in good_for:
            score += 3
            reasons.append(f"{s}向け")
        if s in avoid_if:
            score -= 4
            reasons.append(f"{s}時は注意")

    # 低刺激/シンプルなどのタグ加点（赤み優先）
    tags = item.get("tags") or []
    notes = item.get("notes", "")
    if "赤み" in symptoms and ("低刺激" in tags or "シンプル" in tags or "低刺激" in notes):
        score += 2
        reasons.append("赤み時に低刺激寄り")
    if "乾燥" in symptoms and ("保湿" in tags or "高保湿" in tags):
        score += 2
        reasons.append("保湿寄り")
    if "ベタつき" in symptoms and ("軽い" in tags or "さっぱり" in tags):
        score += 2
        reasons.append("軽い使用感寄り")

    return (score, reasons)

def recommend_products_local(
    user_text: str,
    routine: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    products = load_products()
    skin_type = normalize_skin_type_from_text(user_text)

    symptoms = normalize_symptoms_from_text(user_text)
    if not symptoms and routine:
        symptoms = routine.get("symptoms", [])
    if not symptoms:
        symptoms = get_recent_symptoms_from_journal(limit=7)[:2]
    if not symptoms:
        symptoms = ["乾燥"]

    budget = parse_budget_jpy(user_text)
    ff = wants_fragrance_free(user_text)
    af = wants_alcohol_free(user_text)

    ranked_by_cat: Dict[str, List[Dict[str, Any]]] = {c: [] for c in CATEGORY_ORDER}
    for p in products:
        cat = p.get("category")
        if cat not in ranked_by_cat:
            continue
        score, reasons = score_product(p, symptoms, skin_type, ff, af)
        if score <= -999:
            continue
        row = dict(p)
        row["_score"] = score
        row["_reasons"] = reasons
        row["_monthly_cost_jpy"] = estimate_monthly_cost(p)
        ranked_by_cat[cat].append(row)

    for cat in ranked_by_cat:
        ranked_by_cat[cat].sort(key=lambda x: (x["_score"], -x["_monthly_cost_jpy"]), reverse=True)

    # 基本セット候補（1カテゴリ1件）
    selected = []
    categories_needed = ["洗顔", "化粧水", "日焼け止め"]
    # 症状に応じて追加カテゴリ
    if "乾燥" in symptoms or "赤み" in symptoms:
        categories_needed += ["乳液", "クリーム"]
    else:
        categories_needed += ["乳液"]
    # 美容液は任意
    categories_needed += ["美容液"]

    seen_cat = set()
    for cat in categories_needed:
        if cat in seen_cat:
            continue
        seen_cat.add(cat)
        cands = ranked_by_cat.get(cat, [])
        if cands:
            selected.append(cands[0])

    total_monthly = sum(x["_monthly_cost_jpy"] for x in selected)

    # 予算がある場合、削減調整（優先度低いものから外す）
    removed = []
    if budget is not None and total_monthly > budget:
        # 美容液 → クリーム（ベタつき時）→ 乳液の順で削るなど
        priority_remove = ["美容液", "クリーム", "乳液"]
        for cat in priority_remove:
            if total_monthly <= budget:
                break
            for i, item in enumerate(selected):
                if item["category"] == cat:
                    removed.append(selected.pop(i))
                    total_monthly = sum(x["_monthly_cost_jpy"] for x in selected)
                    break

    return {
        "symptoms": symptoms,
        "skin_type": skin_type,
        "budget_jpy": budget,
        "fragrance_free": ff,
        "alcohol_free": af,
        "selected": selected,
        "removed_for_budget": removed,
        "total_estimated_monthly_jpy": total_monthly,
        "catalog_count": len(products),
    }

def format_product_recommendation(rec: Dict[str, Any]) -> str:
    lines = []
    lines.append("ローカル商品おすすめ（参考候補）")
    lines.append(f"- 症状: {' / '.join(rec['symptoms'])}")
    lines.append(f"- 肌質: {rec['skin_type'] or '未指定'}")
    lines.append(f"- 条件: 無香料={'あり' if rec['fragrance_free'] else '指定なし'} / アルコールフリー={'あり' if rec['alcohol_free'] else '指定なし'}")
    lines.append(f"- 月額目安合計: 約{rec['total_estimated_monthly_jpy']}円" + (f"（予算 {rec['budget_jpy']}円）" if rec['budget_jpy'] else ""))
    lines.append("")

    if not rec["selected"]:
        lines.append("候補が見つかりませんでした。条件を少し緩めてください（例: 無香料条件を外す）。")
        return "\n".join(lines)

    lines.append("【おすすめ候補】")
    for item in rec["selected"]:
        reasons = " / ".join(item.get("_reasons") or []) or "条件一致"
        lines.append(
            f"- {item['category']}: {item['name']} "
            f"(税込目安 {item['price_jpy']}円 / 月額換算 約{item['_monthly_cost_jpy']}円)"
        )
        lines.append(f"  理由: {reasons}")
        if item.get("notes"):
            lines.append(f"  メモ: {item['notes']}")

    if rec["removed_for_budget"]:
        lines.append("")
        lines.append("【予算調整で外した候補】")
        for item in rec["removed_for_budget"]:
            lines.append(f"- {item['category']}: {item['name']}（月額換算 約{item['_monthly_cost_jpy']}円）")

    lines.append("")
    lines.append("※ ローカルDBベースの参考提案です。実商品の成分・価格・在庫は店頭/公式情報で確認してください。")
    return "\n".join(lines)

# ---------------------------------------------------------
# ルーティン + 商品セット提案
# ---------------------------------------------------------
def format_routine_plus_products(user_text: str) -> str:
    routine = generate_offline_routine(user_text)
    rec = recommend_products_local(user_text, routine=routine)
    return format_routine(routine) + "\n\n" + format_product_recommendation(rec)

# ---------------------------------------------------------
# コマンド判定
# ---------------------------------------------------------
def try_load_allergies_from_profile() -> Optional[List[str]]:
    profile = read_json(PROFILE_PATH, {})
    if isinstance(profile, dict):
        allergies = profile.get("allergies")
        if isinstance(allergies, list):
            return [str(x) for x in allergies]
    return None

def extract_ingredients_text(user_text: str) -> Optional[str]:
    patterns = [
        r"成分チェックして[:：]?\s*(.+)$",
        r"成分チェック[:：]\s*(.+)$",
        r"成分[:：]\s*(.+)$",
    ]
    for p in patterns:
        m = re.search(p, user_text.strip(), flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None

def is_journal_save_request(user_text: str) -> bool:
    t = user_text
    return ("日記" in t and "保存" in t) or ("肌日記" in t) or ("記録して" in t)

def parse_journal_list_limit(user_text: str) -> int:
    m = re.search(r"日記一覧\s*([0-9]+)", user_text)
    if m:
        return max(1, min(int(m.group(1)), 30))
    return 7

def is_journal_list_request(user_text: str) -> bool:
    return ("日記一覧" in user_text) or ("最近の肌日記" in user_text and "傾向" not in user_text)

def is_journal_trend_request(user_text: str) -> bool:
    return ("傾向" in user_text and "日記" in user_text) or ("最近の肌日記を見て傾向" in user_text)

def is_symptom_template_request(user_text: str) -> bool:
    return ("症状別テンプレ" in user_text) or ("テンプレ提案" in user_text and any(k in user_text for k in ["乾燥", "赤み", "ベタつき", "てかり"]))

def extract_template_symptoms(user_text: str) -> List[str]:
    symptoms = normalize_symptoms_from_text(user_text)
    if not symptoms and "症状別テンプレ" in user_text:
        symptoms = ["乾燥", "赤み", "ベタつき"]
    return symptoms

def is_routine_request(user_text: str) -> bool:
    has_routine_word = ("ルーティン" in user_text)
    has_make_word = any(w in user_text for w in ["作って", "作成", "提案", "組んで"])
    return has_routine_word and has_make_word

def is_product_recommend_request(user_text: str) -> bool:
    return ("商品おすすめ" in user_text) or ("おすすめ商品" in user_text) or ("商品提案" in user_text)

def is_routine_plus_product_request(user_text: str) -> bool:
    return (
        ("ルーティン" in user_text and "商品" in user_text and any(w in user_text for w in ["おすすめ", "提案"]))
        or ("ルーティン＋商品" in user_text)
    )

def is_product_list_request(user_text: str) -> bool:
    return ("商品一覧" in user_text) or ("ローカル商品一覧" in user_text)

def format_product_list() -> str:
    products = load_products()
    if not products:
        return "ローカル商品DBが空です。"
    lines = [f"ローカル商品一覧（{len(products)}件）:"]
    for p in products:
        monthly = estimate_monthly_cost(p)
        lines.append(
            f"- {p['id']} | {p['category']} | {p['name']} | 価格 {p['price_jpy']}円 | 月額換算 約{monthly}円 | 無香料={'○' if p.get('fragrance_free') else '×'}"
        )
    lines.append("")
    lines.append(f"編集ファイル: {PRODUCTS_PATH}")
    return "\n".join(lines)

# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------
HELP_TEXT = f"""
使い方（ローカル完全版 / API不要）
■ 成分チェック
- 成分チェックして Water, Glycerin, Niacinamide, Fragrance, Limonene

■ 肌日記保存（自然文OK）
- 今日は少し赤みと乾燥あり 睡眠5時間 ストレス4 化粧水と美容液を使った 肌日記として保存して

■ 日記一覧 / 傾向
- 日記一覧
- 日記一覧 5
- 最近の肌日記を見て傾向を教えて

■ 症状別テンプレ提案
- 症状別テンプレ 乾燥
- 症状別テンプレ 赤み ベタつき

■ 朝/夜ルーティン自動作成（ローカル）
- 朝夜ルーティン作って 乾燥 朝3分 夜10分
- ルーティン提案 赤み 朝2分 夜8分
- 朝夜ルーティン作って（症状未指定なら最近の日記から推定）

■ ローカル商品おすすめ（症状/肌質/予算/無香料）
- 商品おすすめ 乾燥 無香料 予算5000円
- おすすめ商品 赤み 敏感肌 無香料 アルコールフリー 予算7000円
- 商品提案 ベタつき 混合肌

■ ルーティン + 商品セット提案
- ルーティンと商品おすすめ 乾燥 朝3分 夜10分 無香料 予算6000円

■ ローカル商品DB確認
- 商品一覧
  （編集ファイル: {PRODUCTS_PATH}）

■ 終了
- exit / quit
""".strip()

def main():
    ensure_local_products()
    print("美容AIエージェント（ローカル完全版）起動")
    print("※ API不要（成分チェック / 日記 / 症状テンプレ / ルーティン / 商品おすすめ）")
    print("終了: exit / quit")
    print("help で使い方")
    print()

    while True:
        try:
            user_text = input("あなた > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n終了します。")
            break

        if not user_text:
            continue

        if user_text.lower() in {"exit", "quit"}:
            print("終了します。")
            break

        if user_text.lower() in {"help", "?", "使い方"}:
            print_ai(HELP_TEXT)
            continue

        # 1) 成分チェック
        ingredients = extract_ingredients_text(user_text)
        if ingredients:
            allergies = try_load_allergies_from_profile()
            result = analyze_ingredients_rule_based(ingredients, allergies)
            print_ai(format_ingredient_result(result))
            continue

        # 2) 日記傾向
        if is_journal_trend_request(user_text):
            print_ai(journal_summary(list_skin_journal(limit=7)))
            continue

        # 3) 日記一覧
        if is_journal_list_request(user_text):
            print_ai(format_journal_entries(list_skin_journal(limit=parse_journal_list_limit(user_text))))
            continue

        # 4) 日記保存
        if is_journal_save_request(user_text):
            saved = save_skin_journal(parse_journal_text(user_text))
            msg = (
                "日記を保存しました\n"
                f"- 日付: {saved.get('date')}\n"
                f"- 要約: {saved.get('condition_summary')}\n"
                f"- 症状: {', '.join(saved.get('symptoms') or []) or 'なし'}\n"
                f"- 使用: {', '.join(saved.get('products_used') or []) or 'なし'}\n"
                f"- 睡眠: {saved.get('sleep_hours') if saved.get('sleep_hours') is not None else '未記録'}\n"
                f"- ストレス: {saved.get('stress_level_1to5') if saved.get('stress_level_1to5') is not None else '未記録'}"
            )
            print_ai(msg)
            continue

        # 5) 症状別テンプレ
        if is_symptom_template_request(user_text):
            print_ai(format_symptom_templates(extract_template_symptoms(user_text)))
            continue

        # 6) ルーティン + 商品セット
        if is_routine_plus_product_request(user_text):
            print_ai(format_routine_plus_products(user_text))
            continue

        # 7) ローカル商品おすすめ
        if is_product_recommend_request(user_text):
            print_ai(format_product_recommendation(recommend_products_local(user_text)))
            continue

        # 8) 商品一覧
        if is_product_list_request(user_text):
            print_ai(format_product_list())
            continue

        # 9) ルーティン作成
        if is_routine_request(user_text):
            print_ai(format_routine(generate_offline_routine(user_text)))
            continue

        # 10) その他
        print_ai("使える機能 → 成分チェック / 肌日記保存 / 日記一覧 / 傾向 / 症状別テンプレ / 朝夜ルーティン / 商品おすすめ")
        print_ai("例: 商品おすすめ 乾燥 無香料 予算5000円")
        print_ai("例: ルーティンと商品おすすめ 赤み 朝2分 夜8分 無香料 予算6000円")

if __name__ == "__main__":
    main()