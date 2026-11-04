"""Download public-domain images and metadata from the Metropolitan Museum of Art.

Usage: python -I tools/fetch_met.py OUTDIR ID [ID ...]
"""
import json
import os
import sys
import time
import urllib.request

API = "https://collectionapi.metmuseum.org/public/collection/v1/objects/{}"


def get(url, tries=4):
    for n in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read()
        except Exception as exc:  # noqa: BLE001
            if n == tries - 1:
                raise
            print(f"  retry {n + 1}: {exc}", file=sys.stderr)
            time.sleep(2)


def main(outdir, ids):
    os.makedirs(outdir, exist_ok=True)
    index = []
    for oid in ids:
        print(f"object {oid}")
        meta = json.loads(get(API.format(oid)))
        if not meta.get("isPublicDomain"):
            print("  skip: not public domain")
            continue
        img_url = meta.get("primaryImageSmall") or meta.get("primaryImage")
        if not img_url:
            print("  skip: no image")
            continue
        ext = os.path.splitext(img_url.split("?")[0])[1] or ".jpg"
        name = f"met_{oid}{ext}"
        with open(os.path.join(outdir, name), "wb") as f:
            f.write(get(img_url))
        rec = {
            "id": oid,
            "file": name,
            "title": meta.get("title"),
            "culture": meta.get("culture"),
            "period": meta.get("period"),
            "date": meta.get("objectDate"),
            "medium": meta.get("medium"),
            "credit": meta.get("creditLine"),
            "url": meta.get("objectURL"),
            "image": img_url,
        }
        index.append(rec)
        print(f"  saved {name}")
    with open(os.path.join(outdir, "met_images.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
