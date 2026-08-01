
SUBJECTS = [
    {"id": "itgs111", "code": "ITGS111", "name": "مقدمة في تقنية المعلومات"},
    {"id": "itgs113", "code": "ITGS113", "name": "الحلول التقنية"},
    {"id": "itgs215", "code": "ITGS215", "name": "مقدمة في هندسة الشبكات"},
    {"id": "itgs213", "code": "ITGS213", "name": "مقدمة في هندسة البرمجيات"},
    {"id": "itgs126", "code": "ITGS126", "name": "تصميم الدوائر المنطقية"},
    {"id": "itgs122", "code": "ITGS122", "name": "مقدمة في البرمجة"},
    {"id": "itgs226", "code": "ITGS226", "name": "مقدمة في برمجة الانترنت"},
    {"id": "itmm122", "code": "ITMM122", "name": "رياضة 2"},
    {"id": "itgs217", "code": "ITGS217", "name": "تراكيب منفصلة"},
    {"id": "itel121", "code": "ITEL121", "name": "لغة إنجليزية 2"},
    {"id": "itgs304", "code": "ITGS304", "name": "كتابة التقارير العلمية"},
    {"id": "itar121", "code": "ITAR121", "name": "لغة عربية 2"},
    {"id": "itgs223", "code": "ITGS223", "name": "معمارية الحاسوب"},
    {"id": "itgs220", "code": "ITGS220", "name": "تراكيب البيانات"},
    {"id": "itgs242", "code": "ITGS242", "name": "مقدمة في علم البيانات"},
    {"id": "itgs211", "code": "ITGS211", "name": "البرمجة الشيئية"},
    {"id": "itgs219", "code": "ITGS219", "name": "التحليل العددي"},
    {"id": "itgs228", "code": "ITGS228", "name": "مقدمة في قواعد البيانات"},
    {"id": "itgs240", "code": "ITGS240", "name": "مقدمة في الذكاء الاصطناعي"},
    {"id": "itgs224", "code": "ITGS224", "name": "أمن المعلومات"},
    {"id": "itgs303", "code": "ITGS303", "name": "إدارة المشاريع"},
    {"id": "itgs302", "code": "ITGS302", "name": "نظم التشغيل"},
    {"id": "itgs301", "code": "ITGS301", "name": "تصميم وتحليل الخوارزميات"},
]


def get_subject(subject_id):
    for s in SUBJECTS:
        if s["id"] == subject_id:
            return s
    return None
