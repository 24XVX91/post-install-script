
def _extract_version_after_colon(self, text, keyword):
    """通用方法：从包含关键词的行提取冒号后的版本号"""
    for line in text.splitlines():
        if keyword in line:
            return line.split(":")[-1].strip()
    return None

def _extract_version_pattern(self, text, keyword, pattern_check):
    """通用方法：按自定义规则提取版本"""
    for line in text.splitlines():
        if keyword in line:
            parts = line.split()
            for p in parts:
                if pattern_check(p):
                    return p
    return None