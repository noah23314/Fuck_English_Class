"""Extract readable text from a saved HTML page. Usage: python -I tools/extract.py FILE [FILE...]"""
import re
import sys
import html


def decode(data: bytes) -> str:
    m = re.search(rb'charset=["\']?([\w-]+)', data[:4000], re.I)
    if m:
        enc = m.group(1).decode("ascii", "ignore").lower()
        if enc in ("gb2312", "gbk", "gb18030"):
            enc = "gb18030"
        try:
            return data.decode(enc)
        except (LookupError, UnicodeDecodeError):
            pass
    for enc in ("utf-8", "gb18030"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", "replace")


def main(paths):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for path in paths:
        with open(path, "rb") as f:
            text = decode(f.read())
        text = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.S | re.I)
        text = re.sub(r"<br\s*/?>|</p>|</div>|</h\d>|</li>|</tr>", "\n", text, flags=re.I)
        text = re.sub(r"<[^>]+>", "", text)
        text = html.unescape(text)
        lines = [re.sub(r"[ \t　]+", " ", ln).strip() for ln in text.split("\n")]
        lines = [ln for ln in lines if ln]
        print(f"\n===== {path} =====")
        print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1:])
