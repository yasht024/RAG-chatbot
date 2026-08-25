import sys
import re
import datetime

file_path = 'packages/retrieval/search.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"2026-08-23"', 'TODAY_STR')
content = content.replace('from typing import List, Dict, Any, Optional', 'import datetime\nfrom typing import List, Dict, Any, Optional\n\nTODAY_STR = datetime.date.today().strftime("%Y-%m-%d")')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('search.py patched')
