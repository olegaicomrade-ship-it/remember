import json
import os
import shutil
import sys
from datetime import datetime

# --- КОНСТАНТЫ ---
HTML_FILE = 'index.html'
TRIGGERS_FILE = 'triggers.txt'

JSON_TAG_START = '<script type="application/ld+json" id="seo-data">'
JSON_TAG_END = '</script>'
AI_TAG_START = '<p itemprop="description">'
AI_TAG_END = '</p>'

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def update_all_seo():
    if not os.path.exists(HTML_FILE):
        log("КРИТИЧЕСКАЯ ОШИБКА: index.html не найден.")
        return False

    triggers_list = []
    if os.path.exists(TRIGGERS_FILE):
        try:
            with open(TRIGGERS_FILE, 'r', encoding='utf-8') as f:
                raw_data = f.read().replace('\n', ',').split(',')
                triggers_list = [t.strip() for t in raw_data if t.strip()]
        except Exception as e:
            log(f"ОШИБКА при чтении триггеров: {e}")
            return False

    if not triggers_list:
        log("ОШИБКА: Список триггеров пуст. Операция отменена.")
        return False

    triggers_str = ", ".join(triggers_list)
    keywords_str = ", ".join(triggers_list[:15])

    try:
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        log(f"ОШИБКА при чтении HTML: {e}")
        return False

    def inject_content(source, s_tag, e_tag, new_data):
        start_pos = source.find(s_tag)
        if start_pos == -1: return None
        idx_after_start = start_pos + len(s_tag)
        end_pos = source.find(e_tag, idx_after_start)
        if end_pos == -1: return None
        return source[:idx_after_start] + "\n" + new_data + "\n" + source[end_pos:]

    seo_metadata = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": "Ты помнишь?",
        "description": triggers_str,
        "keywords": keywords_str,
        "dateModified": datetime.now().strftime("%Y-%m-%d")
    }
    json_payload = json.dumps(seo_metadata, ensure_ascii=False, indent=2)

    # Инъекция JSON-LD
    temp_html = inject_content(html_content, JSON_TAG_START, JSON_TAG_END, json_payload)
    if temp_html is None:
        log("ОШИБКА: Блок JSON-LD не найден.")
        return False

    # Инъекция AI-блока
    final_html = inject_content(temp_html, AI_TAG_START, AI_TAG_END, triggers_str)
    if final_html is None:
        log("ОШИБКА: AI-блок не найден.")
        return False

    try:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        shutil.copyfile(HTML_FILE, f"{HTML_FILE}_{ts}.bak")
        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(final_html)
        log(f"УСПЕХ: Сайт обновлен. Триггеров: {len(triggers_list)}")
        return True
    except Exception as e:
        log(f"КРИТИЧЕСКАЯ ОШИБКА при записи: {e}")
        return False

if __name__ == "__main__":
    success = update_all_seo()
    if success:
        log("Процесс завершен успешно.")
        sys.exit(0)
    else:
        log("Процесс завершен с ошибкой.")
        sys.exit(1)
