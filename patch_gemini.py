with open('care/services/gemini.py', 'r') as f:
    content = f.read()

import_str = "import logging\n\nlogger = logging.getLogger(__name__)\n"
content = content.replace('from google.genai import types', 'from google.genai import types\n' + import_str)

# query_memory
content = content.replace('    client = _client()', '    logger.info(f"Querying Gemini API with query: {query}")\n    logger.debug(f"Full prompt context: {prompt}")\n    client = _client()')
content = content.replace('    result = json.loads(raw_text)', '    logger.debug(f"Gemini API response: {raw_text}")\n    result = json.loads(raw_text)')

# generate_speech
content = content.replace('def generate_speech(text: str) -> str | None:', 'def generate_speech(text: str) -> str | None:\n    logger.info(f"Generating TTS for text: {text}")')
content = content.replace('        print(f"TTS error: {e}")', '        logger.error(f"TTS error: {e}", exc_info=True)')

# get_helpful_tip
content = content.replace('def get_helpful_tip() -> str:', 'def get_helpful_tip() -> str:\n    logger.info("Requesting helpful tip from Gemini")')
content = content.replace('    except Exception:', '    except Exception as e:\n        logger.error(f"Tip generation error: {e}", exc_info=True)')

with open('care/services/gemini.py', 'w') as f:
    f.write(content)
