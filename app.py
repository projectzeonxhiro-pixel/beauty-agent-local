# app.py
# Beauty Agent Local - Multilingual / Pink+Gold / EC-style Cards / Offline Local Version
# Run:
#   python -m streamlit run app.py

import json
import re
from datetime import datetime, date
from html import escape
from pathlib import Path
from typing import Any, Dict, List, Tuple

import streamlit as st

# =========================
# Paths / Local Storage
# =========================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "beauty_agent_data"
DIARY_FILE = DATA_DIR / "skin_diary.json"
PRODUCTS_FILE = DATA_DIR / "products_local.json"


# =========================
# i18n (Japanese / English / Korean / Chinese)
# =========================
I18N: Dict[str, Dict[str, str]] = {
    "ja": {
        "app_title": "Beauty Agent Local",
        "app_subtitle": "女性向けセルフケアWeb版",
        "app_desc": "API不要 / ローカル保存 / 成分チェック・日記・傾向・ルーティン・症状別テンプレ・ローカル商品提案",
        "badge": "streamlitApp • ローカル保存対応",
        "lang": "言語",
        "profile": "プロフィール",
        "profile_desc": "あなた向けに提案をやさしく最適化します",
        "skin_type": "肌タイプ",
        "concerns": "悩み",
        "fragrance_pref": "香りの好み",
        "monthly_budget": "月予算（円）",
        "am_minutes": "朝ケア時間（分）",
        "pm_minutes": "夜ケア時間（分）",
        "logo_frame": "ロゴ（任意）",
        "logo_help": "PNG/JPGをアップロードするとヘッダーに表示します",
        "tabs_ingredient": "成分チェック",
        "tabs_diary": "肌日記（保存/一覧）",
        "tabs_trend": "傾向メモ",
        "tabs_routine": "朝/夜ルーティン",
        "tabs_template": "症状別テンプレ",
        "tabs_products": "ローカル商品提案",
        "stat_records": "記録件数",
        "stat_avg_sleep": "平均睡眠",
        "stat_avg_stress": "平均ストレス",
        "not_recorded": "未記録",
        "daily_ok": "毎日1行でもOK",
        "ingredient_title": "成分チェック（ルールベース簡易）",
        "ingredient_desc": "成分を貼るだけで、香料・香料アレルゲン・乾燥しやすいアルコールなどをざっくり確認できます。",
        "ingredient_input_label": "成分を貼り付け（カンマ区切り / 改行OK）",
        "ingredient_placeholder": "Water, Glycerin, Niacinamide, Fragrance, Limonene",
        "check_button": "チェックする",
        "detected_categories": "検出カテゴリ",
        "warnings": "注意点",
        "notes": "メモ",
        "no_ingredient": "成分を入力してください。",
        "diary_title": "肌日記（ローカル保存）",
        "diary_desc": "その日の肌状態を記録して、あとで傾向を見返せます。",
        "record_date": "日付",
        "symptoms": "症状",
        "sleep_hours": "睡眠時間",
        "stress_level": "ストレス",
        "used_items": "使用アイテム",
        "memo": "メモ",
        "save_diary": "日記を保存",
        "saved_ok": "保存しました",
        "diary_list": "日記一覧",
        "no_diary": "日記はまだありません。",
        "trend_title": "簡易傾向メモ（ローカル集計）",
        "trend_desc": "保存した日記から、睡眠・ストレス・症状の出やすさを確認します。",
        "trend_summary": "簡易傾向メモ",
        "routine_title": "朝/夜ルーティン自動作成（ローカル）",
        "routine_desc": "プロフィール条件と悩みから、時間内に収まるシンプルなケア手順を作成します。",
        "make_routine": "ルーティンを作成",
        "routine_note": "「ルーティンを作成」を押すと、プロフィール条件からローカル生成します。",
        "am_routine": "朝ルーティン",
        "pm_routine": "夜ルーティン",
        "template_title": "症状別テンプレ提案（乾燥 / 赤み / ベタつき）",
        "template_desc": "症状に合わせたケアの考え方テンプレを表示します（一般的なセルフケア向け）。",
        "choose_symptom": "症状を選択",
        "template_am": "朝のポイント",
        "template_pm": "夜のポイント",
        "template_avoid": "避けたいこと",
        "template_when_to_hospital": "受診目安",
        "products_title": "ローカル商品DBからの提案（EC風カード）",
        "products_desc": "ローカルDBを条件で絞って提案します（実在ブランド縛りなし / オフライン用）。",
        "recommend_button": "おすすめを表示",
        "price": "価格",
        "tags": "タグ",
        "steps": "手順",
        "minutes": "分",
        "yen": "円",
        "empty_result": "条件に合う候補が見つかりませんでした。条件を少し緩めてください。",
        "footer_note": "※ これはローカル簡易版です。最終判断は製品ラベル・メーカー情報・専門家確認を優先してください。",
        "skin_normal": "普通肌",
        "skin_dry": "乾燥肌",
        "skin_oily": "脂性肌",
        "skin_combo": "混合肌",
        "skin_sensitive": "敏感肌",
        "skin_unknown": "未設定",
        "fragrance_any": "未設定",
        "fragrance_none": "無香料希望",
        "fragrance_light": "ほのかな香りOK",
        "fragrance_like": "香り重視",
        "concern_dryness": "乾燥",
        "concern_redness": "赤み",
        "concern_oiliness": "ベタつき",
        "concern_pores": "毛穴",
        "concern_dullness": "くすみ",
        "concern_acne": "ニキビ",
        "concern_sensitivity": "刺激感",
        "symptom_none": "なし",
        "save_hint": "例: 赤み, 乾燥 / ヒリつき など",
        "used_items_placeholder": "例: 化粧水 / 美容液 / 乳液",
        "memo_placeholder": "例: マスク時間が長かった / 睡眠不足 / 生理前など",
        "analysis_result": "結果",
        "category_fragrance": "香料",
        "category_allergen": "香料アレルゲン（精油由来を含む）",
        "category_drying_alcohol": "乾燥しやすいアルコール",
        "category_humectant": "保湿成分",
        "category_soothing": "整肌・鎮静寄り",
        "category_brightening": "透明感ケア系",
        "category_exfoliant": "角質ケア系",
        "category_active": "攻め成分",
        "warn_patchtest": "香料/香料アレルゲンの可能性。敏感な方はパッチテスト推奨。",
        "warn_alcohol": "アルコールでしみや乾燥を感じる人は様子見を。",
        "warn_active": "攻め成分が複数ある場合は、頻度を調整して使い分けを。",
        "note_rulebased": "これはルールベースの簡易チェックです。最終判断は製品ラベル・メーカー情報・専門家確認を優先。",
        "product_type_cleanser": "洗顔",
        "product_type_lotion": "化粧水",
        "product_type_serum": "美容液",
        "product_type_moisturizer": "乳液/クリーム",
        "product_type_sunscreen": "日焼け止め",
        "product_type_spot": "部分用ケア",
        "cta_try": "この条件で試す",
        "product_card_note": "ローカルDB提案（テスト用）",
        "lang_ja": "日本語",
        "lang_en": "English",
        "lang_ko": "한국어",
        "lang_zh": "中文",
    },
    "en": {
        "app_title": "Beauty Agent Local",
        "app_subtitle": "Women-Focused Self-Care Web App",
        "app_desc": "No API / Local save / Ingredient check, diary, trends, routine, symptom templates, local product suggestions",
        "badge": "streamlitApp • Local Storage",
        "lang": "Language",
        "profile": "Profile",
        "profile_desc": "Gently tailors suggestions to your preferences",
        "skin_type": "Skin type",
        "concerns": "Concerns",
        "fragrance_pref": "Fragrance preference",
        "monthly_budget": "Monthly budget (JPY)",
        "am_minutes": "AM care time (min)",
        "pm_minutes": "PM care time (min)",
        "logo_frame": "Logo (optional)",
        "logo_help": "Upload PNG/JPG to show in the header",
        "tabs_ingredient": "Ingredient Check",
        "tabs_diary": "Skin Diary",
        "tabs_trend": "Trend Memo",
        "tabs_routine": "AM/PM Routine",
        "tabs_template": "Symptom Templates",
        "tabs_products": "Local Product Picks",
        "stat_records": "Records",
        "stat_avg_sleep": "Avg Sleep",
        "stat_avg_stress": "Avg Stress",
        "not_recorded": "No data",
        "daily_ok": "Even one line per day is enough",
        "ingredient_title": "Ingredient Check (Rule-based quick scan)",
        "ingredient_desc": "Paste an ingredient list to quickly check fragrance, fragrance allergens, drying alcohols, and more.",
        "ingredient_input_label": "Paste ingredients (comma-separated / new lines OK)",
        "ingredient_placeholder": "Water, Glycerin, Niacinamide, Fragrance, Limonene",
        "check_button": "Check",
        "detected_categories": "Detected categories",
        "warnings": "Warnings",
        "notes": "Notes",
        "no_ingredient": "Please enter ingredients.",
        "diary_title": "Skin Diary (Local Save)",
        "diary_desc": "Log your daily skin condition and review later.",
        "record_date": "Date",
        "symptoms": "Symptoms",
        "sleep_hours": "Sleep hours",
        "stress_level": "Stress",
        "used_items": "Used items",
        "memo": "Memo",
        "save_diary": "Save diary",
        "saved_ok": "Saved",
        "diary_list": "Diary list",
        "no_diary": "No diary entries yet.",
        "trend_title": "Quick Trend Memo (Local aggregation)",
        "trend_desc": "Review sleep, stress, and symptom frequency from your saved diary.",
        "trend_summary": "Quick Trend Memo",
        "routine_title": "AM/PM Routine Generator (Local)",
        "routine_desc": "Creates a simple routine within your time budget based on profile + concerns.",
        "make_routine": "Generate routine",
        "routine_note": "Press “Generate routine” to create a local routine from your profile settings.",
        "am_routine": "AM Routine",
        "pm_routine": "PM Routine",
        "template_title": "Symptom Templates (Dryness / Redness / Oiliness)",
        "template_desc": "Shows general self-care template ideas for each symptom.",
        "choose_symptom": "Choose symptom",
        "template_am": "AM tips",
        "template_pm": "PM tips",
        "template_avoid": "Avoid",
        "template_when_to_hospital": "When to see a doctor",
        "products_title": "Local Product Suggestions (EC-style cards)",
        "products_desc": "Filters a local product DB and shows suggestions (offline testing use).",
        "recommend_button": "Show recommendations",
        "price": "Price",
        "tags": "Tags",
        "steps": "Steps",
        "minutes": "min",
        "yen": "JPY",
        "empty_result": "No matches found. Try loosening your filters.",
        "footer_note": "This is a local simplified version. Final decisions should prioritize product labels, official manufacturer information, and professional advice.",
        "skin_normal": "Normal",
        "skin_dry": "Dry",
        "skin_oily": "Oily",
        "skin_combo": "Combination",
        "skin_sensitive": "Sensitive",
        "skin_unknown": "Not set",
        "fragrance_any": "Not set",
        "fragrance_none": "Fragrance-free preferred",
        "fragrance_light": "Light fragrance OK",
        "fragrance_like": "Fragrance-focused",
        "concern_dryness": "Dryness",
        "concern_redness": "Redness",
        "concern_oiliness": "Oiliness",
        "concern_pores": "Pores",
        "concern_dullness": "Dullness",
        "concern_acne": "Acne",
        "concern_sensitivity": "Sensitivity",
        "symptom_none": "None",
        "save_hint": "e.g. redness, dryness, stinging",
        "used_items_placeholder": "e.g. toner / serum / lotion",
        "memo_placeholder": "e.g. long mask wear / poor sleep / pre-period",
        "analysis_result": "Result",
        "category_fragrance": "Fragrance",
        "category_allergen": "Fragrance allergen / essential oil-related",
        "category_drying_alcohol": "Potentially drying alcohol",
        "category_humectant": "Humectants",
        "category_soothing": "Soothing / skin-conditioning",
        "category_brightening": "Tone-care ingredients",
        "category_exfoliant": "Exfoliant-related",
        "category_active": "Actives",
        "warn_patchtest": "Possible fragrance/fragrance allergens. Patch test is recommended if sensitive.",
        "warn_alcohol": "If alcohol tends to sting/dry your skin, monitor carefully.",
        "warn_active": "If multiple actives are combined, adjust frequency and layering.",
        "note_rulebased": "This is a rule-based quick check. Final decisions should prioritize product labels, manufacturer information, and expert advice.",
        "product_type_cleanser": "Cleanser",
        "product_type_lotion": "Toner",
        "product_type_serum": "Serum",
        "product_type_moisturizer": "Moisturizer",
        "product_type_sunscreen": "Sunscreen",
        "product_type_spot": "Spot Care",
        "cta_try": "Try with these settings",
        "product_card_note": "Local DB suggestion (test)",
        "lang_ja": "日本語",
        "lang_en": "English",
        "lang_ko": "한국어",
        "lang_zh": "中文",
    },
    "ko": {
        "app_title": "Beauty Agent Local",
        "app_subtitle": "여성 맞춤 셀프케어 웹앱",
        "app_desc": "API 불필요 / 로컬 저장 / 성분 체크·일기·경향·루틴·증상별 템플릿·로컬 상품 추천",
        "badge": "streamlitApp • 로컬 저장 지원",
        "lang": "언어",
        "profile": "프로필",
        "profile_desc": "취향에 맞게 제안을 부드럽게 맞춰줍니다",
        "skin_type": "피부 타입",
        "concerns": "고민",
        "fragrance_pref": "향 선호",
        "monthly_budget": "월 예산 (엔)",
        "am_minutes": "아침 케어 시간 (분)",
        "pm_minutes": "저녁 케어 시간 (분)",
        "logo_frame": "로고 (선택)",
        "logo_help": "PNG/JPG 업로드 시 헤더에 표시됩니다",
        "tabs_ingredient": "성분 체크",
        "tabs_diary": "피부 일기",
        "tabs_trend": "경향 메모",
        "tabs_routine": "아침/저녁 루틴",
        "tabs_template": "증상별 템플릿",
        "tabs_products": "로컬 상품 추천",
        "stat_records": "기록 수",
        "stat_avg_sleep": "평균 수면",
        "stat_avg_stress": "평균 스트레스",
        "not_recorded": "미기록",
        "daily_ok": "하루 한 줄만 기록해도 좋아요",
        "ingredient_title": "성분 체크 (룰베이스 간이)",
        "ingredient_desc": "성분표를 붙여 넣으면 향료, 향 알레르겐, 건조 유발 가능 알코올 등을 빠르게 확인합니다.",
        "ingredient_input_label": "성분 붙여넣기 (쉼표 / 줄바꿈 가능)",
        "ingredient_placeholder": "Water, Glycerin, Niacinamide, Fragrance, Limonene",
        "check_button": "체크하기",
        "detected_categories": "검출 카테고리",
        "warnings": "주의점",
        "notes": "메모",
        "no_ingredient": "성분을 입력해 주세요.",
        "diary_title": "피부 일기 (로컬 저장)",
        "diary_desc": "하루 피부 상태를 기록하고 나중에 경향을 확인할 수 있어요.",
        "record_date": "날짜",
        "symptoms": "증상",
        "sleep_hours": "수면 시간",
        "stress_level": "스트레스",
        "used_items": "사용 제품",
        "memo": "메모",
        "save_diary": "일기 저장",
        "saved_ok": "저장되었습니다",
        "diary_list": "일기 목록",
        "no_diary": "아직 일기 기록이 없습니다.",
        "trend_title": "간단 경향 메모 (로컬 집계)",
        "trend_desc": "저장된 일기에서 수면·스트레스·증상 빈도를 확인합니다.",
        "trend_summary": "간단 경향 메모",
        "routine_title": "아침/저녁 루틴 자동 생성 (로컬)",
        "routine_desc": "프로필과 고민을 바탕으로 시간 안에 가능한 간단한 루틴을 만듭니다.",
        "make_routine": "루틴 생성",
        "routine_note": "‘루틴 생성’ 버튼을 누르면 프로필 조건으로 로컬 루틴을 생성합니다.",
        "am_routine": "아침 루틴",
        "pm_routine": "저녁 루틴",
        "template_title": "증상별 템플릿 제안 (건조 / 홍조 / 번들거림)",
        "template_desc": "증상에 맞는 일반적인 셀프케어 템플릿을 보여줍니다.",
        "choose_symptom": "증상 선택",
        "template_am": "아침 포인트",
        "template_pm": "저녁 포인트",
        "template_avoid": "피하면 좋은 것",
        "template_when_to_hospital": "진료 권장 기준",
        "products_title": "로컬 상품 DB 추천 (EC 스타일 카드)",
        "products_desc": "로컬 DB를 조건으로 필터링해 제안합니다 (오프라인 테스트용).",
        "recommend_button": "추천 보기",
        "price": "가격",
        "tags": "태그",
        "steps": "단계",
        "minutes": "분",
        "yen": "엔",
        "empty_result": "조건에 맞는 후보가 없습니다. 조건을 조금 완화해 주세요.",
        "footer_note": "※ 로컬 간이 버전입니다. 최종 판단은 제품 라벨·제조사 정보·전문가 상담을 우선하세요.",
        "skin_normal": "중성",
        "skin_dry": "건성",
        "skin_oily": "지성",
        "skin_combo": "복합성",
        "skin_sensitive": "민감성",
        "skin_unknown": "미설정",
        "fragrance_any": "미설정",
        "fragrance_none": "무향 선호",
        "fragrance_light": "은은한 향 OK",
        "fragrance_like": "향 중시",
        "concern_dryness": "건조",
        "concern_redness": "홍조",
        "concern_oiliness": "번들거림",
        "concern_pores": "모공",
        "concern_dullness": "칙칙함",
        "concern_acne": "트러블",
        "concern_sensitivity": "자극감",
        "symptom_none": "없음",
        "save_hint": "예: 홍조, 건조, 따가움",
        "used_items_placeholder": "예: 토너 / 세럼 / 로션",
        "memo_placeholder": "예: 마스크 오래 착용 / 수면 부족 / 생리 전",
        "analysis_result": "결과",
        "category_fragrance": "향료",
        "category_allergen": "향료 알레르겐 / 에센셜오일 관련",
        "category_drying_alcohol": "건조 유발 가능 알코올",
        "category_humectant": "보습 성분",
        "category_soothing": "진정 / 피부컨디셔닝",
        "category_brightening": "톤 케어 성분",
        "category_exfoliant": "각질 케어 관련",
        "category_active": "활성 성분",
        "warn_patchtest": "향료/향 알레르겐 가능성. 민감한 경우 패치 테스트 권장.",
        "warn_alcohol": "알코올에 따가움/건조를 느끼는 편이면 주의 깊게 사용하세요.",
        "warn_active": "활성 성분이 여러 개면 사용 빈도와 레이어링을 조절하세요.",
        "note_rulebased": "룰베이스 간이 체크입니다. 최종 판단은 라벨/제조사 정보/전문가 상담을 우선하세요.",
        "product_type_cleanser": "클렌저",
        "product_type_lotion": "토너",
        "product_type_serum": "세럼",
        "product_type_moisturizer": "보습크림",
        "product_type_sunscreen": "선크림",
        "product_type_spot": "부분 케어",
        "cta_try": "이 조건으로 사용해보기",
        "product_card_note": "로컬 DB 추천 (테스트)",
        "lang_ja": "日本語",
        "lang_en": "English",
        "lang_ko": "한국어",
        "lang_zh": "中文",
    },
    "zh": {
        "app_title": "Beauty Agent Local",
        "app_subtitle": "女性向自我护理网页版",
        "app_desc": "无需API / 本地保存 / 成分检查、日记、趋势、护理流程、症状模板、本地商品推荐",
        "badge": "streamlitApp • 支持本地保存",
        "lang": "语言",
        "profile": "个人资料",
        "profile_desc": "根据你的偏好温和优化建议",
        "skin_type": "肤质",
        "concerns": "困扰",
        "fragrance_pref": "香味偏好",
        "monthly_budget": "月预算（日元）",
        "am_minutes": "早间护理时间（分钟）",
        "pm_minutes": "晚间护理时间（分钟）",
        "logo_frame": "Logo（可选）",
        "logo_help": "上传 PNG/JPG 后会显示在页眉",
        "tabs_ingredient": "成分检查",
        "tabs_diary": "肌肤日记",
        "tabs_trend": "趋势备忘",
        "tabs_routine": "早/晚护理流程",
        "tabs_template": "症状模板",
        "tabs_products": "本地商品推荐",
        "stat_records": "记录数",
        "stat_avg_sleep": "平均睡眠",
        "stat_avg_stress": "平均压力",
        "not_recorded": "未记录",
        "daily_ok": "每天写一行也可以",
        "ingredient_title": "成分检查（规则简版）",
        "ingredient_desc": "粘贴成分表即可快速查看香精、香料过敏原、可能偏干的酒精等。",
        "ingredient_input_label": "粘贴成分（逗号分隔 / 换行也可）",
        "ingredient_placeholder": "Water, Glycerin, Niacinamide, Fragrance, Limonene",
        "check_button": "开始检查",
        "detected_categories": "检测到的类别",
        "warnings": "注意事项",
        "notes": "备注",
        "no_ingredient": "请输入成分。",
        "diary_title": "肌肤日记（本地保存）",
        "diary_desc": "记录每日肌肤状态，后续查看趋势更方便。",
        "record_date": "日期",
        "symptoms": "症状",
        "sleep_hours": "睡眠时长",
        "stress_level": "压力",
        "used_items": "使用产品",
        "memo": "备注",
        "save_diary": "保存日记",
        "saved_ok": "已保存",
        "diary_list": "日记列表",
        "no_diary": "还没有日记记录。",
        "trend_title": "简易趋势备忘（本地汇总）",
        "trend_desc": "从已保存日记中查看睡眠、压力和症状频率。",
        "trend_summary": "简易趋势备忘",
        "routine_title": "早/晚护理流程自动生成（本地）",
        "routine_desc": "根据个人资料与困扰，在限定时间内生成简洁护理步骤。",
        "make_routine": "生成护理流程",
        "routine_note": "点击“生成护理流程”后，将根据个人资料条件在本地生成方案。",
        "am_routine": "早间流程",
        "pm_routine": "晚间流程",
        "template_title": "症状模板建议（干燥 / 泛红 / 出油）",
        "template_desc": "按症状显示常见自我护理思路模板。",
        "choose_symptom": "选择症状",
        "template_am": "早间重点",
        "template_pm": "晚间重点",
        "template_avoid": "尽量避免",
        "template_when_to_hospital": "就医参考",
        "products_title": "本地商品库推荐（电商风卡片）",
        "products_desc": "按条件筛选本地商品库并推荐（离线测试用）。",
        "recommend_button": "显示推荐",
        "price": "价格",
        "tags": "标签",
        "steps": "步骤",
        "minutes": "分钟",
        "yen": "日元",
        "empty_result": "没有找到符合条件的候选，请适当放宽筛选条件。",
        "footer_note": "※ 这是本地简化版。最终判断请优先参考产品标签、官方厂商信息和专业建议。",
        "skin_normal": "中性",
        "skin_dry": "干性",
        "skin_oily": "油性",
        "skin_combo": "混合性",
        "skin_sensitive": "敏感性",
        "skin_unknown": "未设置",
        "fragrance_any": "未设置",
        "fragrance_none": "偏好无香",
        "fragrance_light": "淡香可接受",
        "fragrance_like": "重视香味",
        "concern_dryness": "干燥",
        "concern_redness": "泛红",
        "concern_oiliness": "出油",
        "concern_pores": "毛孔",
        "concern_dullness": "暗沉",
        "concern_acne": "痘痘",
        "concern_sensitivity": "刺激感",
        "symptom_none": "无",
        "save_hint": "例：泛红、干燥、刺痛",
        "used_items_placeholder": "例：化妆水 / 精华 / 乳液",
        "memo_placeholder": "例：长时间戴口罩 / 睡眠不足 / 生理期前",
        "analysis_result": "结果",
        "category_fragrance": "香精/香料",
        "category_allergen": "香料过敏原 / 精油相关",
        "category_drying_alcohol": "可能偏干的酒精",
        "category_humectant": "保湿成分",
        "category_soothing": "舒缓/调理成分",
        "category_brightening": "提亮护理成分",
        "category_exfoliant": "去角质相关",
        "category_active": "功效成分",
        "warn_patchtest": "可能含香精/香料过敏原。敏感肌建议先做局部测试。",
        "warn_alcohol": "如果你对酒精容易刺痛/干燥，请谨慎观察使用感受。",
        "warn_active": "若同时含多个功效成分，建议调整频率与叠加方式。",
        "note_rulebased": "这是规则简版检查。最终判断请优先参考产品标签、厂商信息和专业建议。",
        "product_type_cleanser": "洁面",
        "product_type_lotion": "化妆水",
        "product_type_serum": "精华",
        "product_type_moisturizer": "乳液/面霜",
        "product_type_sunscreen": "防晒",
        "product_type_spot": "局部护理",
        "cta_try": "按此条件试用",
        "product_card_note": "本地数据库推荐（测试）",
        "lang_ja": "日本語",
        "lang_en": "English",
        "lang_ko": "한국어",
        "lang_zh": "中文",
    },
}


