from typing import Optional,  Iterable

font_grade_order = [
    "3", "3+", "4", "4+", "5", "5+", 
    "6a", "6a+", "6b", "6b+", "6c", "6c+",
    "7a", "7a+", "7b", "7b+", "7c", "7c+",
    "8a", "8a+", "8b", "8b+", "8c", "8c+", "9a"
]
v_grade_order = [
    "VB", "V0", "V1", "V2", "V3", "V4", "V5",
    "V6", "V7", "V8", "V9", "V10", "V11",
    "V12", "V13", "V14", "V15", "V16", "V17"
]

V_to_Font ={
    "VB": "3",
    "V0":  "4",
    "V1":  "5",
    "V2":  "5+",
    "V3":  "6a",
    "V4":  "6b",
    "V5":  "6v",
    "V6":  "7a",
    "V7":  "7a+",
    "V8":  "7b",
    "V9":  "7b+",
    "V10": "7c",
    "V11": "8a",
    "V12": "8a+",
    "V13": "8b",
    "V14": "8b+",
    "V15": "8c",
    "V16": "8c+",
    "V17": "9a"
}

font_index = {grade: index for index, grade in enumerate(font_grade_order)}
index_to_font = {index: grade for index, grade in enumerate(font_grade_order)}

def convert_to_font(grade: Optional[str]) -> Optional[str]:
    if not grade:
        return None

    g = str(grade).strip()
    if not g:
        return None

    # font grades => lowercase for matching
    if not g.upper().startswith("V"):
        g = g.lower()
        return g if g in font_index else None

    # V grades
    g = g.upper()
    core = g.replace("+", "")
    mapped = V_to_Font.get(core)
    return mapped.lower() if mapped else None

    
def grade_to_numeric(grade: str) -> int:
    font_grade = convert_to_font(grade)
    return font_index.get(font_grade) if font_grade else None

def highest_grade(grades: Iterable[str]) -> Optional[str]:
    max_index = -1
    best_grade = None

    for grade in grades:
        index = grade_to_numeric(grade)
        if index is not None and index > max_index:
            max_index = index
            best_grade = grade
    return best_grade if max_index > 0 else None