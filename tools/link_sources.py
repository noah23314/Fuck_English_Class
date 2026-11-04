"""Turn footnote citations into direct source links and a numbered reference list.

Usage: python -I tools/link_sources.py FILE
"""
import re
import sys

URLS = {
    1: "https://www.chinanews.com.cn/m/dxw/2026/02-21/10574936.shtml",
    2: "http://js.people.com.cn/n2/2026/0428/c360303-41565094.html",
    4: "http://paper.people.com.cn/rmrbhwb/pc/content/202609/11/content_30180501.html",
    5: "https://www.dpm.org.cn/lemmas/241317.html",
    6: "https://www.dpm.org.cn/collection/embroider/228698.html",
    7: "https://www.dpm.org.cn/lemmas/242132.html",
    8: "http://paper.people.com.cn/rmrbhwb/pc/content/202609/11/content_30180502.html",
    9: "https://www.dpm.org.cn/lemmas/241368.html",
    10: "https://www.dpm.org.cn/lemmas/244511.html",
    11: "https://www.dpm.org.cn/lemmas/245233.html",
    12: "https://www.dpm.org.cn/lemmas/239382.html",
    13: "http://ahczww.com/news/xwdt/2020-04-01/8256.html",
    14: "https://m.cnacs.net.cn/19/202204/3893.html",
    15: "https://www.dpm.org.cn/lemmas/241324.html",
    16: "https://www.dpm.org.cn/collection/ceramic/227777.html",
    17: "https://www.dpm.org.cn/lemmas/241316.html",
}


def main(path):
    text = open(path, encoding="utf-8").read()
    marker = "## 九、引用资料"
    body, refs = text.split(marker, 1)

    def cite(m):
        n = int(m.group(1))
        if n in URLS:
            return f"[<sup>{n}</sup>]({URLS[n]})"
        return f"<sup>{n}</sup>"

    body = re.sub(r"\[\^(\d+)\]", cite, body)

    refs = re.sub(r"^\[\^(\d+)\]:\s*", lambda m: f"**{m.group(1)}.** ", refs, flags=re.M)
    refs = re.sub(r"(https?://[^\s（]+)", r"<\1>", refs)

    note = (
        "本文所据资料主要有四类：故宫博物院的术语词条与藏品说明（用于纹样定义、名物考释与实物描述）；"
        "《人民日报海外版》的专题报道（用于通史脉络与民间纹样）；地方博物馆、学会的科普文章（用于缠枝纹、"
        "宝相花等专题）；以及中新社对吴文化博物馆馆长陈曾路的专访（用于纹样的文化定位与当代转化）。"
        "**文中上标编号均可点击，直接打开对应原文；编号 3、18 分别指古籍与图版授权说明。** 各条出处如下。\n\n"
    )

    # Replace the existing introductory paragraph before the numbered entries.
    refs = re.sub(
        r"^本文所据资料主要有四类：.*?各条出处如下。\n\n",
        note,
        refs,
        count=1,
        flags=re.S,
    )

    open(path, "w", encoding="utf-8").write(body + marker + refs)


if __name__ == "__main__":
    main(sys.argv[1])
