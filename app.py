# app.py
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

import streamlit as st


# =========================
# 基本設定
# =========================
st.set_page_config(
    page_title="Beauty Agent Local",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "beauty_agent_data"
DIARY_FILE = DATA_DIR / "skin_diary.json"
PRODUCTS_FILE = DATA_DIR / "products_local.json"


# =========================
# 多言語（i18n）
# =========================
LANG_OPTIONS = {
    "日本語": "ja",
    "English": "en",
    "한국어": "ko",
    "中文（简体）": "zh",
}

I18N: Dict[str, Dict[str, str]] = {
    "ja": {
        "lang_picker": "言語 / Language",
        "badge": "ローカル保存対応",
        "title": "💄 Beauty Agent Local",
        "subtitle": "女性向けセルフケア Web版",
        "desc": "API不要 / ローカル保存 / 成分チェック・肌日記・傾向メモ・朝夜ルーティン・症状別テンプレ・ローカル商品提案",

        "sidebar_profile": "⚙️ プロフィール",
        "sidebar_profile_desc": "あなた向けに、やさしく提案を最適化します",
        "skin_type": "肌タイプ",
        "concerns": "悩み",
        "fragrance_pref": "香りの好み",
        "budget": "月予算（円）",
        "am_minutes": "朝ケア時間（分）",
        "pm_minutes": "夜ケア時間（分）",

        "unset": "未設定",
        "fragrance_free": "無香料",
        "fragrance_ok": "香りありOK",
        "either": "どちらでも",

        "normal": "普通肌",
        "dry": "乾燥肌",
        "oily": "脂性肌",
        "combo": "混合肌",
        "sensitive": "敏感肌",

        "concern_dryness": "乾燥",
        "concern_pores": "毛穴",
        "concern_redness": "赤み",
        "concern_acne": "ニキビ",
        "concern_dullness": "くすみ",
        "concern_oiliness": "ベタつき",

        "symptom_dry": "乾燥",
        "symptom_redness": "赤み",
        "symptom_oily": "ベタつき",

        "tab_ing": "成分チェック",
        "tab_diary": "肌日記（保存/一覧）",
        "tab_trend": "傾向メモ",
        "tab_routine": "朝/夜ルーティン",
        "tab_template": "症状別テンプレ",
        "tab_products": "ローカル商品提案",

        "stat_records": "記録件数",
        "stat_avg_sleep": "平均睡眠",
        "stat_avg_stress": "平均ストレス",
        "stat_no_data": "未記録",
        "stat_records_sub": "毎日1行でもOK",
        "stat_sleep_sub": "肌のゆらぎと一緒に見やすい",
        "stat_stress_sub": "生活要因の振り返り用",

        "chip_skin": "肌タイプ",
        "chip_concerns": "悩み",
        "chip_fragrance": "香り",
        "chip_budget": "予算",
        "chip_time": "朝{am}分 / 夜{pm}分",

        "ing_title": "成分チェック（ルールベース簡易）",
        "ing_desc": "成分を貼るだけで、香料・香料アレルゲン・乾燥しやすいアルコールなどをざっくり確認できます。",
        "ing_input_label": "成分を貼り付け（カンマ区切り / 改行OK）",
        "ing_placeholder": "Water, Glycerin, Niacinamide, Fragrance, Limonene",
        "check": "チェックする",
        "please_input_ing": "成分を入力してください。",
        "detected_categories": "検出カテゴリ",
        "cautions": "注意点",
        "memo": "メモ",
        "matches": "検出語",
        "no_hit": "大きな注意カテゴリは見つかりませんでした（簡易判定）。",
        "cat_fragrance": "香料",
        "cat_allergen": "香料アレルゲン（精油由来含む）",
        "cat_drying_alcohol": "乾燥しやすいアルコール",
        "cat_niacinamide": "ナイアシンアミド",
        "cat_humectant": "保湿成分",
        "cat_barrier": "バリアサポート成分",
        "cat_exfoliant": "角質ケア成分",
        "cat_vitc": "ビタミンC系",
        "caution_fragrance": "香料/香料アレルゲンの可能性。敏感な方はパッチテスト推奨。",
        "caution_alcohol": "乾燥・刺激を感じやすい方は様子見推奨。",
        "caution_exfoliant": "角質ケア成分は頻度・濃度で刺激になる場合があります。",
        "memo_ing": "これはルールベースの簡易チェックです。最終判断は製品ラベル・メーカー情報・専門家確認を優先してください。",

        "diary_title": "肌日記（保存 / 一覧）",
        "diary_desc": "今日の状態を短く残して、肌の傾向を見やすくします。",
        "diary_date": "日付",
        "diary_condition": "今日の肌の状態",
        "diary_used": "使用したもの",
        "diary_symptoms": "症状",
        "diary_sleep": "睡眠（時間）",
        "diary_stress": "ストレス（1〜5）",
        "diary_note": "メモ",
        "save_diary": "日記を保存",
        "saved": "保存しました。",
        "diary_list": "日記一覧",
        "no_diary": "日記はまだありません。",

        "trend_title": "傾向メモ",
        "trend_desc": "最近の記録から、睡眠・ストレス・症状の傾向を簡易表示します。",
        "trend_btn": "最近の肌日記を見て傾向を教えて",
        "trend_empty": "日記データはまだありません。",
        "trend_summary": "簡易傾向メモ",
        "avg_sleep": "平均睡眠",
        "avg_stress": "平均ストレス",
        "frequent_symptoms": "よく出る症状",
        "medical_note": "強い赤み・痛み・腫れ・化膿・急な悪化がある場合は皮膚科へ。",

        "routine_title": "朝/夜ルーティン自動作成（ローカル）",
        "routine_desc": "プロフィール条件に合わせて、続けやすい簡易ルーティンを提案します。",
        "routine_btn": "ルーティンを作成",
        "am_routine": "朝ルーティン",
        "pm_routine": "夜ルーティン",
        "routine_tip": "やりすぎより、続けやすさ優先でOK。",

        "tpl_title": "症状別テンプレ提案",
        "tpl_desc": "乾燥 / 赤み / ベタつきの時に使いやすい、やさしめテンプレです。",
        "select_symptom": "症状を選択",
        "show_tpl": "テンプレを表示",
        "do_list": "やること",
        "avoid_list": "避けたいこと",
        "timing_list": "使い方のコツ",

        "prod_title": "ローカル商品提案",
        "prod_desc": "ローカルDBから条件に合う候補を簡易表示します（ブランド推薦ではなくサンプルDBベース）。",
        "show_reco": "おすすめを見る",
        "prod_none": "該当するローカル商品がありません。",
        "prod_note": "※ ローカルDBからの簡易提案です。最終判断は成分・肌状態で確認してください。",
        "prod_price": "価格",
        "prod_type": "カテゴリ",
        "prod_tags": "タグ",
        "score": "相性スコア",

        "type_cleanser": "洗顔",
        "type_lotion": "化粧水",
        "type_serum": "美容液",
        "type_moisturizer": "乳液/クリーム",
        "type_sunscreen": "日焼け止め",
        "type_cleansing": "クレンジング",

        "step_cleanse_light": "ぬるま湯 or やさしい洗顔で軽く整える",
        "step_lotion": "化粧水で水分補給",
        "step_serum_optional": "悩みに合わせて美容液（必要な時だけ）",
        "step_moisturize": "乳液/クリームで保湿",
        "step_sunscreen": "日焼け止めで仕上げ（朝）",
        "step_remove_makeup": "メイク・日焼け止めをやさしく落とす",
        "step_cleanser_night": "洗顔で汚れを落とす",
        "step_repair": "保湿重視で整える",
        "step_sleep_note": "刺激を増やしすぎず、睡眠を優先",

        "tpl_dry_do": "低刺激の保湿中心（化粧水→美容液→クリーム）",
        "tpl_dry_avoid": "角質ケアのやりすぎ / 熱いお湯 / こすり洗い",
        "tpl_dry_tip": "朝は短く、夜は保湿を厚めに",
        "tpl_red_do": "シンプルケア（少ない工程）で様子を見る",
        "tpl_red_avoid": "新しい成分を一気に追加 / 香り強め / 摩擦",
        "tpl_red_tip": "赤みが強い日は攻めのケアを休む",
        "tpl_oily_do": "洗いすぎない範囲で皮脂バランスを整える",
        "tpl_oily_avoid": "脱脂しすぎ / 重すぎる重ね塗り",
        "tpl_oily_tip": "保湿は軽めでもゼロにしない",

        "diary_condition_placeholder": "例）乾燥あり / 頬が少し赤い / 落ち着いている",
        "diary_used_placeholder": "例）化粧水、美容液、クリーム",
        "diary_note_placeholder": "例）睡眠不足、外出長め、エアコン強め など",
    },

    "en": {
        "lang_picker": "Language / 言語",
        "badge": "Local Save Enabled",
        "title": "💄 Beauty Agent Local",
        "subtitle": "Women-Focused Self-Care Web App",
        "desc": "No API / Local save / Ingredient check · Skin diary · Trend memo · AM/PM routine · Symptom templates · Local product suggestions",

        "sidebar_profile": "⚙️ Profile",
        "sidebar_profile_desc": "Gently personalize suggestions for you",
        "skin_type": "Skin type",
        "concerns": "Concerns",
        "fragrance_pref": "Fragrance preference",
        "budget": "Monthly budget (JPY)",
        "am_minutes": "Morning care time (min)",
        "pm_minutes": "Night care time (min)",

        "unset": "Not set",
        "fragrance_free": "Fragrance-free",
        "fragrance_ok": "Fragrance OK",
        "either": "Either",

        "normal": "Normal",
        "dry": "Dry",
        "oily": "Oily",
        "combo": "Combination",
        "sensitive": "Sensitive",

        "concern_dryness": "Dryness",
        "concern_pores": "Pores",
        "concern_redness": "Redness",
        "concern_acne": "Acne",
        "concern_dullness": "Dullness",
        "concern_oiliness": "Oiliness",

        "symptom_dry": "Dryness",
        "symptom_redness": "Redness",
        "symptom_oily": "Oiliness",

        "tab_ing": "Ingredient Check",
        "tab_diary": "Skin Diary",
        "tab_trend": "Trend Memo",
        "tab_routine": "AM/PM Routine",
        "tab_template": "Symptom Templates",
        "tab_products": "Local Products",

        "stat_records": "Records",
        "stat_avg_sleep": "Avg Sleep",
        "stat_avg_stress": "Avg Stress",
        "stat_no_data": "No data",
        "stat_records_sub": "Even 1 line/day is great",
        "stat_sleep_sub": "Easy to review with skin changes",
        "stat_stress_sub": "For lifestyle factor review",

        "chip_skin": "Skin",
        "chip_concerns": "Concerns",
        "chip_fragrance": "Fragrance",
        "chip_budget": "Budget",
        "chip_time": "AM {am}m / PM {pm}m",

        "ing_title": "Ingredient Check (Simple Rule-Based)",
        "ing_desc": "Paste ingredients to roughly check fragrance, fragrance allergens, and potentially drying alcohols.",
        "ing_input_label": "Paste ingredients (comma-separated / line breaks OK)",
        "ing_placeholder": "Water, Glycerin, Niacinamide, Fragrance, Limonene",
        "check": "Check",
        "please_input_ing": "Please enter ingredients.",
        "detected_categories": "Detected categories",
        "cautions": "Cautions",
        "memo": "Memo",
        "matches": "Matched terms",
        "no_hit": "No major caution category found (simple check).",
        "cat_fragrance": "Fragrance",
        "cat_allergen": "Fragrance allergen (incl. essential-oil derived)",
        "cat_drying_alcohol": "Potentially drying alcohol",
        "cat_niacinamide": "Niacinamide",
        "cat_humectant": "Humectants",
        "cat_barrier": "Barrier-support ingredients",
        "cat_exfoliant": "Exfoliating ingredients",
        "cat_vitc": "Vitamin C derivatives",
        "caution_fragrance": "Possible fragrance/fragrance allergens. Patch test recommended for sensitive skin.",
        "caution_alcohol": "If you feel dryness or irritation easily, use with caution.",
        "caution_exfoliant": "Exfoliating ingredients may irritate depending on frequency/concentration.",
        "memo_ing": "This is a simple rule-based check. Confirm with product label, brand info, and professionals when needed.",

        "diary_title": "Skin Diary (Save / List)",
        "diary_desc": "Keep short daily logs to spot your skin trends more easily.",
        "diary_date": "Date",
        "diary_condition": "Today's skin condition",
        "diary_used": "Products used",
        "diary_symptoms": "Symptoms",
        "diary_sleep": "Sleep (hours)",
        "diary_stress": "Stress (1-5)",
        "diary_note": "Note",
        "save_diary": "Save diary",
        "saved": "Saved.",
        "diary_list": "Diary list",
        "no_diary": "No diary entries yet.",

        "trend_title": "Trend Memo",
        "trend_desc": "Shows simple trends from recent logs (sleep, stress, symptoms).",
        "trend_btn": "Analyze recent diary trend",
        "trend_empty": "No diary data yet.",
        "trend_summary": "Simple trend memo",
        "avg_sleep": "Average sleep",
        "avg_stress": "Average stress",
        "frequent_symptoms": "Frequent symptoms",
        "medical_note": "If you have strong redness, pain, swelling, pus, or sudden worsening, see a dermatologist.",

        "routine_title": "AM/PM Routine Generator (Local)",
        "routine_desc": "Creates an easy routine based on your profile and time.",
        "routine_btn": "Create routine",
        "am_routine": "Morning routine",
        "pm_routine": "Night routine",
        "routine_tip": "Consistency matters more than overdoing it.",

        "tpl_title": "Symptom Template Suggestions",
        "tpl_desc": "Gentle templates for dryness / redness / oiliness.",
        "select_symptom": "Select symptom",
        "show_tpl": "Show template",
        "do_list": "Do",
        "avoid_list": "Avoid",
        "timing_list": "Tips",

        "prod_title": "Local Product Suggestions",
        "prod_desc": "Shows matching candidates from local DB (sample DB based, not brand endorsement).",
        "show_reco": "Show recommendations",
        "prod_none": "No matching local products found.",
        "prod_note": "Local DB-based simple suggestion. Always confirm ingredients and your skin condition.",
        "prod_price": "Price",
        "prod_type": "Category",
        "prod_tags": "Tags",
        "score": "Match score",

        "type_cleanser": "Cleanser",
        "type_lotion": "Lotion/Toner",
        "type_serum": "Serum",
        "type_moisturizer": "Moisturizer",
        "type_sunscreen": "Sunscreen",
        "type_cleansing": "Makeup Remover",

        "step_cleanse_light": "Rinse lightly with lukewarm water or gentle cleanser",
        "step_lotion": "Hydrate with lotion/toner",
        "step_serum_optional": "Add serum based on concerns (only when needed)",
        "step_moisturize": "Seal with moisturizer/cream",
        "step_sunscreen": "Finish with sunscreen (AM)",
        "step_remove_makeup": "Gently remove makeup/sunscreen",
        "step_cleanser_night": "Cleanse skin",
        "step_repair": "Focus on hydration and barrier support",
        "step_sleep_note": "Avoid adding too much irritation; prioritize sleep",

        "tpl_dry_do": "Focus on low-irritation hydration (toner → serum → cream)",
        "tpl_dry_avoid": "Over-exfoliation / hot water / harsh rubbing",
        "tpl_dry_tip": "Keep AM short, add extra moisture at night",
        "tpl_red_do": "Use a simple routine with fewer steps",
        "tpl_red_avoid": "Adding many new products / strong fragrance / friction",
        "tpl_red_tip": "Pause aggressive actives on redness days",
        "tpl_oily_do": "Balance sebum without over-cleansing",
        "tpl_oily_avoid": "Over-stripping / overly heavy layering",
        "tpl_oily_tip": "Use lighter hydration, but don't skip moisture",

        "diary_condition_placeholder": "e.g.) Slight dryness / a little redness on cheeks / stable",
        "diary_used_placeholder": "e.g.) toner, serum, cream",
        "diary_note_placeholder": "e.g.) lack of sleep, long time outside, strong AC",
    },

    "ko": {
        "lang_picker": "언어 / Language",
        "badge": "로컬 저장 지원",
        "title": "💄 Beauty Agent Local",
        "subtitle": "여성 맞춤 셀프케어 웹앱",
        "desc": "API 불필요 / 로컬 저장 / 성분 체크 · 피부 일기 · 경향 메모 · 아침/저녁 루틴 · 증상별 템플릿 · 로컬 상품 추천",

        "sidebar_profile": "⚙️ 프로필",
        "sidebar_profile_desc": "당신에게 맞게 제안을 부드럽게 최적화합니다",
        "skin_type": "피부 타입",
        "concerns": "고민",
        "fragrance_pref": "향 선호",
        "budget": "월 예산 (엔)",
        "am_minutes": "아침 케어 시간 (분)",
        "pm_minutes": "저녁 케어 시간 (분)",

        "unset": "미설정",
        "fragrance_free": "무향",
        "fragrance_ok": "향 가능",
        "either": "상관없음",

        "normal": "보통",
        "dry": "건성",
        "oily": "지성",
        "combo": "복합성",
        "sensitive": "민감성",

        "concern_dryness": "건조",
        "concern_pores": "모공",
        "concern_redness": "붉음",
        "concern_acne": "여드름",
        "concern_dullness": "칙칙함",
        "concern_oiliness": "번들거림",

        "symptom_dry": "건조",
        "symptom_redness": "붉음",
        "symptom_oily": "번들거림",

        "tab_ing": "성분 체크",
        "tab_diary": "피부 일기",
        "tab_trend": "경향 메모",
        "tab_routine": "아침/저녁 루틴",
        "tab_template": "증상 템플릿",
        "tab_products": "로컬 상품 추천",

        "stat_records": "기록 수",
        "stat_avg_sleep": "평균 수면",
        "stat_avg_stress": "평균 스트레스",
        "stat_no_data": "미기록",
        "stat_records_sub": "하루 한 줄만 기록해도 좋아요",
        "stat_sleep_sub": "피부 변화와 함께 보기 쉬움",
        "stat_stress_sub": "생활 요인 점검용",

        "chip_skin": "피부",
        "chip_concerns": "고민",
        "chip_fragrance": "향",
        "chip_budget": "예산",
        "chip_time": "아침 {am}분 / 저녁 {pm}분",

        "ing_title": "성분 체크 (간단 룰 기반)",
        "ing_desc": "성분을 붙여 넣으면 향료, 향료 알레르겐, 건조 유발 가능 알코올 등을 대략 확인할 수 있어요.",
        "ing_input_label": "성분 붙여넣기 (쉼표 구분 / 줄바꿈 가능)",
        "ing_placeholder": "Water, Glycerin, Niacinamide, Fragrance, Limonene",
        "check": "체크하기",
        "please_input_ing": "성분을 입력해 주세요.",
        "detected_categories": "검출 카테고리",
        "cautions": "주의점",
        "memo": "메모",
        "matches": "검출어",
        "no_hit": "큰 주의 카테고리는 발견되지 않았습니다 (간단 판정).",
        "cat_fragrance": "향료",
        "cat_allergen": "향료 알레르겐 (에센셜오일 유래 포함)",
        "cat_drying_alcohol": "건조 유발 가능 알코올",
        "cat_niacinamide": "나이아신아마이드",
        "cat_humectant": "보습 성분",
        "cat_barrier": "장벽 보조 성분",
        "cat_exfoliant": "각질 케어 성분",
        "cat_vitc": "비타민C 계열",
        "caution_fragrance": "향료/향 알레르겐 가능성. 민감 피부는 패치 테스트 권장.",
        "caution_alcohol": "건조감/자극을 잘 느끼면 주의해서 사용하세요.",
        "caution_exfoliant": "각질 케어 성분은 빈도/농도에 따라 자극이 될 수 있어요.",
        "memo_ing": "간단한 룰 기반 체크입니다. 최종 판단은 제품 라벨/제조사 정보/전문가 확인을 우선하세요.",

        "diary_title": "피부 일기 (저장 / 목록)",
        "diary_desc": "짧게 기록해서 피부 경향을 보기 쉽게 만듭니다.",
        "diary_date": "날짜",
        "diary_condition": "오늘 피부 상태",
        "diary_used": "사용한 제품",
        "diary_symptoms": "증상",
        "diary_sleep": "수면 (시간)",
        "diary_stress": "스트레스 (1~5)",
        "diary_note": "메모",
        "save_diary": "일기 저장",
        "saved": "저장되었습니다.",
        "diary_list": "일기 목록",
        "no_diary": "아직 일기가 없습니다.",

        "trend_title": "경향 메모",
        "trend_desc": "최근 기록에서 수면/스트레스/증상 경향을 간단히 보여줍니다.",
        "trend_btn": "최근 피부 일기 경향 보기",
        "trend_empty": "아직 일기 데이터가 없습니다.",
        "trend_summary": "간단 경향 메모",
        "avg_sleep": "평균 수면",
        "avg_stress": "평균 스트레스",
        "frequent_symptoms": "자주 나타나는 증상",
        "medical_note": "심한 붉음/통증/붓기/고름/급격한 악화가 있으면 피부과 진료를 권장합니다.",

        "routine_title": "아침/저녁 루틴 자동 생성 (로컬)",
        "routine_desc": "프로필과 시간에 맞춰 꾸준히 하기 쉬운 루틴을 제안합니다.",
        "routine_btn": "루틴 만들기",
        "am_routine": "아침 루틴",
        "pm_routine": "저녁 루틴",
        "routine_tip": "과하게 하기보다 꾸준함이 더 중요해요.",

        "tpl_title": "증상별 템플릿 제안",
        "tpl_desc": "건조 / 붉음 / 번들거림에 맞는 부드러운 템플릿입니다.",
        "select_symptom": "증상 선택",
        "show_tpl": "템플릿 보기",
        "do_list": "할 것",
        "avoid_list": "피할 것",
        "timing_list": "팁",

        "prod_title": "로컬 상품 추천",
        "prod_desc": "로컬 DB 조건 매칭으로 후보를 보여줍니다 (브랜드 추천 아님 / 샘플DB 기반).",
        "show_reco": "추천 보기",
        "prod_none": "조건에 맞는 로컬 상품이 없습니다.",
        "prod_note": "로컬 DB 기반 간단 추천입니다. 최종 판단은 성분과 피부 상태를 확인하세요.",
        "prod_price": "가격",
        "prod_type": "카테고리",
        "prod_tags": "태그",
        "score": "적합도",

        "type_cleanser": "클렌저",
        "type_lotion": "토너/로션",
        "type_serum": "세럼",
        "type_moisturizer": "보습크림/로션",
        "type_sunscreen": "선크림",
        "type_cleansing": "클렌징",

        "step_cleanse_light": "미온수 또는 순한 세안으로 가볍게 정리",
        "step_lotion": "토너/로션으로 수분 보충",
        "step_serum_optional": "고민에 따라 세럼 추가 (필요할 때만)",
        "step_moisturize": "보습제로 마무리",
        "step_sunscreen": "선크림으로 마무리 (아침)",
        "step_remove_makeup": "메이크업/선크림을 부드럽게 제거",
        "step_cleanser_night": "세안으로 노폐물 정리",
        "step_repair": "보습/장벽 중심으로 정돈",
        "step_sleep_note": "자극을 늘리기보다 수면을 우선",

        "tpl_dry_do": "저자극 보습 중심 (토너 → 세럼 → 크림)",
        "tpl_dry_avoid": "과한 각질 케어 / 뜨거운 물 / 문지르기",
        "tpl_dry_tip": "아침은 짧게, 밤에는 보습을 조금 더",
        "tpl_red_do": "단계 수를 줄인 심플 케어",
        "tpl_red_avoid": "새 제품 한꺼번에 추가 / 강한 향 / 마찰",
        "tpl_red_tip": "붉은 날은 공격적인 케어 쉬기",
        "tpl_oily_do": "과세안 없이 유분 균형 맞추기",
        "tpl_oily_avoid": "과한 탈지 / 지나치게 무거운 레이어링",
        "tpl_oily_tip": "가벼운 보습이라도 생략하지 않기",

        "diary_condition_placeholder": "예) 약간 건조 / 볼 붉음 / 안정적",
        "diary_used_placeholder": "예) 토너, 세럼, 크림",
        "diary_note_placeholder": "예) 수면 부족, 장시간 외출, 에어컨 강함",
    },

    "zh": {
        "lang_picker": "语言 / Language",
        "badge": "支持本地保存",
        "title": "💄 Beauty Agent Local",
        "subtitle": "女性向自我护理网页版",
        "desc": "无需 API / 本地保存 / 成分检查·护肤日记·趋势备忘·早晚护理流程·症状模板·本地商品推荐",

        "sidebar_profile": "⚙️ 个人资料",
        "sidebar_profile_desc": "为你温和地优化建议",
        "skin_type": "肤质",
        "concerns": "困扰",
        "fragrance_pref": "香味偏好",
        "budget": "月预算（日元）",
        "am_minutes": "早间护理时间（分钟）",
        "pm_minutes": "夜间护理时间（分钟）",

        "unset": "未设置",
        "fragrance_free": "无香",
        "fragrance_ok": "可接受香味",
        "either": "都可以",

        "normal": "中性",
        "dry": "干性",
        "oily": "油性",
        "combo": "混合性",
        "sensitive": "敏感性",

        "concern_dryness": "干燥",
        "concern_pores": "毛孔",
        "concern_redness": "泛红",
        "concern_acne": "痘痘",
        "concern_dullness": "暗沉",
        "concern_oiliness": "出油",

        "symptom_dry": "干燥",
        "symptom_redness": "泛红",
        "symptom_oily": "出油",

        "tab_ing": "成分检查",
        "tab_diary": "护肤日记",
        "tab_trend": "趋势备忘",
        "tab_routine": "早/晚护理流程",
        "tab_template": "症状模板",
        "tab_products": "本地商品推荐",

        "stat_records": "记录数",
        "stat_avg_sleep": "平均睡眠",
        "stat_avg_stress": "平均压力",
        "stat_no_data": "未记录",
        "stat_records_sub": "每天写一行也很好",
        "stat_sleep_sub": "便于结合皮肤波动查看",
        "stat_stress_sub": "用于回顾生活因素",

        "chip_skin": "肤质",
        "chip_concerns": "困扰",
        "chip_fragrance": "香味",
        "chip_budget": "预算",
        "chip_time": "早{am}分 / 晚{pm}分",

        "ing_title": "成分检查（简易规则版）",
        "ing_desc": "粘贴成分后，可粗略检查香精、香料过敏原、易致干燥酒精等。",
        "ing_input_label": "粘贴成分（逗号分隔 / 可换行）",
        "ing_placeholder": "Water, Glycerin, Niacinamide, Fragrance, Limonene",
        "check": "开始检查",
        "please_input_ing": "请输入成分。",
        "detected_categories": "检测类别",
        "cautions": "注意事项",
        "memo": "备注",
        "matches": "匹配词",
        "no_hit": "未发现明显高风险类别（简易判断）。",
        "cat_fragrance": "香精",
        "cat_allergen": "香料过敏原（含精油来源）",
        "cat_drying_alcohol": "可能致干酒精",
        "cat_niacinamide": "烟酰胺",
        "cat_humectant": "保湿成分",
        "cat_barrier": "屏障支持成分",
        "cat_exfoliant": "去角质成分",
        "cat_vitc": "维C类成分",
        "caution_fragrance": "可能含香精/香料过敏原。敏感肌建议先做局部测试。",
        "caution_alcohol": "若容易干燥或刺激，请谨慎使用。",
        "caution_exfoliant": "去角质成分可能因使用频率/浓度而刺激皮肤。",
        "memo_ing": "这是基于规则的简易检查。最终请以产品标签、品牌信息和专业意见为准。",

        "diary_title": "护肤日记（保存 / 列表）",
        "diary_desc": "记录简短日常，更容易观察皮肤趋势。",
        "diary_date": "日期",
        "diary_condition": "今天的皮肤状态",
        "diary_used": "使用产品",
        "diary_symptoms": "症状",
        "diary_sleep": "睡眠（小时）",
        "diary_stress": "压力（1~5）",
        "diary_note": "备注",
        "save_diary": "保存日记",
        "saved": "已保存。",
        "diary_list": "日记列表",
        "no_diary": "还没有日记记录。",

        "trend_title": "趋势备忘",
        "trend_desc": "根据最近记录，简要显示睡眠/压力/症状趋势。",
        "trend_btn": "查看最近护肤日记趋势",
        "trend_empty": "暂无日记数据。",
        "trend_summary": "简易趋势备忘",
        "avg_sleep": "平均睡眠",
        "avg_stress": "平均压力",
        "frequent_symptoms": "常见症状",
        "medical_note": "如出现明显泛红、疼痛、肿胀、化脓或突然恶化，请及时就诊皮肤科。",

        "routine_title": "早/晚护理流程自动生成（本地）",
        "routine_desc": "根据你的资料和时间，生成更容易坚持的简易流程。",
        "routine_btn": "生成流程",
        "am_routine": "早间流程",
        "pm_routine": "夜间流程",
        "routine_tip": "比起做太多，更重要的是容易坚持。",

        "tpl_title": "症状模板建议",
        "tpl_desc": "适用于干燥 / 泛红 / 出油时的温和模板。",
        "select_symptom": "选择症状",
        "show_tpl": "显示模板",
        "do_list": "建议做",
        "avoid_list": "建议避免",
        "timing_list": "使用小贴士",

        "prod_title": "本地商品推荐",
        "prod_desc": "按条件从本地数据库匹配候选（样例DB，不代表品牌推荐）。",
        "show_reco": "查看推荐",
        "prod_none": "没有符合条件的本地商品。",
        "prod_note": "基于本地数据库的简易推荐。最终请结合成分与皮肤状态判断。",
        "prod_price": "价格",
        "prod_type": "类别",
        "prod_tags": "标签",
        "score": "匹配分",

        "type_cleanser": "洁面",
        "type_lotion": "化妆水/爽肤水",
        "type_serum": "精华",
        "type_moisturizer": "乳液/面霜",
        "type_sunscreen": "防晒",
        "type_cleansing": "卸妆",

        "step_cleanse_light": "用温水或温和洁面轻柔清洁",
        "step_lotion": "用化妆水补水",
        "step_serum_optional": "按困扰选择精华（需要时再加）",
        "step_moisturize": "用乳液/面霜锁水",
        "step_sunscreen": "最后使用防晒（早间）",
        "step_remove_makeup": "温和卸除彩妆/防晒",
        "step_cleanser_night": "洁面清洁",
        "step_repair": "以保湿和屏障护理为主",
        "step_sleep_note": "减少刺激叠加，优先保证睡眠",

        "tpl_dry_do": "以低刺激保湿为核心（化妆水→精华→面霜）",
        "tpl_dry_avoid": "过度去角质 / 热水 / 用力摩擦",
        "tpl_dry_tip": "早上简化，晚上加强保湿",
        "tpl_red_do": "使用更精简的护理步骤观察状态",
        "tpl_red_avoid": "一次加太多新品 / 香味过强 / 摩擦",
        "tpl_red_tip": "泛红明显时暂停刺激性护理",
        "tpl_oily_do": "避免过度清洁，帮助平衡油脂",
        "tpl_oily_avoid": "过度脱脂 / 过厚重叠涂抹",
        "tpl_oily_tip": "保湿可以轻薄，但不要完全省略",

        "diary_condition_placeholder": "例）有点干 / 脸颊稍微泛红 / 状态稳定",
        "diary_used_placeholder": "例）化妆水、精华、面霜",
        "diary_note_placeholder": "例）睡眠不足、外出时间长、空调较强",
    },
}


def get_lang() -> str:
    if "lang_code" not in st.session_state:
        st.session_state["lang_code"] = "ja"
    return st.session_state["lang_code"]


def t(key: str, **kwargs) -> str:
    lang = get_lang()
    text = I18N.get(lang, I18N["ja"]).get(key, I18N["ja"].get(key, key))
    try:
        return text.format(**kwargs)
    except Exception:
        return text


# =========================
# 選択肢ID（内部値は固定）
# =========================
SKIN_TYPE_IDS = ["unset", "normal", "dry", "oily", "combo", "sensitive"]
CONCERN_IDS = [
    "concern_dryness",
    "concern_pores",
    "concern_redness",
    "concern_acne",
    "concern_dullness",
    "concern_oiliness",
]
FRAGRANCE_IDS = ["unset", "fragrance_free", "fragrance_ok", "either"]
SYMPTOM_IDS = ["symptom_dry", "symptom_redness", "symptom_oily"]

PRODUCT_TYPE_IDS = ["type_cleanser", "type_lotion", "type_serum", "type_moisturizer", "type_sunscreen", "type_cleansing"]


def opt_label(opt_id: str) -> str:
    return t(opt_id)


# 既存データ（日本語文字列）互換
LEGACY_MAP = {
    "未設定": "unset",
    "普通肌": "normal",
    "乾燥肌": "dry",
    "脂性肌": "oily",
    "混合肌": "combo",
    "敏感肌": "sensitive",
    "乾燥": "symptom_dry",
    "赤み": "symptom_redness",
    "ベタつき": "symptom_oily",
    "無香料": "fragrance_free",
    "香りありOK": "fragrance_ok",
    "どちらでも": "either",
}


def norm(v: Any) -> Any:
    if isinstance(v, list):
        return [norm(x) for x in v]
    if isinstance(v, str):
        return LEGACY_MAP.get(v, v)
    return v


# =========================
# データI/O
# =========================
def ensure_data_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DIARY_FILE.exists():
        DIARY_FILE.write_text("[]", encoding="utf-8")

    if not PRODUCTS_FILE.exists():
        sample_products = [
            {
                "id": "p001",
                "name": {
                    "ja": "やさしい泡洗顔ジェル",
                    "en": "Gentle Foam Cleanser Gel",
                    "ko": "순한 폼 클렌저 젤",
                    "zh": "温和泡沫洁面啫喱",
                },
                "type": "type_cleanser",
                "price_jpy": 1280,
                "tags": ["fragrance_free", "sensitive", "symptom_redness", "concern_redness"],
                "desc": {
                    "ja": "低刺激寄りの洗顔を想定したローカルDBサンプル。",
                    "en": "Local DB sample for a gentle daily cleanser.",
                    "ko": "저자극 데일리 클렌저를 가정한 로컬 DB 샘플.",
                    "zh": "适合作为温和日常洁面的本地DB样例。",
                },
            },
            {
                "id": "p002",
                "name": {
                    "ja": "しっとり保湿化粧水",
                    "en": "Hydrating Moist Toner",
                    "ko": "촉촉 보습 토너",
                    "zh": "保湿化妆水",
                },
                "type": "type_lotion",
                "price_jpy": 1450,
                "tags": ["fragrance_free", "dry", "sensitive", "symptom_dry", "concern_dryness"],
                "desc": {
                    "ja": "乾燥・敏感寄りに使いやすい想定の保湿化粧水サンプル。",
                    "en": "Hydrating toner sample suited to dry/sensitive skin profiles.",
                    "ko": "건성/민감성 프로필에 맞춘 보습 토너 샘플.",
                    "zh": "适合干性/敏感性倾向的保湿化妆水样例。",
                },
            },
            {
                "id": "p003",
                "name": {
                    "ja": "ナイアシン美容液ライト",
                    "en": "Niacinamide Light Serum",
                    "ko": "나이아신 라이트 세럼",
                    "zh": "烟酰胺轻盈精华",
                },
                "type": "type_serum",
                "price_jpy": 1980,
                "tags": ["fragrance_free", "combo", "oily", "concern_pores", "concern_oiliness"],
                "desc": {
                    "ja": "毛穴・ベタつき向けを想定した軽めの美容液サンプル。",
                    "en": "Light serum sample aimed at pores/oiliness concerns.",
                    "ko": "모공/번들거림 고민용 가벼운 세럼 샘플.",
                    "zh": "适合毛孔/出油困扰的轻盈精华样例。",
                },
            },
            {
                "id": "p004",
                "name": {
                    "ja": "バリア保湿クリーム",
                    "en": "Barrier Moisture Cream",
                    "ko": "장벽 보습 크림",
                    "zh": "屏障保湿面霜",
                },
                "type": "type_moisturizer",
                "price_jpy": 2200,
                "tags": ["fragrance_free", "dry", "sensitive", "symptom_dry", "symptom_redness", "concern_dryness", "concern_redness"],
                "desc": {
                    "ja": "乾燥・赤み時の守りケアに寄せたクリームサンプル。",
                    "en": "Cream sample focused on barrier care for dryness/redness days.",
                    "ko": "건조/붉은 날의 장벽 케어 중심 크림 샘플.",
                    "zh": "适合干燥/泛红时屏障护理的面霜样例。",
                },
            },
            {
                "id": "p005",
                "name": {
                    "ja": "軽やかUVミルク",
                    "en": "Light UV Milk",
                    "ko": "가벼운 UV 밀크",
                    "zh": "轻盈防晒乳",
                },
                "type": "type_sunscreen",
                "price_jpy": 1680,
                "tags": ["either", "combo", "oily", "dry", "concern_dullness"],
                "desc": {
                    "ja": "日中ケア用の軽め日焼け止めサンプル。",
                    "en": "Light daily sunscreen sample for daytime care.",
                    "ko": "낮 케어용 가벼운 선크림 샘플.",
                    "zh": "适合日间护理的轻盈防晒样例。",
                },
            },
            {
                "id": "p006",
                "name": {
                    "ja": "やわらかクレンジングミルク",
                    "en": "Soft Cleansing Milk",
                    "ko": "부드러운 클렌징 밀크",
                    "zh": "柔和卸妆乳",
                },
                "type": "type_cleansing",
                "price_jpy": 1800,
                "tags": ["fragrance_free", "sensitive", "symptom_redness"],
                "desc": {
                    "ja": "夜の摩擦を減らしたい時向けのクレンジングサンプル。",
                    "en": "Cleansing milk sample for gentler nighttime cleansing.",
                    "ko": "밤 세안 마찰을 줄이고 싶을 때용 클렌징 샘플.",
                    "zh": "适合夜间减少摩擦清洁的卸妆样例。",
                },
            },
        ]
        PRODUCTS_FILE.write_text(json.dumps(sample_products, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_diaries() -> List[Dict[str, Any]]:
    data = read_json(DIARY_FILE, [])
    if not isinstance(data, list):
        return []
    cleaned = []
    for x in data:
        if isinstance(x, dict):
            y = {k: norm(v) for k, v in x.items()}
            cleaned.append(y)
    return cleaned


def save_diaries(diaries: List[Dict[str, Any]]) -> None:
    write_json(DIARY_FILE, diaries)


def load_products() -> List[Dict[str, Any]]:
    data = read_json(PRODUCTS_FILE, [])
    return data if isinstance(data, list) else []


# =========================
# UIスタイル（ピンク + ゴールド）
# =========================
def inject_css() -> None:
    st.markdown(
        """
<style>
:root{
  --bg1:#070812;
  --bg2:#0d1020;
  --card: rgba(255,255,255,0.04);
  --card2: rgba(255,255,255,0.06);
  --line: rgba(255,255,255,0.08);
  --text: #f6f2ff;
  --muted: #c8bddc;
  --pink: #ff5da8;
  --pink2:#ff89c2;
  --gold: #d4af37;
  --gold2:#f6d57a;
  --accent-grad: linear-gradient(135deg, rgba(255,93,168,.28), rgba(212,175,55,.22));
  --border-grad: linear-gradient(135deg, rgba(255,93,168,.55), rgba(246,213,122,.45));
}

html, body, [class*="css"]  {
  font-family: "Segoe UI", "Yu Gothic UI", "Meiryo", sans-serif;
}

.stApp {
  background:
    radial-gradient(1200px 500px at 15% 5%, rgba(255,93,168,0.13), transparent 55%),
    radial-gradient(1000px 500px at 90% 0%, rgba(212,175,55,0.10), transparent 60%),
    linear-gradient(180deg, var(--bg2), var(--bg1));
  color: var(--text);
}

section[data-testid="stSidebar"] {
  background:
    radial-gradient(600px 300px at 0% 0%, rgba(255,93,168,.12), transparent 60%),
    linear-gradient(180deg, rgba(255,255,255,.025), rgba(255,255,255,.01));
  border-right: 1px solid rgba(255,255,255,0.06);
}

.block-container {
  padding-top: 1.2rem;
  padding-bottom: 2rem;
  max-width: 1200px;
}

.hero-card {
  position: relative;
  border-radius: 28px;
  padding: 1.2rem 1.4rem 1.2rem 1.4rem;
  background: var(--accent-grad);
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 18px 48px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.05);
  overflow: hidden;
}
.hero-card::before{
  content:"";
  position:absolute;
  inset:-1px;
  border-radius:28px;
  padding:1px;
  background: var(--border-grad);
  -webkit-mask:
    linear-gradient(#000 0 0) content-box,
    linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events:none;
}
.badge {
  display:inline-block;
  padding:.35rem .75rem;
  border-radius:999px;
  font-size: .85rem;
  color:#ffeaf6;
  border:1px solid rgba(255,255,255,.18);
  background: rgba(255,93,168,.12);
  margin-bottom:.7rem;
}
.hero-title {
  font-size: clamp(1.8rem, 2.2vw, 2.6rem);
  line-height:1.1;
  font-weight: 800;
  margin: 0.2rem 0 0.2rem 0;
  letter-spacing: .2px;
}
.hero-sub {
  color: var(--muted);
  margin-top: .35rem;
  font-size: 1.02rem;
}
.chips-wrap { margin-top: .8rem; display:flex; flex-wrap: wrap; gap:.5rem; }
.chip {
  display:inline-flex; align-items:center; gap:.35rem;
  border-radius:999px;
  padding:.38rem .72rem;
  background: rgba(255,255,255,.045);
  border:1px solid rgba(255,255,255,.10);
  color:#eee7fb;
  font-size:.88rem;
}

.metric-card {
  border-radius: 22px;
  padding: 1rem 1.05rem;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
  min-height: 130px;
}
.metric-title { color:#d8cfee; font-size:.95rem; margin-bottom:.25rem; }
.metric-value { font-size: 2rem; font-weight: 800; line-height:1.05; color: #fff; }
.metric-sub { color:#bfb3d6; margin-top:.3rem; font-size:.9rem; }

.section-card{
  border-radius: 24px;
  padding: 1rem 1rem .8rem;
  background: rgba(255,255,255,0.025);
  border: 1px solid rgba(255,255,255,0.07);
  box-shadow: 0 8px 30px rgba(0,0,0,.15), inset 0 1px 0 rgba(255,255,255,.03);
}
.soft-card{
  border-radius: 18px;
  padding: .9rem .95rem;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  margin-bottom: .75rem;
}

.gold-divider {
  height:1px;
  background: linear-gradient(90deg, rgba(255,93,168,.25), rgba(246,213,122,.55), rgba(255,93,168,.12));
  margin: .5rem 0 .8rem;
}

.stButton > button {
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,.12) !important;
  background:
    linear-gradient(135deg, rgba(255,93,168,.95), rgba(212,175,55,.85)) !important;
  color: white !important;
  font-weight: 700 !important;
  box-shadow: 0 8px 22px rgba(255,93,168,.18);
}
.stButton > button:hover{
  filter: brightness(1.03);
  box-shadow: 0 10px 26px rgba(212,175,55,.22);
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
.stTextArea textarea,
.stDateInput input,
.stNumberInput input {
  background: rgba(255,255,255,.03) !important;
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,.10) !important;
  color: white !important;
}
.stTextArea textarea {
  min-height: 120px;
}

[data-testid="stMetric"]{
  background: transparent;
}

.stTabs [data-baseweb="tab-list"]{
  gap: .4rem;
}
.stTabs [data-baseweb="tab"]{
  border-radius: 14px 14px 0 0;
  padding: .6rem .85rem;
}
.stTabs [aria-selected="true"]{
  color: white !important;
  background: rgba(255,93,168,.08) !important;
  border-bottom: 2px solid var(--pink) !important;
}

.product-card {
  border-radius: 18px;
  padding: .95rem;
  background: rgba(255,255,255,.03);
  border: 1px solid rgba(255,255,255,.08);
  margin-bottom: .8rem;
}
.product-title {
  font-weight: 700;
  font-size: 1.03rem;
}
.product-meta {
  color: #cdbfe2;
  font-size: .9rem;
  margin-top: .2rem;
}
.tag {
  display:inline-block; padding:.22rem .55rem; margin:.16rem .2rem 0 0;
  border-radius: 999px; font-size:.8rem;
  color:#f8f4ff;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.08);
}
.small-muted { color: #c5badb; font-size: .9rem; }
.notice {
  border-left: 3px solid rgba(246,213,122,.8);
  padding: .6rem .75rem;
  background: rgba(246,213,122,.06);
  border-radius: 8px;
}

h1,h2,h3,h4 { letter-spacing: .15px; }
</style>
        """,
        unsafe_allow_html=True,
    )


# =========================
# 成分チェック
# =========================
def parse_ingredients(text: str) -> List[str]:
    if not text:
        return []
    parts = re.split(r"[,;\n\r\t]+", text)
    cleaned = []
    for p in parts:
        s = p.strip()
        if s:
            cleaned.append(s)
    return cleaned


def ingredient_check(ingredients: List[str]) -> Dict[str, Any]:
    lower_map = {ing: ing.lower() for ing in ingredients}

    rules = {
        "cat_fragrance": [
            "fragrance", "parfum", "perfume", "aroma"
        ],
        "cat_allergen": [
            "limonene", "linalool", "citral", "citronellol", "geraniol", "eugenol",
            "farnesol", "benzyl alcohol", "benzyl salicylate", "hexyl cinnamal",
            "coumarin", "alpha-isomethyl ionone"
        ],
        "cat_drying_alcohol": [
            "alcohol denat", "sd alcohol", "ethanol", "isopropyl alcohol", "alcohol"
        ],
        "cat_niacinamide": [
            "niacinamide"
        ],
        "cat_humectant": [
            "glycerin", "butylene glycol", "bg", "propylene glycol", "panthenol", "hyaluronic acid", "sodium hyaluronate"
        ],
        "cat_barrier": [
            "ceramide", "cholesterol", "fatty acid", "squalane", "allantoin", "beta-glucan"
        ],
        "cat_exfoliant": [
            "salicylic acid", "glycolic acid", "lactic acid", "aha", "bha", "pha", "gluconolactone"
        ],
        "cat_vitc": [
            "ascorbic acid", "ascorbyl", "3-o-ethyl ascorbic", "magnesium ascorbyl phosphate", "sodium ascorbyl phosphate"
        ],
    }

    hits: Dict[str, List[str]] = {}
    detected = []

    for cat, keywords in rules.items():
        found_terms = []
        for original, lo in lower_map.items():
            for kw in keywords:
                if kw in lo:
                    found_terms.append(original)
                    break
        if found_terms:
            hits[cat] = sorted(list(dict.fromkeys(found_terms)))
            detected.append(cat)

    cautions = []
    if "cat_fragrance" in detected or "cat_allergen" in detected:
        cautions.append("caution_fragrance")
    if "cat_drying_alcohol" in detected:
        cautions.append("caution_alcohol")
    if "cat_exfoliant" in detected:
        cautions.append("caution_exfoliant")

    return {
        "detected": detected,
        "hits": hits,
        "cautions": cautions,
    }


# =========================
# 傾向 / ルーティン / テンプレ
# =========================
def safe_mean(nums: List[float]) -> float | None:
    vals = [x for x in nums if isinstance(x, (int, float))]
    if not vals:
        return None
    try:
        return float(mean(vals))
    except Exception:
        return None


def generate_routine(profile: Dict[str, Any]) -> Dict[str, List[str]]:
    skin = profile.get("skin_type", "unset")
    concerns = set(profile.get("concerns", []))
    fragrance_pref = profile.get("fragrance_pref", "unset")
    am_minutes = int(profile.get("am_minutes", 3))
    pm_minutes = int(profile.get("pm_minutes", 10))

    am_steps: List[str] = []
    pm_steps: List[str] = []

    # 朝
    if am_minutes <= 2:
        am_steps.extend([
            t("step_cleanse_light"),
            t("step_moisturize"),
            t("step_sunscreen"),
        ])
    elif am_minutes <= 5:
        am_steps.extend([
            t("step_cleanse_light"),
            t("step_lotion"),
            t("step_moisturize"),
            t("step_sunscreen"),
        ])
    else:
        am_steps.extend([
            t("step_cleanse_light"),
            t("step_lotion"),
            t("step_serum_optional"),
            t("step_moisturize"),
            t("step_sunscreen"),
        ])

    # 夜
    pm_steps.extend([
        t("step_remove_makeup"),
        t("step_cleanser_night"),
        t("step_lotion"),
    ])

    if pm_minutes >= 6:
        pm_steps.append(t("step_serum_optional"))

    pm_steps.extend([
        t("step_repair"),
        t("step_sleep_note"),
    ])

    # 肌タイプ・悩みで微調整（表示文は追記）
    extras_am = []
    extras_pm = []

    if skin in ("dry", "sensitive") or "concern_dryness" in concerns:
        extras_pm.append("🟡 " + t("tpl_dry_tip"))
    if "concern_redness" in concerns or skin == "sensitive":
        extras_pm.append("🩷 " + t("tpl_red_tip"))
    if "concern_oiliness" in concerns or skin in ("oily", "combo"):
        extras_am.append("✨ " + t("tpl_oily_tip"))
    if fragrance_pref == "fragrance_free":
        extras_pm.append("🌿 " + t("fragrance_pref") + ": " + t("fragrance_free"))

    if extras_am:
        am_steps.extend(extras_am)
    if extras_pm:
        pm_steps.extend(extras_pm)

    return {"am": am_steps, "pm": pm_steps}


def symptom_template(symptom_id: str) -> Dict[str, List[str]]:
    if symptom_id == "symptom_dry":
        return {
            "do": [t("tpl_dry_do")],
            "avoid": [t("tpl_dry_avoid")],
            "tips": [t("tpl_dry_tip")],
        }
    if symptom_id == "symptom_redness":
        return {
            "do": [t("tpl_red_do")],
            "avoid": [t("tpl_red_avoid")],
            "tips": [t("tpl_red_tip")],
        }
    return {
        "do": [t("tpl_oily_do")],
        "avoid": [t("tpl_oily_avoid")],
        "tips": [t("tpl_oily_tip")],
    }


# =========================
# ローカル商品提案
# =========================
def get_product_name(prod: Dict[str, Any]) -> str:
    lang = get_lang()
    name = prod.get("name")
    if isinstance(name, dict):
        return name.get(lang) or name.get("ja") or next(iter(name.values()), prod.get("id", ""))
    return str(name or prod.get("id", ""))


def get_product_desc(prod: Dict[str, Any]) -> str:
    lang = get_lang()
    desc = prod.get("desc")
    if isinstance(desc, dict):
        return desc.get(lang) or desc.get("ja") or next(iter(desc.values()), "")
    return str(desc or "")


def score_product(prod: Dict[str, Any], profile: Dict[str, Any]) -> int:
    score = 0
    tags = set(prod.get("tags", []))

    skin_type = profile.get("skin_type", "unset")
    concerns = set(profile.get("concerns", []))
    fragrance_pref = profile.get("fragrance_pref", "unset")
    budget = int(profile.get("budget", 5000))

    price = int(prod.get("price_jpy", 0))

    # 予算
    if price <= budget:
        score += 3
    elif price <= int(budget * 1.2):
        score += 1
    else:
        score -= 1

    # 肌タイプ
    if skin_type != "unset" and skin_type in tags:
        score += 3

    # 悩み
    for c in concerns:
        if c in tags:
            score += 2

    # 香り
    if fragrance_pref == "fragrance_free":
        if "fragrance_free" in tags:
            score += 3
        elif "fragrance_ok" in tags:
            score -= 1
    elif fragrance_pref == "fragrance_ok":
        score += 1  # 制限弱い
    elif fragrance_pref == "either":
        score += 1

    # 敏感/赤み対応
    if skin_type == "sensitive" and ("sensitive" in tags or "symptom_redness" in tags):
        score += 2

    return score


def recommend_products(products: List[Dict[str, Any]], profile: Dict[str, Any], top_n: int = 6) -> List[Dict[str, Any]]:
    scored = []
    for p in products:
        p2 = dict(p)
        p2["_score"] = score_product(p2, profile)
        scored.append(p2)
    scored.sort(key=lambda x: (x.get("_score", 0), -int(x.get("price_jpy", 0) or 0)), reverse=True)

    # 最低限スコアが低すぎるものを間引く
    filtered = [x for x in scored if x.get("_score", 0) >= 1]
    return (filtered or scored)[:top_n]


# =========================
# ヘルパー描画
# =========================
def chip_html(label: str, value: str) -> str:
    return f"<span class='chip'><strong>{label}:</strong>&nbsp;{value}</span>"


def render_metric_card(title: str, value: str, sub: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-title">{title}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def fmt_hours(v: float | None) -> str:
    if v is None:
        return t("stat_no_data")
    return f"{v:.1f}h"


def fmt_stress(v: float | None) -> str:
    if v is None:
        return t("stat_no_data")
    return f"{v:.1f}/5"


# =========================
# メイン
# =========================
def main() -> None:
    ensure_data_files()
    inject_css()

    # 言語初期化
    _ = get_lang()

    diaries = load_diaries()
    products = load_products()

    # -------------------------
    # Sidebar (Profile)
    # -------------------------
    st.sidebar.markdown(f"### {t('sidebar_profile')}")
    st.sidebar.caption(t("sidebar_profile_desc"))

    lang_name_list = list(LANG_OPTIONS.keys())
    current_lang = get_lang()
    try:
        default_lang_idx = list(LANG_OPTIONS.values()).index(current_lang)
    except ValueError:
        default_lang_idx = 0

    selected_lang_name = st.sidebar.selectbox(
        t("lang_picker"),
        lang_name_list,
        index=default_lang_idx,
    )
    st.session_state["lang_code"] = LANG_OPTIONS[selected_lang_name]

    # 言語切替後に表示再反映
    current_lang = get_lang()

    skin_type = st.sidebar.selectbox(
        t("skin_type"),
        SKIN_TYPE_IDS,
        index=0,
        format_func=opt_label,
    )
    concerns = st.sidebar.multiselect(
        t("concerns"),
        CONCERN_IDS,
        default=[],
        format_func=opt_label,
    )
    fragrance_pref = st.sidebar.selectbox(
        t("fragrance_pref"),
        FRAGRANCE_IDS,
        index=0,
        format_func=opt_label,
    )
    budget = st.sidebar.number_input(t("budget"), min_value=0, value=5000, step=500)
    am_minutes = st.sidebar.slider(t("am_minutes"), min_value=1, max_value=20, value=3)
    pm_minutes = st.sidebar.slider(t("pm_minutes"), min_value=1, max_value=30, value=10)

    profile = {
        "skin_type": skin_type,
        "concerns": concerns,
        "fragrance_pref": fragrance_pref,
        "budget": int(budget),
        "am_minutes": int(am_minutes),
        "pm_minutes": int(pm_minutes),
    }

    # -------------------------
    # サマリー計算
    # -------------------------
    sleeps = [float(d.get("sleep_hours")) for d in diaries if isinstance(d.get("sleep_hours"), (int, float))]
    stresses = [float(d.get("stress")) for d in diaries if isinstance(d.get("stress"), (int, float))]
    avg_sleep = safe_mean(sleeps)
    avg_stress = safe_mean(stresses)

    # -------------------------
    # Header Hero
    # -------------------------
    concerns_text = " / ".join([opt_label(c) for c in concerns]) if concerns else t("unset")
    chips = [
        chip_html(t("chip_skin"), opt_label(skin_type)),
        chip_html(t("chip_concerns"), concerns_text),
        chip_html(t("chip_fragrance"), opt_label(fragrance_pref)),
        chip_html(t("chip_budget"), f"¥{int(budget):,}"),
        chip_html(t("chip_time"), t("chip_time", am=am_minutes, pm=pm_minutes).replace("朝", "").replace("夜", "") if get_lang()=="ja" else t("chip_time", am=am_minutes, pm=pm_minutes)),
    ]

    # 日本語だけ chip_time の label 重複回避（見た目優先）
    if get_lang() == "ja":
        chips[-1] = chip_html("時間", t("chip_time", am=am_minutes, pm=pm_minutes))

    st.markdown(
        f"""
        <div class="hero-card">
            <div class="badge">streamlitApp • {t('badge')}</div>
            <div class="hero-title">{t('title')}<br>{t('subtitle')}</div>
            <div class="hero-sub">{t('desc')}</div>
            <div class="chips-wrap">
                {''.join(chips)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    # -------------------------
    # Metrics row
    # -------------------------
    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card(t("stat_records"), f"{len(diaries)}", t("stat_records_sub"))
    with c2:
        render_metric_card(t("stat_avg_sleep"), fmt_hours(avg_sleep), t("stat_sleep_sub"))
    with c3:
        render_metric_card(t("stat_avg_stress"), fmt_stress(avg_stress), t("stat_stress_sub"))

    st.write("")

    tabs = st.tabs([
        t("tab_ing"),
        t("tab_diary"),
        t("tab_trend"),
        t("tab_routine"),
        t("tab_template"),
        t("tab_products"),
    ])

    # -------------------------
    # Tab 1: Ingredient Check
    # -------------------------
    with tabs[0]:
        st.markdown(f"## {t('ing_title')}")
        st.caption(t("ing_desc"))
        ing_text = st.text_area(
            t("ing_input_label"),
            value="Water, Glycerin, Niacinamide, Fragrance, Limonene",
            placeholder=t("ing_placeholder"),
            height=120,
            key="ing_text",
        )

        if st.button(t("check"), key="btn_check_ing"):
            ingredients = parse_ingredients(ing_text)
            if not ingredients:
                st.warning(t("please_input_ing"))
            else:
                result = ingredient_check(ingredients)

                st.markdown("<div class='section-card'>", unsafe_allow_html=True)
                st.markdown(f"### {t('detected_categories')}")
                if result["detected"]:
                    cats = " / ".join([t(cat) for cat in result["detected"]])
                    st.success(cats)
                else:
                    st.info(t("no_hit"))

                if result["hits"]:
                    st.markdown(f"### {t('matches')}")
                    for cat, words in result["hits"].items():
                        st.markdown(
                            f"<div class='soft-card'><strong>{t(cat)}</strong><br><span class='small-muted'>{', '.join(words)}</span></div>",
                            unsafe_allow_html=True,
                        )

                st.markdown(f"### {t('cautions')}")
                if result["cautions"]:
                    for ck in result["cautions"]:
                        st.markdown(f"- {t(ck)}")
                else:
                    st.markdown(f"- {t('memo_ing')}")

                st.markdown(f"### {t('memo')}")
                st.markdown(f"<div class='notice'>{t('memo_ing')}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------
    # Tab 2: Diary
    # -------------------------
    with tabs[1]:
        st.markdown(f"## {t('diary_title')}")
        st.caption(t("diary_desc"))

        with st.form("diary_form", clear_on_submit=False):
            col_a, col_b = st.columns([1, 1])
            with col_a:
                diary_date = st.date_input(t("diary_date"), value=date.today())
                diary_condition = st.text_input(t("diary_condition"), placeholder=t("diary_condition_placeholder"))
                used_items = st.text_input(t("diary_used"), placeholder=t("diary_used_placeholder"))
                diary_symptoms = st.multiselect(t("diary_symptoms"), SYMPTOM_IDS, format_func=opt_label)
            with col_b:
                sleep_hours = st.number_input(t("diary_sleep"), min_value=0.0, max_value=24.0, value=5.0, step=0.5)
                stress = st.slider(t("diary_stress"), 1, 5, 3)
                diary_note = st.text_area(t("diary_note"), placeholder=t("diary_note_placeholder"), height=110)

            submitted = st.form_submit_button(t("save_diary"))

        if submitted:
            entry = {
                "date": str(diary_date),
                "condition": diary_condition.strip(),
                "used_items": used_items.strip(),
                "symptoms": diary_symptoms,
                "sleep_hours": float(sleep_hours),
                "stress": int(stress),
                "note": diary_note.strip(),
                "profile_skin_type": skin_type,
                "profile_concerns": concerns,
                "profile_fragrance_pref": fragrance_pref,
                "profile_budget": int(budget),
                "profile_am_minutes": int(am_minutes),
                "profile_pm_minutes": int(pm_minutes),
                "saved_at": datetime.now().isoformat(timespec="seconds"),
                "lang": get_lang(),
            }
            diaries.append(entry)
            diaries.sort(key=lambda x: x.get("date", ""), reverse=True)
            save_diaries(diaries)
            st.success(t("saved"))

        st.markdown("<div class='gold-divider'></div>", unsafe_allow_html=True)
        st.markdown(f"### {t('diary_list')}")

        if not diaries:
            st.info(t("no_diary"))
        else:
            for i, d in enumerate(diaries[:30], start=1):
                d_date = d.get("date", "")
                d_cond = d.get("condition", "")
                d_used = d.get("used_items", "")
                d_sym = [opt_label(x) for x in norm(d.get("symptoms", [])) if isinstance(x, str)]
                d_sleep = d.get("sleep_hours", "")
                d_stress = d.get("stress", "")
                d_note = d.get("note", "")

                title = f"{d_date}  |  {d_cond if d_cond else t('stat_no_data')}"
                with st.expander(title, expanded=(i == 1)):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**{t('diary_used')}**")
                        st.write(d_used or "-")
                        st.markdown(f"**{t('diary_symptoms')}**")
                        st.write(" / ".join(d_sym) if d_sym else "-")
                    with c2:
                        st.markdown(f"**{t('diary_sleep')}**")
                        st.write(f"{d_sleep}" if d_sleep != "" else "-")
                        st.markdown(f"**{t('diary_stress')}**")
                        st.write(f"{d_stress}" if d_stress != "" else "-")
                    st.markdown(f"**{t('diary_note')}**")
                    st.write(d_note or "-")

    # -------------------------
    # Tab 3: Trend Memo
    # -------------------------
    with tabs[2]:
        st.markdown(f"## {t('trend_title')}")
        st.caption(t("trend_desc"))

        if st.button(t("trend_btn"), key="btn_trend"):
            if not diaries:
                st.info(t("trend_empty"))
            else:
                recent = diaries[:14]  # 直近14件ベース
                recent_sleeps = [float(d.get("sleep_hours")) for d in recent if isinstance(d.get("sleep_hours"), (int, float))]
                recent_stresses = [float(d.get("stress")) for d in recent if isinstance(d.get("stress"), (int, float))]
                symptom_counter = Counter()

                for d in recent:
                    for s in norm(d.get("symptoms", [])):
                        if isinstance(s, str) and s in SYMPTOM_IDS:
                            symptom_counter[s] += 1

                rs = safe_mean(recent_sleeps)
                rt = safe_mean(recent_stresses)

                st.markdown("<div class='section-card'>", unsafe_allow_html=True)
                st.markdown(f"### {t('trend_summary')}")
                st.markdown(f"- **{t('avg_sleep')}**: {fmt_hours(rs)}")
                st.markdown(f"- **{t('avg_stress')}**: {fmt_stress(rt)}")

                if symptom_counter:
                    top_sym = " / ".join([f"{opt_label(k)}({v})" for k, v in symptom_counter.most_common(5)])
                else:
                    top_sym = t("stat_no_data")
                st.markdown(f"- **{t('frequent_symptoms')}**: {top_sym}")

                st.markdown(f"<div class='notice'>{t('medical_note')}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------
    # Tab 4: Routine
    # -------------------------
    with tabs[3]:
        st.markdown(f"## {t('routine_title')}")
        st.caption(t("routine_desc"))

        if st.button(t("routine_btn"), key="btn_routine"):
            rt = generate_routine(profile)
            ca, cb = st.columns(2)

            with ca:
                st.markdown(f"### ☀️ {t('am_routine')}")
                st.markdown("<div class='section-card'>", unsafe_allow_html=True)
                for step in rt["am"]:
                    st.markdown(f"- {step}")
                st.markdown("</div>", unsafe_allow_html=True)

            with cb:
                st.markdown(f"### 🌙 {t('pm_routine')}")
                st.markdown("<div class='section-card'>", unsafe_allow_html=True)
                for step in rt["pm"]:
                    st.markdown(f"- {step}")
                st.markdown("</div>", unsafe_allow_html=True)

            st.caption(t("routine_tip"))

    # -------------------------
    # Tab 5: Symptom Templates
    # -------------------------
    with tabs[4]:
        st.markdown(f"## {t('tpl_title')}")
        st.caption(t("tpl_desc"))

        symptom_selected = st.selectbox(
            t("select_symptom"),
            SYMPTOM_IDS,
            format_func=opt_label,
            key="symptom_template_select",
        )

        if st.button(t("show_tpl"), key="btn_template"):
            tpl = symptom_template(symptom_selected)

            c_do, c_avoid, c_tip = st.columns(3)
            with c_do:
                st.markdown(f"### ✅ {t('do_list')}")
                st.markdown("<div class='section-card'>", unsafe_allow_html=True)
                for x in tpl["do"]:
                    st.markdown(f"- {x}")
                st.markdown("</div>", unsafe_allow_html=True)
            with c_avoid:
                st.markdown(f"### ⚠️ {t('avoid_list')}")
                st.markdown("<div class='section-card'>", unsafe_allow_html=True)
                for x in tpl["avoid"]:
                    st.markdown(f"- {x}")
                st.markdown("</div>", unsafe_allow_html=True)
            with c_tip:
                st.markdown(f"### ✨ {t('timing_list')}")
                st.markdown("<div class='section-card'>", unsafe_allow_html=True)
                for x in tpl["tips"]:
                    st.markdown(f"- {x}")
                st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------
    # Tab 6: Local Products
    # -------------------------
    with tabs[5]:
        st.markdown(f"## {t('prod_title')}")
        st.caption(t("prod_desc"))

        if st.button(t("show_reco"), key="btn_products"):
            recos = recommend_products(products, profile, top_n=8)

            if not recos:
                st.info(t("prod_none"))
            else:
                for p in recos:
                    name = get_product_name(p)
                    ptype = t(p.get("type", "type_serum"))
                    price = int(p.get("price_jpy", 0))
                    desc = get_product_desc(p)
                    score = p.get("_score", 0)
                    tags = p.get("tags", [])

                    # タグ表示（翻訳できるものだけ翻訳）
                    tag_labels = []
                    for tag in tags:
                        if isinstance(tag, str):
                            if tag in I18N["ja"] or tag in SYMPTOM_IDS or tag in CONCERN_IDS or tag in SKIN_TYPE_IDS or tag in FRAGRANCE_IDS:
                                tag_labels.append(t(tag))
                            else:
                                tag_labels.append(tag)

                    st.markdown(
                        f"""
                        <div class="product-card">
                          <div class="product-title">{name}</div>
                          <div class="product-meta">{t('prod_type')}: {ptype} &nbsp;|&nbsp; {t('prod_price')}: ¥{price:,} &nbsp;|&nbsp; {t('score')}: {score}</div>
                          <div style="margin-top:.35rem;">{desc}</div>
                          <div style="margin-top:.35rem;">
                            {''.join([f"<span class='tag'>{tg}</span>" for tg in tag_labels[:8]])}
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.caption(t("prod_note"))


if __name__ == "__main__":
    main()