def t(key: str, lang: str) -> str:
    """Translate text by key with fallback to JA then key."""
    if lang in I18N and key in I18N[lang]:
        return I18N[lang][key]
    if key in I18N["ja"]:
        return I18N["ja"][key]
    return key


# =========================
# Local Data Initialization
# =========================
DEFAULT_PRODUCTS: List[Dict[str, Any]] = [
    {
        "id": "p001",
        "name": {
            "ja": "モイストバランス クレンジングフォーム",
            "en": "Moist Balance Cleansing Foam",
            "ko": "모이스트 밸런스 클렌징 폼",
            "zh": "水润平衡洁面泡沫",
        },
        "type": "cleanser",
        "price_jpy": 1380,
        "fragrance": "none",
        "skin_types": ["dry", "combo", "sensitive"],
        "concerns": ["dryness", "sensitivity", "redness"],
        "tags": ["低刺激", "アミノ酸系", "しっとり"],
        "emoji": "🫧",
        "steps": ["cleanse"],
        "texture": "foam",
        "description": {
            "ja": "やさしい洗浄でつっぱりにくい朝夜兼用の洗顔フォーム。",
            "en": "Gentle cleanser that minimizes tightness after washing.",
            "ko": "세안 후 당김을 줄이는 순한 클렌징 폼.",
            "zh": "温和清洁，降低洗后紧绷感的洁面泡沫。",
        },
    },
    {
        "id": "p002",
        "name": {
            "ja": "セラミドモイスチャー ローション",
            "en": "Ceramide Moisture Lotion",
            "ko": "세라마이드 모이스처 토너",
            "zh": "神经酰胺保湿化妆水",
        },
        "type": "lotion",
        "price_jpy": 1780,
        "fragrance": "none",
        "skin_types": ["dry", "sensitive", "combo"],
        "concerns": ["dryness", "redness", "sensitivity"],
        "tags": ["セラミド", "保湿", "無香料"],
        "emoji": "💧",
        "steps": ["tone"],
        "texture": "watery",
        "description": {
            "ja": "保湿重視のシンプル処方。乾燥・赤みが気になる日に。",
            "en": "Hydration-focused simple formula for dryness and redness-prone days.",
            "ko": "보습 중심의 심플 포뮬러로 건조/붉음 고민에 적합.",
            "zh": "以保湿为主的简洁配方，适合干燥或泛红状态。",
        },
    },
    {
        "id": "p003",
        "name": {
            "ja": "ナイアシンブライト セラム",
            "en": "Niacin Bright Serum",
            "ko": "나이아신 브라이트 세럼",
            "zh": "烟酰胺提亮精华",
        },
        "type": "serum",
        "price_jpy": 2480,
        "fragrance": "light",
        "skin_types": ["combo", "oily", "normal"],
        "concerns": ["dullness", "pores", "oiliness"],
        "tags": ["ナイアシンアミド", "くすみ", "毛穴"],
        "emoji": "✨",
        "steps": ["serum"],
        "texture": "serum",
        "description": {
            "ja": "なめらかさと透明感ケアを両立した軽めの美容液。",
            "en": "Light serum for smoother texture and tone care.",
            "ko": "결 정돈과 톤 케어를 함께 노리는 가벼운 세럼.",
            "zh": "轻盈质地，兼顾肤感平滑与提亮护理。",
        },
    },
    {
        "id": "p004",
        "name": {
            "ja": "カームリペア ジェルクリーム",
            "en": "Calm Repair Gel Cream",
            "ko": "카밍 리페어 젤 크림",
            "zh": "舒缓修护凝霜",
        },
        "type": "moisturizer",
        "price_jpy": 2280,
        "fragrance": "none",
        "skin_types": ["sensitive", "combo", "dry"],
        "concerns": ["redness", "sensitivity", "dryness"],
        "tags": ["整肌", "ジェル", "バリア感"],
        "emoji": "🩷",
        "steps": ["moisturize"],
        "texture": "gel-cream",
        "description": {
            "ja": "ベタつきにくく、赤みや刺激感が出やすい時の保湿に。",
            "en": "Non-greasy moisturizer for redness-prone or sensitive days.",
            "ko": "번들거림 적고 민감/붉음이 있을 때 쓰기 좋은 보습 젤크림.",
            "zh": "清爽不黏腻，适合泛红或敏感时段的保湿修护。",
        },
    },
    {
        "id": "p005",
        "name": {
            "ja": "エアリーフィット UVミルク SPF50+",
            "en": "Airy Fit UV Milk SPF50+",
            "ko": "에어리 핏 UV 밀크 SPF50+",
            "zh": "轻盈贴肤防晒乳 SPF50+",
        },
        "type": "sunscreen",
        "price_jpy": 1980,
        "fragrance": "none",
        "skin_types": ["normal", "combo", "oily", "sensitive"],
        "concerns": ["dullness", "pores", "sensitivity"],
        "tags": ["UV", "日常使い", "無香料"],
        "emoji": "☀️",
        "steps": ["sunscreen"],
        "texture": "milk",
        "description": {
            "ja": "軽い塗り心地で朝の時短に向いた日焼け止め。",
            "en": "Lightweight daily sunscreen ideal for quick AM routines.",
            "ko": "가볍게 발리는 데일리 선케어로 아침 시간 단축에 좋아요.",
            "zh": "轻薄防晒乳，适合早晨快节奏护理流程。",
        },
    },
    {
        "id": "p006",
        "name": {
            "ja": "ポアスムース バランストナー",
            "en": "Pore Smooth Balance Toner",
            "ko": "포어 스무스 밸런스 토너",
            "zh": "毛孔平衡爽肤水",
        },
        "type": "lotion",
        "price_jpy": 1580,
        "fragrance": "light",
        "skin_types": ["oily", "combo"],
        "concerns": ["oiliness", "pores"],
        "tags": ["さっぱり", "毛穴", "皮脂バランス"],
        "emoji": "🧴",
        "steps": ["tone"],
        "texture": "watery",
        "description": {
            "ja": "ベタつきや毛穴目立ちが気になる方向けのさっぱり系。",
            "en": "Fresh-feel toner for oiliness and visible pores.",
            "ko": "번들거림/모공 고민에 맞춘 산뜻한 토너.",
            "zh": "偏清爽型，适合出油和毛孔困扰。",
        },
    },
    {
        "id": "p007",
        "name": {
            "ja": "スポットクリア ジェル",
            "en": "Spot Clear Gel",
            "ko": "스팟 클리어 젤",
            "zh": "局部净肤凝胶",
        },
        "type": "spot",
        "price_jpy": 1280,
        "fragrance": "none",
        "skin_types": ["oily", "combo", "normal"],
        "concerns": ["acne", "oiliness"],
        "tags": ["部分用", "ジェル", "夜向け"],
        "emoji": "🎯",
        "steps": ["spot"],
        "texture": "gel",
        "description": {
            "ja": "気になる部分にピンポイントで使いやすいジェル。",
            "en": "Targeted gel for spot-use on concern areas.",
            "ko": "고민 부위에 국소적으로 사용하기 쉬운 젤.",
            "zh": "用于局部护理的凝胶型产品。",
        },
    },
    {
        "id": "p008",
        "name": {
            "ja": "リッチバリア ナイトクリーム",
            "en": "Rich Barrier Night Cream",
            "ko": "리치 배리어 나이트 크림",
            "zh": "丰润屏障晚霜",
        },
        "type": "moisturizer",
        "price_jpy": 2980,
        "fragrance": "none",
        "skin_types": ["dry", "sensitive", "normal"],
        "concerns": ["dryness", "redness", "dullness"],
        "tags": ["夜用", "バリア", "しっとり"],
        "emoji": "🌙",
        "steps": ["moisturize"],
        "texture": "cream",
        "description": {
            "ja": "夜の保湿重視ケアに。乾燥しやすい季節にも。",
            "en": "Rich nighttime moisturizer for dry seasons and barrier support.",
            "ko": "밤 보습 강화용 크림으로 건조한 계절에 적합.",
            "zh": "适合夜间加强保湿与屏障感护理。",
        },
    },
]


