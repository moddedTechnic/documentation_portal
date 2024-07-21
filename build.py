import json
import shutil
import subprocess
from pathlib import Path

import typst

DOCS_DIR = Path("docs")
CONTENT_DIR = Path("content")
STATIC_DIR = Path("static")

RENDERED_DOCS_DIR = STATIC_DIR / "docs"


def build_typst(path: Path):
    rel_path = path.relative_to(DOCS_DIR)

    c = typst.Compiler(
        str(path),
        font_paths=["static/fonts/"],
        root=str(DOCS_DIR),
    )

    title = json.loads(c.query("<title>", field="value", one=True))
    author = json.loads(c.query("<author>", field="value"))

    c.compile(output=str(RENDERED_DOCS_DIR / rel_path.with_suffix(".pdf").name))

    with (CONTENT_DIR / rel_path.with_suffix(".md")).open("w") as f:
        f.writelines([
            "---\n",
            f"title: {title}\n",
            f"author: {author}\n",
            f"type: document\n",
            f"path: /docs/{rel_path.with_suffix('.pdf')}\n",
            "---\n",
        ])


def main():
    if CONTENT_DIR.exists():
        shutil.rmtree(CONTENT_DIR)
    if RENDERED_DOCS_DIR.exists():
        shutil.rmtree(RENDERED_DOCS_DIR)

    CONTENT_DIR.mkdir(parents=True)
    RENDERED_DOCS_DIR.mkdir(parents=True)

    for path in DOCS_DIR.glob("*"):
        if path.is_dir():
            continue
        if path.name.startswith('_') and path.name != '_index.md':
            continue
        if path.name.startswith('.'):
            continue
        if path.suffix in {'.typ', '.typst'}:
            build_typst(path)
        elif path.suffix == '.md':
            rel_path = path.relative_to(DOCS_DIR)
            shutil.copy(path, CONTENT_DIR / rel_path)
        else:
            rel_path = path.relative_to(DOCS_DIR)
            shutil.copy(path, RENDERED_DOCS_DIR / rel_path)

    subprocess.run(["hugo"], check=True)


if __name__ == "__main__":
    main()