# =========================
# Helpers / Data IO
# =========================
def ensure_data_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DIARY_FILE.exists():
        DIARY_FILE.write_text("[]", encoding="utf-8")
    if not PRODUCTS_FILE.exists():
        PRODUCTS_FILE.write_text(
            json.dumps(DEFAULT_PRODUCTS, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        raw = path.read_text(encoding="utf-8")
        if not raw.strip():
            return default
        return json.loads(raw)
    except Exception:
        return default


def write_json(path: Path, data: Any) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False


def load_diaries() -> List[Dict[str, Any]]:
    data = read_json(DIARY_FILE, [])
    if isinstance(data, list):
        # newest first (date descending, fallback by created_at)
        def sort_key(x: Dict[str, Any]) -> str:
            return str(x.get("date", "")) + str(x.get("created_at", ""))
        return sorted(data, key=sort_key, reverse=True)
    return []


def save_diary_entry(entry: Dict[str, Any]) -> bool:
    diaries = load_diaries()
    diaries.append(entry)
    # resort after append
    diaries = sorted(diaries, key=lambda x: (str(x.get("date", "")), str(x.get("created_at", ""))), reverse=True)
    return write_json(DIARY_FILE, diaries)


def load_products() -> List[Dict[str, Any]]:
    data = read_json(PRODUCTS_FILE, DEFAULT_PRODUCTS)
    if isinstance(data, list):
        return data
    return DEFAULT_PRODUCTS


def get_product_name(prod: Dict[str, Any], lang: str) -> str:
    nm = prod.get("name", {})
    if isinstance(nm, dict):
        return str(nm.get(lang) or nm.get("ja") or next(iter(nm.values()), "Product"))
    return str(nm)


def get_product_desc(prod: Dict[str, Any], lang: str) -> str:
    ds = prod.get("description", {})
    if isinstance(ds, dict):
        return str(ds.get(lang) or ds.get("ja") or "")
    return str(ds)


# =========================
# Ingredient Analysis (Rule-based)
# =========================
FRAGRANCE_KEYWORDS = {
    "fragrance", "parfum", "perfume", "aroma",
}
ALLERGEN_KEYWORDS = {
    "limonene", "linalool", "citral", "geraniol", "citronellol",
    "eugenol", "farnesol", "benzyl alcohol", "benzyl salicylate",
    "hexyl cinnamal", "coumarin", "alpha-isomethyl ionone"
}
DRYING_ALCOHOLS = {
    "alcohol", "alcohol denat", "ethanol", "sd alcohol", "isopropyl alcohol"
}
HUMECTANTS = {
    "glycerin", "butylene glycol", "propylene glycol", "bg", "dipropylene glycol",
    "hyaluronic acid", "sodium hyaluronate", "panthenol", "betaine", "urea", "trehalose"
}
SOOTHING = {
    "allantoin", "centella asiatica", "cica", "madecassoside",
    "dipotassium glycyrrhizate", "glycyrrhizate", "bisabolol", "azulene", "aloe", "camellia sinensis"
}
BRIGHTENING = {
    "niacinamide", "ascorbic acid", "ascorbyl glucoside", "3-o-ethyl ascorbic acid",
    "tranexamic acid", "arbutin", "kojic acid", "glutathione"
}
EXFOLIANTS = {
    "salicylic acid", "bha", "lactic acid", "glycolic acid", "aha",
    "gluconolactone", "pha", "mandelic acid"
}
ACTIVES = {
    "retinol", "retinal", "retinyl palmitate", "adapalene",
    "niacinamide", "vitamin c", "ascorbic acid", "salicylic acid", "glycolic acid", "azelaic acid",
    "tranexamic acid"
}


def normalize_token(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def parse_ingredients(text: str) -> List[str]:
    if not text:
        return []
    # split by comma, newline, semicolon, slash
    parts = re.split(r"[,;\n/]+", text)
    out = []
    for p in parts:
        p2 = normalize_token(p)
        if p2:
            out.append(p2)
    return out


def contains_keyword(token: str, keywords: set) -> bool:
    for kw in keywords:
        if kw in token:
            return True
    return False


def analyze_ingredients(ingredient_text: str, lang: str) -> Dict[str, Any]:
    tokens = parse_ingredients(ingredient_text)

    categories: Dict[str, List[str]] = {
        "fragrance": [],
        "allergen": [],
        "drying_alcohol": [],
        "humectant": [],
        "soothing": [],
        "brightening": [],
        "exfoliant": [],
        "active": [],
    }

    for tok in tokens:
        if contains_keyword(tok, FRAGRANCE_KEYWORDS):
            categories["fragrance"].append(tok)
        if contains_keyword(tok, ALLERGEN_KEYWORDS):
            categories["allergen"].append(tok)
        if contains_keyword(tok, DRYING_ALCOHOLS):
            categories["drying_alcohol"].append(tok)
        if contains_keyword(tok, HUMECTANTS):
            categories["humectant"].append(tok)
        if contains_keyword(tok, SOOTHING):
            categories["soothing"].append(tok)
        if contains_keyword(tok, BRIGHTENING):
            categories["brightening"].append(tok)
        if contains_keyword(tok, EXFOLIANTS):
            categories["exfoliant"].append(tok)
        if contains_keyword(tok, ACTIVES):
            categories["active"].append(tok)

    warnings = []
    if categories["fragrance"] or categories["allergen"]:
        warnings.append(t("warn_patchtest", lang))
    if categories["drying_alcohol"]:
        warnings.append(t("warn_alcohol", lang))
    if len(set(categories["active"])) >= 2:
        warnings.append(t("warn_active", lang))

    notes = [t("note_rulebased", lang)]

    # de-dup and sort display
    for key in categories:
        categories[key] = sorted(list(dict.fromkeys(categories[key])))

    return {
        "tokens": tokens,
        "categories": categories,
        "warnings": warnings,
        "notes": notes,
    }


# =========================
# Trend / Routine / Templates
# =========================
def parse_symptoms_text(symptoms_text: str) -> List[str]:
    if not symptoms_text:
        return []
    parts = re.split(r"[,\n/、，]+", symptoms_text)
    return [p.strip() for p in parts if p.strip()]


def summarize_trends(diaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not diaries:
        return {
            "count": 0,
            "avg_sleep": None,
            "avg_stress": None,
            "symptom_counts": {},
            "recent": [],
        }

    sleeps = []
    stresses = []
    symptom_counts: Dict[str, int] = {}
    chart_rows = []

    for d in diaries:
        sleep = d.get("sleep_hours")
        stress = d.get("stress")
        try:
            if sleep is not None and str(sleep) != "":
                sleeps.append(float(sleep))
        except Exception:
            pass
        try:
            if stress is not None and str(stress) != "":
                stresses.append(float(stress))
        except Exception:
            pass

        syms = parse_symptoms_text(str(d.get("symptoms", "")))
        for s in syms:
            symptom_counts[s] = symptom_counts.get(s, 0) + 1

        chart_rows.append(
            {
                "date": str(d.get("date", "")),
                "sleep": float(sleep) if isinstance(sleep, (int, float)) else None,
                "stress": float(stress) if isinstance(stress, (int, float)) else None,
            }
        )

    avg_sleep = round(sum(sleeps) / len(sleeps), 2) if sleeps else None
    avg_stress = round(sum(stresses) / len(stresses), 2) if stresses else None

    chart_rows = [r for r in chart_rows if r["date"]]
    chart_rows = sorted(chart_rows, key=lambda x: x["date"])

    top_symptoms = sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "count": len(diaries),
        "avg_sleep": avg_sleep,
        "avg_stress": avg_stress,
        "symptom_counts": symptom_counts,
        "top_symptoms": top_symptoms,
        "chart_rows": chart_rows,
        "recent": diaries[:5],
    }


def generate_routine(profile: Dict[str, Any], lang: str) -> Dict[str, List[Dict[str, Any]]]:
    skin_type = profile.get("skin_type", "unknown")
    concerns = set(profile.get("concerns", []))
    fragrance_pref = profile.get("fragrance_pref", "any")
    am_min = int(profile.get("am_minutes", 3))
    pm_min = int(profile.get("pm_minutes", 10))

    def step(name_key: str, desc_map: Dict[str, str], minute: int, optional: bool = False) -> Dict[str, Any]:
        return {
            "title": name_key,
            "desc": desc_map.get(lang) or desc_map.get("ja") or "",
            "minutes": minute,
            "optional": optional,
        }

    # Base AM
    am_steps = [
        step("cleanse", {
            "ja": "ぬるま湯洗顔 or やさしい洗顔で皮脂を整える",
            "en": "Rinse or use a gentle cleanser to reset oil/sweat",
            "ko": "미온수 세안 또는 순한 클렌저로 유분 정리",
            "zh": "温水清洁或温和洁面，整理皮脂与汗水",
        }, 1),
        step("tone", {
            "ja": "化粧水で水分補給（手でやさしく）",
            "en": "Hydrating toner application (gently with hands)",
            "ko": "토너로 수분 보충 (손으로 가볍게)",
            "zh": "使用化妆水补水（轻柔按压）",
        }, 1),
        step("serum", {
            "ja": "悩みに合わせて美容液を1種だけ",
            "en": "Use one serum matching your main concern",
            "ko": "주요 고민에 맞는 세럼 1가지만 사용",
            "zh": "按主要困扰选择一种精华即可",
        }, 1, optional=True),
        step("moisturize", {
            "ja": "乳液/クリームで保湿バランス調整",
            "en": "Seal hydration with lotion/cream",
            "ko": "로션/크림으로 수분막 마무리",
            "zh": "用乳液/面霜锁水收尾",
        }, 1),
        step("sunscreen", {
            "ja": "日焼け止めを十分量",
            "en": "Apply sufficient sunscreen",
            "ko": "충분량의 선크림 사용",
            "zh": "足量使用防晒",
        }, 1),
    ]

    # Base PM
    pm_steps = [
        step("cleanse", {
            "ja": "メイク/日焼け止めを落とし、やさしく洗顔",
            "en": "Remove makeup/sunscreen, then cleanse gently",
            "ko": "메이크업/선케어 제거 후 순하게 세안",
            "zh": "先卸除防晒/彩妆，再温和洁面",
        }, 2),
        step("tone", {
            "ja": "化粧水で水分補給",
            "en": "Hydrating toner",
            "ko": "토너로 수분 보충",
            "zh": "化妆水补水",
        }, 1),
        step("serum", {
            "ja": "美容液（攻め成分は1つまで）",
            "en": "Serum (limit strong actives to one at a time)",
            "ko": "세럼 (강한 활성 성분은 한 번에 1개)",
            "zh": "精华（功效型成分一次尽量只用一种）",
        }, 2),
        step("moisturize", {
            "ja": "乳液/クリームで保湿",
            "en": "Moisturizer/cream",
            "ko": "로션/크림 보습",
            "zh": "乳液/面霜保湿",
        }, 2),
        step("spot", {
            "ja": "必要なら部分用ケアを気になる箇所へ",
            "en": "Optional spot care for local concerns",
            "ko": "필요 시 고민 부위에 국소 케어",
            "zh": "如有需要可进行局部护理",
        }, 1, optional=True),
    ]

    # Concern-based tuning
    if "redness" in concerns or "sensitivity" in concerns or skin_type == "sensitive":
        for s in am_steps + pm_steps:
            if s["title"] == "serum":
                s["desc"] = {
                    "ja": "刺激が少ない整肌系を優先（新規導入は少量から）",
                    "en": "Prefer gentle soothing serums (introduce new products slowly)",
                    "ko": "자극 적은 진정 세럼 우선 (새 제품은 소량부터)",
                    "zh": "优先选择温和舒缓型精华（新品从少量开始）",
                }.get(lang, s["desc"])
        if fragrance_pref != "like":
            for s in am_steps + pm_steps:
                if s["title"] in ("tone", "moisturize"):
                    s["desc"] += {
                        "ja": "（無香料寄り推奨）",
                        "en": " (fragrance-free preferred)",
                        "ko": " (무향 추천)",
                        "zh": "（建议偏无香）",
                    }.get(lang, "")

    if "dryness" in concerns or skin_type == "dry":
        for s in am_steps + pm_steps:
            if s["title"] == "tone":
                s["desc"] = {
                    "ja": "化粧水は重ね付け1〜2回で水分補給",
                    "en": "Layer toner 1–2 times for extra hydration",
                    "ko": "토너를 1~2회 레이어링해 수분 보충",
                    "zh": "化妆水可叠涂1～2次加强补水",
                }.get(lang, s["desc"])
            if s["title"] == "moisturize":
                s["desc"] = {
                    "ja": "乳液/クリームをややしっかりめに",
                    "en": "Use a slightly richer moisturizer/cream",
                    "ko": "보습제를 조금 더 리치하게 사용",
                    "zh": "保湿步骤可用稍微更滋润的乳霜",
                }.get(lang, s["desc"])

    if "oiliness" in concerns or skin_type == "oily":
        for s in am_steps + pm_steps:
            if s["title"] == "moisturize":
                s["desc"] = {
                    "ja": "ジェル/軽い乳液でベタつきを抑えて保湿",
                    "en": "Use a gel/light lotion to hydrate without heaviness",
                    "ko": "젤/라이트 로션으로 번들거림 줄이며 보습",
                    "zh": "使用凝胶或轻乳液，减少厚重感同时保湿",
                }.get(lang, s["desc"])

    if "acne" in concerns:
        for s in pm_steps:
            if s["title"] == "spot":
                s["optional"] = False
                s["desc"] = {
                    "ja": "部分用ケアを気になる箇所に薄く",
                    "en": "Apply spot care thinly on concern areas",
                    "ko": "고민 부위에 스팟 케어를 얇게 도포",
                    "zh": "在问题区域薄涂局部护理产品",
                }.get(lang, s["desc"])

    # Fit to time budget
    def fit_steps(steps: List[Dict[str, Any]], max_minutes: int) -> List[Dict[str, Any]]:
        total = 0
        fitted: List[Dict[str, Any]] = []
        # Always keep sunscreen in AM and cleanse/moisturize in PM if possible
        for s in steps:
            m = int(s.get("minutes", 1))
            optional = bool(s.get("optional", False))
            must_keep = s["title"] in {"cleanse", "moisturize", "sunscreen"}  # sunscreen ignored if PM list has none
            if total + m <= max_minutes:
                fitted.append(s)
                total += m
            else:
                if not optional and must_keep:
                    # squeeze in as 1 min summary step if no room
                    short_s = dict(s)
                    short_s["minutes"] = 1
                    suffix = {
                        "ja": "（時短版）",
                        "en": " (quick)",
                        "ko": " (간단)",
                        "zh": "（精简）",
                    }.get(lang, "")
                    short_s["desc"] = str(short_s["desc"]) + suffix
                    if total + 1 <= max_minutes:
                        fitted.append(short_s)
                        total += 1
        return fitted

    return {
        "am": fit_steps(am_steps, max(2, am_min)),
        "pm": fit_steps(pm_steps, max(3, pm_min)),
    }


def get_symptom_templates(lang: str) -> Dict[str, Dict[str, List[str]]]:
    return {
        "dryness": {
            "label": {
                "ja": "乾燥", "en": "Dryness", "ko": "건조", "zh": "干燥"
            }.get(lang, "Dryness"),
            "am": {
                "ja": ["洗いすぎを避ける", "保湿化粧水を重ねすぎず丁寧に", "日中は乾燥を感じたら保湿ミストより乳液少量を検討"],
                "en": ["Avoid over-cleansing", "Use a hydrating toner gently", "For daytime dryness, a small amount of lotion may help more than mist"],
                "ko": ["과세안 피하기", "보습 토너를 부드럽게 사용", "낮 건조감에는 미스트보다 소량 로션이 도움이 될 수 있음"],
                "zh": ["避免过度清洁", "温和使用保湿化妆水", "白天干燥时可考虑少量乳液而不只是喷雾"],
            }.get(lang, []),
            "pm": {
                "ja": ["洗顔後は早めに保湿", "美容液は1種に絞る", "最後にクリームで水分蒸発を防ぐ"],
                "en": ["Moisturize soon after cleansing", "Limit serums to one", "Finish with cream to reduce moisture loss"],
                "ko": ["세안 후 빠르게 보습", "세럼은 1종 위주", "마지막에 크림으로 수분 증발 방지"],
                "zh": ["洁面后尽快保湿", "精华尽量只选一种", "最后用面霜减少水分流失"],
            }.get(lang, []),
            "avoid": {
                "ja": ["熱いお湯", "強い角質ケアの連用", "香りの強い新製品を一気に増やす"],
                "en": ["Hot water", "Frequent strong exfoliation", "Adding multiple strongly fragranced new products at once"],
                "ko": ["뜨거운 물", "강한 각질 케어의 연속 사용", "향 강한 신제품을 한꺼번에 추가"],
                "zh": ["过热的水", "频繁使用强去角质", "一次性加入多种浓香新品"],
            }.get(lang, []),
            "hospital": {
                "ja": ["強いヒリつき・腫れ・痛み・ジュクジュクが続く場合は皮膚科へ"],
                "en": ["See a dermatologist if severe stinging, swelling, pain, or oozing continues"],
                "ko": ["심한 따가움·붓기·통증·진물이 지속되면 피부과 진료 권장"],
                "zh": ["若明显刺痛、肿胀、疼痛或渗出持续，请及时就医"],
            }.get(lang, []),
        },
        "redness": {
            "label": {
                "ja": "赤み", "en": "Redness", "ko": "홍조", "zh": "泛红"
            }.get(lang, "Redness"),
            "am": {
                "ja": ["摩擦を減らす（こすらない）", "無香料寄りを優先", "紫外線対策を丁寧に"],
                "en": ["Reduce friction", "Prioritize fragrance-free options", "Be consistent with UV protection"],
                "ko": ["마찰 줄이기", "무향 제품 우선", "자외선 차단 꼼꼼히"],
                "zh": ["减少摩擦", "优先无香产品", "认真做好防晒"],
            }.get(lang, []),
            "pm": {
                "ja": ["新しい攻め成分の同時併用を避ける", "シンプルな保湿中心にする", "赤みが強い日は手順を減らす"],
                "en": ["Avoid combining new strong actives", "Keep routine simple and moisturizing", "On red days, reduce total steps"],
                "ko": ["새로운 강한 활성 성분 동시 사용 피하기", "단순 보습 위주 루틴", "홍조 심한 날은 단계 줄이기"],
                "zh": ["避免叠加新功效型成分", "以简洁保湿为主", "泛红明显时减少步骤数量"],
            }.get(lang, []),
            "avoid": {
                "ja": ["スクラブ", "強いピーリング", "熱刺激（熱い風呂・サウナ直後）"],
                "en": ["Scrubs", "Strong peels", "Heat triggers (hot bath/sauna immediately)"],
                "ko": ["스크럽", "강한 필링", "열 자극 (뜨거운 목욕/사우나 직후)"],
                "zh": ["磨砂", "强效焕肤/酸类过度使用", "高热刺激（热水澡/桑拿后）"],
            }.get(lang, []),
            "hospital": {
                "ja": ["赤みが広がる・痛む・腫れる・長引く場合は皮膚科へ"],
                "en": ["See a dermatologist if redness spreads, hurts, swells, or persists"],
                "ko": ["붉음이 퍼지거나 아프고 붓거나 오래 지속되면 진료 권장"],
                "zh": ["若泛红扩散、疼痛、肿胀或持续不退，请就医"],
            }.get(lang, []),
        },
        "oiliness": {
            "label": {
                "ja": "ベタつき", "en": "Oiliness", "ko": "번들거림", "zh": "出油"
            }.get(lang, "Oiliness"),
            "am": {
                "ja": ["洗いすぎず軽く整える", "さっぱり系保湿を省かない", "日焼け止めは軽い質感を選ぶ"],
                "en": ["Cleanse lightly, not aggressively", "Do not skip light hydration", "Choose lightweight sunscreen textures"],
                "ko": ["과하게 씻지 말고 가볍게 정리", "가벼운 보습은 생략하지 않기", "가벼운 제형 선케어 선택"],
                "zh": ["轻度清洁不要过度", "不要省略清爽保湿", "选择轻薄型防晒"],
            }.get(lang, []),
            "pm": {
                "ja": ["落とすケアを丁寧に", "毛穴/皮脂向け成分は頻度調整", "乾燥させすぎない保湿を入れる"],
                "en": ["Cleanse thoroughly but gently", "Adjust frequency of pore/oil-care actives", "Add non-heavy hydration to avoid over-drying"],
                "ko": ["세정은 꼼꼼하지만 순하게", "모공/피지 성분은 빈도 조절", "과건조 방지를 위한 가벼운 보습"],
                "zh": ["清洁到位但保持温和", "控油/毛孔成分注意频率", "加入不过度厚重的保湿避免越控越油"],
            }.get(lang, []),
            "avoid": {
                "ja": ["強い脱脂を毎日", "保湿を完全に抜く", "気になるから何度も洗顔"],
                "en": ["Daily harsh stripping", "Skipping moisturizer entirely", "Washing repeatedly because of shine"],
                "ko": ["매일 강한 탈지 세안", "보습 완전 생략", "번들거림 때문에 잦은 세안"],
                "zh": ["每天强力去脂", "完全不保湿", "因为油光频繁洗脸"],
            }.get(lang, []),
            "hospital": {
                "ja": ["炎症ニキビが増える・痛み/化膿がある場合は皮膚科へ"],
                "en": ["See a dermatologist if inflammatory acne increases or becomes painful/pus-filled"],
                "ko": ["염증성 트러블 증가, 통증/고름이 있으면 피부과 진료 권장"],
                "zh": ["若炎症痘增多，出现疼痛或化脓，请及时就医"],
            }.get(lang, []),
        },
    }


# =========================
# Product Recommendation
# =========================
def recommend_products(
    products: List[Dict[str, Any]],
    profile: Dict[str, Any],
    limit: int = 8,
) -> List[Dict[str, Any]]:
    skin_type = profile.get("skin_type", "unknown")
    concerns = set(profile.get("concerns", []))
    fragrance_pref = profile.get("fragrance_pref", "any")
    budget = int(profile.get("monthly_budget", 5000))
    am_min = int(profile.get("am_minutes", 3))
    pm_min = int(profile.get("pm_minutes", 10))
    time_budget_factor = am_min + pm_min

    scored: List[Tuple[float, Dict[str, Any]]] = []

    for p in products:
        score = 0.0
        price = int(p.get("price_jpy", 0))
        p_skin = set(p.get("skin_types", []))
        p_concerns = set(p.get("concerns", []))
        frag = str(p.get("fragrance", "any"))

        # skin type matching
        if skin_type == "unknown":
            score += 1.0
        elif skin_type in p_skin:
            score += 3.0
        else:
            score -= 0.5

        # concern matching
        overlap = len(concerns & p_concerns)
        score += overlap * 2.5

        # fragrance preference
        if fragrance_pref == "none":
            if frag == "none":
                score += 2.5
            elif frag == "light":
                score -= 0.5
            else:
                score -= 2.0
        elif fragrance_pref == "light":
            if frag in ("none", "light"):
                score += 1.5
        elif fragrance_pref == "like":
            if frag in ("light", "like"):
                score += 1.2

        # price fit
        # rough bundle assumption (3-5 items per month)
        ideal_single = max(800, budget / 4)
        if price <= budget:
            score += 1.0
        score -= abs(price - ideal_single) / 3000.0

        # time budget preference: if short, prioritize simple steps / multi-use textures
        p_type = str(p.get("type", ""))
        if time_budget_factor <= 10:
            if p_type in {"lotion", "moisturizer", "sunscreen"}:
                score += 0.8
            if p_type == "serum":
                score += 0.2
        else:
            if p_type in {"serum", "spot"}:
                score += 0.5

        scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    picked = [p for _, p in scored[:limit]]

    # Keep a sensible mix (EC-like variety)
    type_quota = {"cleanser": 1, "lotion": 2, "serum": 2, "moisturizer": 2, "sunscreen": 1, "spot": 1}
    final: List[Dict[str, Any]] = []
    used_type_count: Dict[str, int] = {}

    for p in picked:
        p_type = str(p.get("type", ""))
        current = used_type_count.get(p_type, 0)
        if current < type_quota.get(p_type, 2):
            final.append(p)
            used_type_count[p_type] = current + 1

    # backfill if too few
    if len(final) < min(limit, len(picked)):
        for p in picked:
            if p not in final:
                final.append(p)
            if len(final) >= min(limit, len(picked)):
                break

    return final


# =========================
# UI Styling
# =========================
def inject_css() -> None:
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;800&family=Inter:wght@400;600;700;800&display=swap');

    :root{
      --bg1:#070812;
      --bg2:#0f1223;
      --card:rgba(255,255,255,0.04);
      --card2:rgba(255,255,255,0.06);
      --line:rgba(255,255,255,0.10);
      --text:#f7f7fb;
      --muted:#b9bfd0;
      --pink1:#ff4d8d;
      --pink2:#ff7ab6;
      --gold1:#d6a84f;
      --gold2:#ffd889;
      --purple1:#8d61ff;
      --glow: 0 0 0 1px rgba(255,255,255,.06), 0 12px 40px rgba(0,0,0,.28);
    }

    html, body, [class*="css"]  {
      font-family: "Inter", "Noto Sans JP", "Apple SD Gothic Neo", "Microsoft YaHei", sans-serif;
    }

    .stApp {
      background:
        radial-gradient(1200px 700px at 85% -5%, rgba(214,168,79,0.18), transparent 55%),
        radial-gradient(900px 650px at 10% 10%, rgba(255,77,141,0.18), transparent 60%),
        linear-gradient(180deg, var(--bg1) 0%, #080b18 40%, var(--bg2) 100%);
      color: var(--text);
    }

    [data-testid="stSidebar"] {
      background:
        radial-gradient(500px 320px at 10% 0%, rgba(255,122,182,0.12), transparent 65%),
        linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border-right: 1px solid rgba(255,255,255,0.06);
    }

    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
      color: var(--text);
    }

    .hero-wrap{
      border-radius: 26px;
      border: 1px solid rgba(255,255,255,0.08);
      background:
        radial-gradient(900px 500px at 100% 0%, rgba(214,168,79,0.12), transparent 70%),
        radial-gradient(800px 500px at 0% 0%, rgba(255,77,141,0.15), transparent 70%),
        linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.03));
      box-shadow: var(--glow);
      padding: 22px 26px 22px 26px;
      margin-bottom: 14px;
      position: relative;
      overflow: hidden;
    }
    .hero-wrap:before{
      content:"";
      position:absolute; inset:0;
      background: linear-gradient(120deg, rgba(255,255,255,0.03), transparent 35%, rgba(255,255,255,0.02));
      pointer-events:none;
    }
    .hero-badge{
      display:inline-flex;
      align-items:center;
      gap:6px;
      font-size:12px;
      color:#f8d6e9;
      border:1px solid rgba(255,122,182,0.35);
      background: rgba(255,77,141,0.12);
      border-radius: 999px;
      padding: 6px 10px;
      margin-bottom: 12px;
      font-weight: 600;
    }
    .hero-grid{
      display:grid;
      grid-template-columns: 78px 1fr;
      gap: 14px;
      align-items: center;
    }
    .logo-shell{
      width: 78px;
      height: 78px;
      border-radius: 22px;
      border: 1px solid rgba(255,255,255,0.10);
      background:
        radial-gradient(circle at 20% 20%, rgba(255,122,182,0.18), transparent 45%),
        radial-gradient(circle at 80% 10%, rgba(214,168,79,0.16), transparent 45%),
        rgba(255,255,255,0.03);
      display:flex; align-items:center; justify-content:center;
      box-shadow: inset 0 0 20px rgba(255,255,255,0.02);
      overflow:hidden;
    }
    .logo-shell span{
      font-size: 38px;
      line-height: 1;
      filter: drop-shadow(0 4px 12px rgba(255,77,141,0.30));
    }
    .hero-title{
      font-size: 28px;
      line-height: 1.15;
      font-weight: 800;
      letter-spacing: -0.02em;
      margin: 0;
      color: var(--text);
    }
    .hero-title .grad{
      background: linear-gradient(90deg, #ffffff, #ffd7e9 45%, #ffe7b0 90%);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
    }
    .hero-sub{
      font-size: 13px;
      color: var(--muted);
      margin-top: 10px;
      margin-bottom: 10px;
      line-height: 1.55;
    }
    .chip-row{
      display:flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 8px;
    }
    .chip{
      border:1px solid rgba(255,255,255,0.10);
      background: rgba(255,255,255,0.03);
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 12px;
      color: #e8ebf7;
    }

    .glass-card{
      border-radius: 22px;
      border:1px solid rgba(255,255,255,0.08);
      background:
        linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
      box-shadow: var(--glow);
      padding: 14px 16px;
      height: 100%;
    }
    .stat-k{
      font-size: 12px;
      color: var(--muted);
      margin-bottom: 10px;
    }
    .stat-v{
      font-size: 28px;
      font-weight: 800;
      line-height: 1.1;
      margin-bottom: 4px;
      color: var(--text);
    }
    .stat-s{
      font-size: 12px;
      color: #cbd2e6;
    }

    .section-card{
      border-radius: 22px;
      border:1px solid rgba(255,255,255,0.08);
      background: rgba(255,255,255,0.02);
      box-shadow: var(--glow);
      padding: 18px;
      margin-top: 10px;
      margin-bottom: 12px;
    }
    .section-title{
      font-size: 18px;
      font-weight: 800;
      margin-bottom: 6px;
      color: #fff;
    }
    .section-desc{
      color: var(--muted);
      font-size: 13px;
      line-height: 1.6;
      margin-bottom: 12px;
    }

    .small-note{
      color:#d7dcef;
      font-size: 12px;
      border-left: 3px solid rgba(255,122,182,0.5);
      padding: 8px 10px;
      background: rgba(255,255,255,0.02);
      border-radius: 0 12px 12px 0;
      margin: 8px 0 12px 0;
    }

    .pill{
      display:inline-block;
      border-radius:999px;
      padding:4px 9px;
      margin: 0 6px 6px 0;
      font-size: 11px;
      font-weight: 600;
      border:1px solid rgba(255,255,255,0.10);
      background: rgba(255,255,255,0.03);
      color:#eef2ff;
    }
    .pill.warn{
      border-color: rgba(255,122,182,0.38);
      background: rgba(255,77,141,0.10);
      color:#ffe3ef;
    }
    .pill.gold{
      border-color: rgba(214,168,79,0.34);
      background: rgba(214,168,79,0.10);
      color:#fff0c6;
    }

    .step-card{
      border:1px solid rgba(255,255,255,0.08);
      border-radius: 16px;
      padding: 12px;
      background: rgba(255,255,255,0.02);
      margin-bottom: 10px;
    }
    .step-head{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:10px;
      margin-bottom:6px;
    }
    .step-title{
      font-size: 14px;
      font-weight: 700;
      color:#fff;
    }
    .step-min{
      color:#ffdca1;
      font-size: 12px;
      font-weight: 700;
      border-radius: 999px;
      border:1px solid rgba(214,168,79,0.25);
      padding: 3px 8px;
      background: rgba(214,168,79,0.08);
      white-space: nowrap;
    }
    .step-desc{
      color:#d2d8eb;
      font-size: 13px;
      line-height: 1.5;
    }

    .ec-card{
      border-radius: 18px;
      border:1px solid rgba(255,255,255,0.08);
      background:
        radial-gradient(500px 160px at 100% 0%, rgba(214,168,79,0.08), transparent 55%),
        radial-gradient(450px 180px at 0% 0%, rgba(255,77,141,0.08), transparent 60%),
        rgba(255,255,255,0.02);
      padding: 14px;
      box-shadow: var(--glow);
      height: 100%;
    }
    .ec-top{
      display:flex;
      align-items:center;
      gap:12px;
      margin-bottom: 10px;
    }
    .ec-emoji{
      width: 54px; height:54px;
      border-radius: 15px;
      display:flex; align-items:center; justify-content:center;
      font-size: 26px;
      border:1px solid rgba(255,255,255,0.09);
      background: rgba(255,255,255,0.03);
      flex-shrink: 0;
    }
    .ec-name{
      color:#fff;
      font-size: 14px;
      line-height: 1.3;
      font-weight: 700;
      margin-bottom: 2px;
    }
    .ec-meta{
      color:#d4d9e9;
      font-size: 12px;
    }
    .ec-desc{
      color:#c7cee2;
      font-size: 12px;
      line-height: 1.5;
      min-height: 48px;
      margin: 8px 0 8px 0;
    }
    .ec-price{
      margin-top: 8px;
      color:#ffe8b8;
      font-weight: 800;
      font-size: 16px;
      letter-spacing: 0.02em;
    }
    .ec-tags{
      margin-top: 8px;
      min-height: 28px;
    }
    .ec-tag{
      display:inline-block;
      font-size: 11px;
      border-radius: 999px;
      padding: 4px 8px;
      margin: 0 6px 6px 0;
      background: rgba(255,255,255,0.03);
      border:1px solid rgba(255,255,255,0.08);
      color:#eaf0ff;
    }
    .ec-footer{
      margin-top: 10px;
      display:flex;
      justify-content: space-between;
      align-items:center;
      gap:8px;
    }
    .ec-badge{
      font-size:11px;
      color:#ffd8e8;
      border:1px solid rgba(255,122,182,0.26);
      padding:4px 8px;
      border-radius:999px;
      background: rgba(255,77,141,0.08);
    }
    .ec-btn{
      font-size:12px;
      color:#fff;
      border:1px solid rgba(214,168,79,0.35);
      padding:5px 10px;
      border-radius:999px;
      background: rgba(214,168,79,0.10);
    }

    .profile-card{
      border-radius: 18px;
      border:1px solid rgba(255,255,255,0.08);
      background:
        radial-gradient(400px 120px at 100% 0%, rgba(214,168,79,0.08), transparent 70%),
        radial-gradient(360px 120px at 0% 0%, rgba(255,77,141,0.10), transparent 70%),
        rgba(255,255,255,0.02);
      padding: 14px;
      margin-bottom: 12px;
    }
    .profile-card h4{
      margin: 0 0 6px 0;
      font-size: 17px;
      color: #fff;
      font-weight: 800;
    }
    .profile-card p{
      margin: 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.55;
    }

    .stButton > button {
      border-radius: 14px !important;
      border: 1px solid rgba(255,255,255,0.10) !important;
      background:
        linear-gradient(180deg, rgba(255,122,182,0.18), rgba(255,77,141,0.14)) !important;
      color: #fff !important;
      font-weight: 700 !important;
      box-shadow: 0 6px 20px rgba(255,77,141,0.20);
    }
    .stButton > button:hover {
      border-color: rgba(214,168,79,0.30) !important;
      box-shadow: 0 8px 24px rgba(214,168,79,0.18);
    }

    .stTextArea textarea, .stTextInput input, .stDateInput input {
      border-radius: 14px !important;
      background: rgba(255,255,255,0.02) !important;
      color: #fff !important;
      border:1px solid rgba(255,255,255,0.08) !important;
    }

    div[data-baseweb="select"] > div {
      border-radius: 14px !important;
      background: rgba(255,255,255,0.02) !important;
      border:1px solid rgba(255,255,255,0.08) !important;
    }

    [data-testid="stMetric"]{
      background: rgba(255,255,255,0.02);
      border-radius: 16px;
      border: 1px solid rgba(255,255,255,0.08);
      padding: 10px;
    }

    .footer-note{
      margin-top: 18px;
      color: #cfd5ea;
      font-size: 12px;
      line-height: 1.6;
      border-top: 1px solid rgba(255,255,255,0.08);
      padding-top: 12px;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# =========================
# UI Render Helpers
# =========================
def render_hero(profile: Dict[str, Any], lang: str, stats: Dict[str, Any], logo_file) -> None:
    # header chips
    concern_labels = []
    for c in profile.get("concerns", []):
        concern_labels.append(concern_label(c, lang))
    if not concern_labels:
        concern_labels = [t("skin_unknown", lang)]

    chips = [
        f"{t('skin_type', lang)}: {skin_type_label(profile.get('skin_type', 'unknown'), lang)}",
        f"{t('concerns', lang)}: {', '.join(concern_labels)}",
        f"{t('fragrance_pref', lang)}: {fragrance_label(profile.get('fragrance_pref', 'any'), lang)}",
        f"{t('monthly_budget', lang)}: ¥{int(profile.get('monthly_budget', 5000)):,}",
        f"{t('am_minutes', lang)} {int(profile.get('am_minutes', 3))}{t('minutes', lang)} / {t('pm_minutes', lang)} {int(profile.get('pm_minutes', 10))}{t('minutes', lang)}",
    ]

    logo_html = "<span>💄</span>"
    if logo_file is not None:
        # embed uploaded image directly in Streamlit component area separately (safer than base64 inline)
        # Here we just switch icon marker; actual image shown under hero using st.image
        logo_html = "<span>🪞</span>"

    title_html = (
        "<span class='grad'>"
        + escape(t("app_title", lang))
        + "</span><br>"
        + escape(t("app_subtitle", lang))
    )

    chips_html = "".join([f"<span class='chip'>{escape(ch)}</span>" for ch in chips])

    hero_html = f"""
    <div class="hero-wrap">
      <div class="hero-badge">{escape(t("badge", lang))}</div>
      <div class="hero-grid">
        <div class="logo-shell">{logo_html}</div>
        <div>
          <div class="hero-title">{title_html}</div>
          <div class="hero-sub">{escape(t("app_desc", lang))}</div>
          <div class="chip-row">{chips_html}</div>
        </div>
      </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

    if logo_file is not None:
        with st.container():
            c1, c2, c3 = st.columns([1.2, 3.6, 0.2])
            with c1:
                st.image(logo_file, use_container_width=True, caption=t("logo_frame", lang))

    # KPI cards row
    c1, c2, c3 = st.columns(3)
    with c1:
        val = f"{stats.get('count', 0)}"
        html = f"""
        <div class="glass-card">
          <div class="stat-k">{escape(t('stat_records', lang))}</div>
          <div class="stat-v">{escape(val)}{escape('件' if lang == 'ja' else '')}</div>
          <div class="stat-s">{escape(t('daily_ok', lang))}</div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
    with c2:
        avg_sleep = stats.get("avg_sleep")
        val = t("not_recorded", lang) if avg_sleep is None else f"{avg_sleep}"
        sub = {
            "ja": "肌のゆらぎと一緒に見やすい",
            "en": "Useful to compare with flare days",
            "ko": "피부 컨디션과 함께 보면 좋아요",
            "zh": "可与皮肤波动一起对照查看",
        }.get(lang, "")
        html = f"""
        <div class="glass-card">
          <div class="stat-k">{escape(t('stat_avg_sleep', lang))}</div>
          <div class="stat-v">{escape(val)}</div>
          <div class="stat-s">{escape(sub)}</div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
    with c3:
        avg_stress = stats.get("avg_stress")
        val = t("not_recorded", lang) if avg_stress is None else f"{avg_stress}/5"
        sub = {
            "ja": "生活要因の振り返り用",
            "en": "Good for lifestyle reflection",
            "ko": "생활요인 돌아보기용",
            "zh": "用于回看生活因素变化",
        }.get(lang, "")
        html = f"""
        <div class="glass-card">
          <div class="stat-k">{escape(t('stat_avg_stress', lang))}</div>
          <div class="stat-v">{escape(val)}</div>
          <div class="stat-s">{escape(sub)}</div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)


def render_section_header(title: str, desc: str) -> None:
    html = f"""
    <div class="section-card">
      <div class="section-title">{escape(title)}</div>
      <div class="section-desc">{escape(desc)}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_small_note(text: str) -> None:
    html = "<div class='small-note'>{}</div>".format(escape(text))
    st.markdown(html, unsafe_allow_html=True)


def concern_label(code: str, lang: str) -> str:
    key_map = {
        "dryness": "concern_dryness",
        "redness": "concern_redness",
        "oiliness": "concern_oiliness",
        "pores": "concern_pores",
        "dullness": "concern_dullness",
        "acne": "concern_acne",
        "sensitivity": "concern_sensitivity",
    }
    return t(key_map.get(code, "symptom_none"), lang)


def skin_type_label(code: str, lang: str) -> str:
    key_map = {
        "normal": "skin_normal",
        "dry": "skin_dry",
        "oily": "skin_oily",
        "combo": "skin_combo",
        "sensitive": "skin_sensitive",
        "unknown": "skin_unknown",
    }
    return t(key_map.get(code, "skin_unknown"), lang)


def fragrance_label(code: str, lang: str) -> str:
    key_map = {
        "any": "fragrance_any",
        "none": "fragrance_none",
        "light": "fragrance_light",
        "like": "fragrance_like",
    }
    return t(key_map.get(code, "fragrance_any"), lang)


def product_type_label(code: str, lang: str) -> str:
    key_map = {
        "cleanser": "product_type_cleanser",
        "lotion": "product_type_lotion",
        "serum": "product_type_serum",
        "moisturizer": "product_type_moisturizer",
        "sunscreen": "product_type_sunscreen",
        "spot": "product_type_spot",
    }
    return t(key_map.get(code, "product_type_serum"), lang)


def category_label(code: str, lang: str) -> str:
    key_map = {
        "fragrance": "category_fragrance",
        "allergen": "category_allergen",
        "drying_alcohol": "category_drying_alcohol",
        "humectant": "category_humectant",
        "soothing": "category_soothing",
        "brightening": "category_brightening",
        "exfoliant": "category_exfoliant",
        "active": "category_active",
    }
    return t(key_map.get(code, code), lang)


def render_step_list(title: str, steps: List[Dict[str, Any]], lang: str) -> None:
    st.markdown(f"### {escape(title)}")
    total_m = 0
    for idx, s in enumerate(steps, start=1):
        total_m += int(s.get("minutes", 0))
        step_title_map = {
            "cleanse": {"ja": "洗う/落とす", "en": "Cleanse", "ko": "세안/클렌징", "zh": "清洁"},
            "tone": {"ja": "化粧水", "en": "Toner", "ko": "토너", "zh": "化妆水"},
            "serum": {"ja": "美容液", "en": "Serum", "ko": "세럼", "zh": "精华"},
            "moisturize": {"ja": "保湿", "en": "Moisturize", "ko": "보습", "zh": "保湿"},
            "sunscreen": {"ja": "日焼け止め", "en": "Sunscreen", "ko": "선케어", "zh": "防晒"},
            "spot": {"ja": "部分ケア", "en": "Spot Care", "ko": "스팟 케어", "zh": "局部护理"},
        }
        localized_title = step_title_map.get(s["title"], {}).get(lang, s["title"])
        head_title = f"{idx}. {localized_title}"
        desc_text = str(s.get("desc", ""))
        minutes_text = f"{int(s.get('minutes', 1))}{t('minutes', lang)}"

        html = f"""
        <div class="step-card">
          <div class="step-head">
            <div class="step-title">{escape(head_title)}</div>
            <div class="step-min">{escape(minutes_text)}</div>
          </div>
          <div class="step-desc">{escape(desc_text)}</div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    total_label = {
        "ja": f"合計目安: {total_m}分",
        "en": f"Estimated total: {total_m} min",
        "ko": f"예상 총 시간: {total_m}분",
        "zh": f"预计总时长：{total_m}分钟",
    }.get(lang, f"{total_m} min")
    render_small_note(total_label)


def render_product_card(prod: Dict[str, Any], lang: str, profile: Dict[str, Any]) -> None:
    name = get_product_name(prod, lang)
    desc = get_product_desc(prod, lang)
    emoji = str(prod.get("emoji", "🧴"))
    p_type = product_type_label(str(prod.get("type", "serum")), lang)
    price = int(prod.get("price_jpy", 0))
    frag = fragrance_label(str(prod.get("fragrance", "any")), lang)

    tags = prod.get("tags", [])
    if not isinstance(tags, list):
        tags = []
    tags_html = "".join([f"<span class='ec-tag'>{escape(str(tag))}</span>" for tag in tags[:4]])

    price_text = f"¥{price:,}"
    footer_note = t("product_card_note", lang)
    cta = t("cta_try", lang)

    html = f"""
    <div class="ec-card">
      <div class="ec-top">
        <div class="ec-emoji">{escape(emoji)}</div>
        <div>
          <div class="ec-name">{escape(name)}</div>
          <div class="ec-meta">{escape(p_type)} ・ {escape(frag)}</div>
        </div>
      </div>
      <div class="ec-desc">{escape(desc)}</div>
      <div class="ec-tags">{tags_html}</div>
      <div class="ec-price">{escape(t('price', lang))}: {escape(price_text)}</div>
      <div class="ec-footer">
        <span class="ec-badge">{escape(footer_note)}</span>
        <span class="ec-btn">{escape(cta)}</span>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# =========================
# Main App
# =========================
def main() -> None:
    st.set_page_config(
        page_title="Beauty Agent Local",
        page_icon="💄",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    ensure_data_files()
    inject_css()

    # Session defaults
    if "lang" not in st.session_state:
        st.session_state["lang"] = "ja"

    if "last_recommendations" not in st.session_state:
        st.session_state["last_recommendations"] = []

    # Sidebar - Language
    with st.sidebar:
        lang_options = {
            t("lang_ja", "ja"): "ja",
            t("lang_en", "ja"): "en",
            t("lang_ko", "ja"): "ko",
            t("lang_zh", "ja"): "zh",
        }
        selected_lang_label = st.selectbox(
            "🌐 Language / 言語",
            options=list(lang_options.keys()),
            index=list(lang_options.values()).index(st.session_state.get("lang", "ja")),
        )
        lang = lang_options[selected_lang_label]
        st.session_state["lang"] = lang

        st.markdown(
            f"""
            <div class="profile-card">
              <h4>⚙️ {escape(t('profile', lang))}</h4>
              <p>{escape(t('profile_desc', lang))}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        logo_file = st.file_uploader(
            t("logo_frame", lang),
            type=["png", "jpg", "jpeg"],
            help=t("logo_help", lang),
        )

        skin_map = {
            skin_type_label("unknown", lang): "unknown",
            skin_type_label("normal", lang): "normal",
            skin_type_label("dry", lang): "dry",
            skin_type_label("oily", lang): "oily",
            skin_type_label("combo", lang): "combo",
            skin_type_label("sensitive", lang): "sensitive",
        }
        skin_sel = st.selectbox(t("skin_type", lang), list(skin_map.keys()), index=0)
        skin_type = skin_map[skin_sel]

        concern_opts = [
            ("dryness", concern_label("dryness", lang)),
            ("redness", concern_label("redness", lang)),
            ("oiliness", concern_label("oiliness", lang)),
            ("pores", concern_label("pores", lang)),
            ("dullness", concern_label("dullness", lang)),
            ("acne", concern_label("acne", lang)),
            ("sensitivity", concern_label("sensitivity", lang)),
        ]
        concern_labels = [label for _, label in concern_opts]
        concern_code_map = {label: code for code, label in concern_opts}
        concern_selected_labels = st.multiselect(
            t("concerns", lang),
            options=concern_labels,
            default=[],
        )
        concern_codes = [concern_code_map[x] for x in concern_selected_labels]

        frag_map = {
            fragrance_label("any", lang): "any",
            fragrance_label("none", lang): "none",
            fragrance_label("light", lang): "light",
            fragrance_label("like", lang): "like",
        }
        frag_sel = st.selectbox(t("fragrance_pref", lang), list(frag_map.keys()), index=0)
        fragrance_pref = frag_map[frag_sel]

        monthly_budget = st.number_input(
            t("monthly_budget", lang),
            min_value=1000,
            max_value=50000,
            value=5000,
            step=500,
        )

        am_minutes = st.slider(t("am_minutes", lang), min_value=1, max_value=15, value=3)
        pm_minutes = st.slider(t("pm_minutes", lang), min_value=3, max_value=30, value=10)

    profile = {
        "skin_type": skin_type,
        "concerns": concern_codes,
        "fragrance_pref": fragrance_pref,
        "monthly_budget": int(monthly_budget),
        "am_minutes": int(am_minutes),
        "pm_minutes": int(pm_minutes),
    }

    # Load data
    diaries = load_diaries()
    products = load_products()
    trend = summarize_trends(diaries)

    # Header / Hero
    render_hero(profile, lang, trend, logo_file)

    # Tabs
    tab_titles = [
        t("tabs_ingredient", lang),
        t("tabs_diary", lang),
        t("tabs_trend", lang),
        t("tabs_routine", lang),
        t("tabs_template", lang),
        t("tabs_products", lang),
    ]
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tab_titles)

    # -------------------------
    # Tab 1: Ingredient Check
    # -------------------------
    with tab1:
        render_section_header(t("ingredient_title", lang), t("ingredient_desc", lang))
        ingredient_text = st.text_area(
            t("ingredient_input_label", lang),
            height=150,
            placeholder=t("ingredient_placeholder", lang),
        )
        if st.button(t("check_button", lang), key="btn_check_ingredients"):
            if not ingredient_text.strip():
                st.warning(t("no_ingredient", lang))
            else:
                result = analyze_ingredients(ingredient_text, lang)

                st.markdown(f"### {escape(t('analysis_result', lang))}")

                # categories summary pills
                detected_blocks = []
                for ckey, vals in result["categories"].items():
                    if vals:
                        label = category_label(ckey, lang)
                        pill_class = "gold" if ckey in ("humectant", "soothing", "brightening") else ""
                        detected_blocks.append(f"<span class='pill {pill_class}'>{escape(label)}</span>")
                if detected_blocks:
                    st.markdown(
                        "<div>" + "".join(detected_blocks) + "</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.info({
                        "ja": "明確なカテゴリ検出はありませんでした（簡易ルール判定）。",
                        "en": "No clear category hit found (quick rule-based scan).",
                        "ko": "명확한 카테고리 검출이 없었습니다 (간이 룰베이스).",
                        "zh": "未检测到明显类别（简易规则判断）。",
                    }.get(lang, ""))

                # detailed detected ingredients
                with st.expander(t("detected_categories", lang), expanded=True):
                    for ckey, vals in result["categories"].items():
                        if vals:
                            st.markdown(f"**{escape(category_label(ckey, lang))}**")
                            pills = []
                            for v in vals:
                                cls = "pill warn" if ckey in ("fragrance", "allergen", "drying_alcohol") else "pill"
                                pills.append(f"<span class='{cls}'>{escape(v)}</span>")
                            st.markdown("".join(pills), unsafe_allow_html=True)

                if result["warnings"]:
                    st.markdown(f"**{escape(t('warnings', lang))}**")
                    for w in result["warnings"]:
                        st.warning(w)

                if result["notes"]:
                    st.markdown(f"**{escape(t('notes', lang))}**")
                    for n in result["notes"]:
                        render_small_note(n)

    # -------------------------
    # Tab 2: Diary (Save/List)
    # -------------------------
    with tab2:
        render_section_header(t("diary_title", lang), t("diary_desc", lang))

        with st.form("diary_form"):
            rec_date = st.date_input(t("record_date", lang), value=date.today())
            symptoms_text = st.text_input(
                t("symptoms", lang),
                placeholder=t("save_hint", lang),
            )

            c1, c2 = st.columns(2)
            with c1:
                sleep_hours = st.slider(
                    t("sleep_hours", lang),
                    min_value=0.0,
                    max_value=12.0,
                    value=6.0,
                    step=0.5,
                )
            with c2:
                stress = st.slider(
                    t("stress_level", lang),
                    min_value=1,
                    max_value=5,
                    value=3,
                    step=1,
                )

            used_items = st.text_input(
                t("used_items", lang),
                placeholder=t("used_items_placeholder", lang),
            )
            memo = st.text_area(
                t("memo", lang),
                height=100,
                placeholder=t("memo_placeholder", lang),
            )

            submitted = st.form_submit_button(t("save_diary", lang))
            if submitted:
                entry = {
                    "date": str(rec_date),
                    "symptoms": symptoms_text.strip(),
                    "sleep_hours": float(sleep_hours),
                    "stress": int(stress),
                    "used_items": used_items.strip(),
                    "memo": memo.strip(),
                    "lang": lang,
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                }
                ok = save_diary_entry(entry)
                if ok:
                    st.success(t("saved_ok", lang))
                    st.rerun()
                else:
                    st.error("Save failed")

        st.markdown(f"### {escape(t('diary_list', lang))}")
        diaries = load_diaries()  # refresh for immediate display
        if not diaries:
            st.info(t("no_diary", lang))
        else:
            for idx, d in enumerate(diaries[:50]):
                with st.expander(
                    f"{d.get('date', '')} / {t('stress_level', lang)} {d.get('stress', '-')}/5 / {t('sleep_hours', lang)} {d.get('sleep_hours', '-')}",
                    expanded=(idx == 0),
                ):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**{t('symptoms', lang)}**: {d.get('symptoms', '') or t('symptom_none', lang)}")
                        st.write(f"**{t('used_items', lang)}**: {d.get('used_items', '') or '-'}")
                    with c2:
                        st.write(f"**{t('memo', lang)}**: {d.get('memo', '') or '-'}")
                        created_at = d.get("created_at", "")
                        if created_at:
                            st.caption(created_at)

    # -------------------------
    # Tab 3: Trend Memo
    # -------------------------
    with tab3:
        render_section_header(t("trend_title", lang), t("trend_desc", lang))
        trend = summarize_trends(load_diaries())

        if trend["count"] == 0:
            st.info(t("no_diary", lang))
        else:
            # Summary bullets
            st.markdown(f"### {escape(t('trend_summary', lang))}")
            c1, c2 = st.columns(2)
            with c1:
                avg_sleep_text = (
                    t("not_recorded", lang)
                    if trend["avg_sleep"] is None
                    else f"{trend['avg_sleep']}"
                )
                st.markdown(f"- {t('stat_avg_sleep', lang)}: **{avg_sleep_text}**")
                avg_stress_text = (
                    t("not_recorded", lang)
                    if trend["avg_stress"] is None
                    else f"{trend['avg_stress']}/5"
                )
                st.markdown(f"- {t('stat_avg_stress', lang)}: **{avg_stress_text}**")
                st.markdown(f"- {t('stat_records', lang)}: **{trend['count']}**")
            with c2:
                if trend.get("top_symptoms"):
                    lines = []
                    for name, cnt in trend["top_symptoms"]:
                        lines.append(f"{name} ({cnt})")
                    st.markdown("- " + "\n- ".join(lines))
                else:
                    st.markdown(f"- {t('symptoms', lang)}: **{t('symptom_none', lang)}**")

            # charts
            rows = trend.get("chart_rows", [])
            if rows:
                # prepare DataFrame only if pandas available in Streamlit runtime
                try:
                    import pandas as pd  # local import to avoid hard dependency in code reading
                    df = pd.DataFrame(rows)
                    if not df.empty:
                        # convert date
                        try:
                            df["date"] = pd.to_datetime(df["date"])
                            df = df.sort_values("date")
                            df = df.set_index("date")
                        except Exception:
                            pass
                        st.markdown("### 📈 Sleep / Stress")
                        st.line_chart(df[["sleep", "stress"]], use_container_width=True)
                except Exception:
                    pass

            # insights note
            tips = []
            if trend["avg_sleep"] is not None and trend["avg_sleep"] < 6:
                tips.append({
                    "ja": "平均睡眠が短めです。肌がゆらぐ日は睡眠時間も一緒にメモすると比較しやすいです。",
                    "en": "Average sleep looks short. Tracking sleep alongside flare days may help.",
                    "ko": "평균 수면이 짧은 편입니다. 피부 흔들림과 함께 기록해보세요.",
                    "zh": "平均睡眠偏短，建议与肌肤波动一起对照记录。",
                }.get(lang, ""))
            if trend["avg_stress"] is not None and trend["avg_stress"] >= 4:
                tips.append({
                    "ja": "ストレス高めの日が多い可能性。ルーティンは“減らす”選択も有効です。",
                    "en": "Stress looks high. Simplifying your routine on those days can help.",
                    "ko": "스트레스가 높은 날이 많은 편입니다. 그럴 땐 루틴을 줄이는 것도 방법입니다.",
                    "zh": "压力较高的日子较多时，可考虑适当减少护理步骤。",
                }.get(lang, ""))
            if not tips:
                tips.append({
                    "ja": "記録を継続すると、睡眠・ストレス・症状のつながりが見えやすくなります。",
                    "en": "Keep logging regularly to better spot patterns among sleep, stress, and symptoms.",
                    "ko": "기록을 꾸준히 하면 수면/스트레스/증상 패턴을 더 잘 볼 수 있어요.",
                    "zh": "持续记录后，更容易看出睡眠、压力和症状之间的关系。",
                }.get(lang, ""))

            for tip in tips:
                render_small_note(tip)

    # -------------------------
    # Tab 4: Routine Generator
    # -------------------------
    with tab4:
        render_section_header(t("routine_title", lang), t("routine_desc", lang))
        render_small_note(t("routine_note", lang))
        if st.button(t("make_routine", lang), key="btn_make_routine"):
            st.session_state["generated_routine"] = generate_routine(profile, lang)

        routine = st.session_state.get("generated_routine")
        if routine:
            c1, c2 = st.columns(2)
            with c1:
                render_step_list(t("am_routine", lang), routine.get("am", []), lang)
            with c2:
                render_step_list(t("pm_routine", lang), routine.get("pm", []), lang)
        else:
            render_small_note({
                "ja": "まだ生成されていません。プロフィールを調整してボタンを押してください。",
                "en": "No routine generated yet. Adjust your profile and press the button.",
                "ko": "아직 루틴이 생성되지 않았습니다. 프로필 설정 후 버튼을 눌러주세요.",
                "zh": "尚未生成护理流程，请先调整个人资料后点击按钮。",
            }.get(lang, ""))

    # -------------------------
    # Tab 5: Symptom Templates
    # -------------------------
    with tab5:
        render_section_header(t("template_title", lang), t("template_desc", lang))
        templates = get_symptom_templates(lang)
        symptom_order = ["dryness", "redness", "oiliness"]
        symptom_labels = [templates[k]["label"] for k in symptom_order]
        selected_label = st.selectbox(t("choose_symptom", lang), symptom_labels, index=0)
        selected_key = symptom_order[symptom_labels.index(selected_label)]
        selected = templates[selected_key]

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"### {escape(t('template_am', lang))}")
            for item in selected.get("am", []):
                st.markdown(f"- {escape(item)}")
            st.markdown(f"### {escape(t('template_avoid', lang))}")
            for item in selected.get("avoid", []):
                st.markdown(f"- {escape(item)}")
        with c2:
            st.markdown(f"### {escape(t('template_pm', lang))}")
            for item in selected.get("pm", []):
                st.markdown(f"- {escape(item)}")
            st.markdown(f"### {escape(t('template_when_to_hospital', lang))}")
            for item in selected.get("hospital", []):
                st.warning(item)

    # -------------------------
    # Tab 6: Products (EC-like)
    # -------------------------
    with tab6:
        render_section_header(t("products_title", lang), t("products_desc", lang))

        if st.button(t("recommend_button", lang), key="btn_recommend_products"):
            st.session_state["last_recommendations"] = recommend_products(products, profile, limit=8)

        picks = st.session_state.get("last_recommendations", [])
        if not picks:
            render_small_note({
                "ja": "まだ表示していません。「おすすめを表示」を押して、プロフィール条件に合わせた候補を出します。",
                "en": "No recommendations shown yet. Press the button to filter suggestions from your profile.",
                "ko": "아직 추천이 표시되지 않았습니다. 버튼을 눌러 프로필 조건에 맞는 후보를 보세요.",
                "zh": "尚未显示推荐，请点击按钮按个人资料条件筛选候选。",
            }.get(lang, ""))
        else:
            # budget summary
            total_est = sum(int(p.get("price_jpy", 0)) for p in picks[:4])
            budget_msg = {
                "ja": f"おすすめ上位4点の合計目安: ¥{total_est:,}（月予算 ¥{int(profile['monthly_budget']):,}）",
                "en": f"Approx. total for top 4 picks: ¥{total_est:,} (Monthly budget ¥{int(profile['monthly_budget']):,})",
                "ko": f"상위 4개 추천 예상 합계: ¥{total_est:,} (월 예산 ¥{int(profile['monthly_budget']):,})",
                "zh": f"前4项推荐预计合计：¥{total_est:,}（月预算 ¥{int(profile['monthly_budget']):,}）",
            }.get(lang, "")
            render_small_note(budget_msg)

            cols = st.columns(2)
            for i, p in enumerate(picks):
                with cols[i % 2]:
                    render_product_card(p, lang, profile)

    # Footer
    st.markdown(
        f"<div class='footer-note'>{escape(t('footer_note', lang))}</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()