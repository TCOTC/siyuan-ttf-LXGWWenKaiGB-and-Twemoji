#!/usr/bin/env python3
"""
从 LXGWWenKai/ 下的字体文件中移除与 Twemoji 冲突的字形。

码位列表见同目录 wenkai-excluded-unicodes.txt。更新字体后重新执行：

  pip install -r scripts/requirements-fonttools.txt
  pnpm strip-wenkai-glyphs

默认就地覆盖，并将原文件保存为同名的 .bak；加 --no-backup 可不保留备份。
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FONT_DIR = REPO_ROOT / "LXGWWenKai"
DEFAULT_EXCLUDE_FILE = Path(__file__).resolve().parent / "wenkai-excluded-unicodes.txt"
FONT_SUFFIXES = {".woff", ".woff2", ".ttf", ".otf"}


def _import_fonttools():
    try:
        from fontTools.subset import Options, Subsetter
        from fontTools.ttLib import TTFont
    except ImportError as exc:
        print(
            "缺少 fonttools，请先安装：\n"
            "  pip install -r scripts/requirements-fonttools.txt",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc
    return Options, Subsetter, TTFont


def load_excluded_unicodes(path: Path) -> set[int]:
    codes: set[int] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        codes.add(int(line, 16))
    if not codes:
        raise ValueError(f"未在 {path} 中读到任何码位")
    return codes


def collect_unicodes(font) -> set[int]:
    unicodes: set[int] = set()
    for table in font["cmap"].tables:
        if table.isUnicode():
            unicodes.update(table.cmap.keys())
    return unicodes


def flavor_for_suffix(suffix: str) -> str | None:
    if suffix == ".woff":
        return "woff"
    if suffix == ".woff2":
        return "woff2"
    return None


def subset_font(
    input_path: Path,
    output_path: Path,
    excluded: set[int],
    *,
    Options,
    Subsetter,
    TTFont,
) -> tuple[int, int]:
    font = TTFont(input_path, lazy=True)
    present = collect_unicodes(font)
    removed = present & excluded
    keep = present - excluded

    if not removed:
        print(f"  跳过（无冲突字形）: {input_path.name}")
        if output_path != input_path:
            shutil.copy2(input_path, output_path)
        return 0, 0

    options = Options()
    options.layout_features = ["*"]
    options.name_Legacy = True
    options.name_IDs = ["*"]
    options.recalc_bounds = True
    options.recalc_timestamp = True
    flavor = flavor_for_suffix(input_path.suffix.lower())
    if flavor:
        options.flavor = flavor

    subsetter = Subsetter(options=options)
    subsetter.populate(unicodes=keep)
    subsetter.subset(font)
    font.save(output_path)

    verify = collect_unicodes(TTFont(output_path, lazy=True))
    still = verify & excluded
    if still:
        hexes = ", ".join(f"U+{cp:04X}" for cp in sorted(still))
        raise RuntimeError(f"subset 后仍存在应删除的码位: {hexes}")

    print(
        f"  {input_path.name}: 移除 {len(removed)} 个字形 "
        f"({', '.join(f'U+{cp:04X}' for cp in sorted(removed))})"
    )
    return len(removed), len(keep)


def iter_font_files(font_dir: Path) -> list[Path]:
    return sorted(
        p
        for p in font_dir.iterdir()
        if p.is_file() and p.suffix.lower() in FONT_SUFFIXES
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dir",
        type=Path,
        default=DEFAULT_FONT_DIR,
        help=f"字体目录（默认: {DEFAULT_FONT_DIR.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--exclude-file",
        type=Path,
        default=DEFAULT_EXCLUDE_FILE,
        help="要移除的 Unicode 码位列表（十六进制，每行一个）",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="不将原文件复制为同名的 .bak（默认会备份）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只报告将移除的字形，不写文件",
    )
    args = parser.parse_args()

    font_dir = args.dir.resolve()
    if not font_dir.is_dir():
        print(f"目录不存在: {font_dir}", file=sys.stderr)
        return 1

    excluded = load_excluded_unicodes(args.exclude_file.resolve())
    fonts = iter_font_files(font_dir)
    if not fonts:
        print(f"在 {font_dir} 中未找到字体文件（{', '.join(FONT_SUFFIXES)}）", file=sys.stderr)
        return 1

    print(f"目录: {font_dir}")
    print(f"排除 {len(excluded)} 个码位: {', '.join(f'U+{cp:04X}' for cp in sorted(excluded))}")
    print(f"待处理 {len(fonts)} 个文件")

    if args.dry_run:
        Options, Subsetter, TTFont = _import_fonttools()
        for path in fonts:
            font = TTFont(path, lazy=True)
            removed = collect_unicodes(font) & excluded
            if removed:
                print(
                    f"  [dry-run] {path.name}: 将移除 "
                    f"{', '.join(f'U+{cp:04X}' for cp in sorted(removed))}"
                )
            else:
                print(f"  [dry-run] {path.name}: 无冲突字形")
        return 0

    Options, Subsetter, TTFont = _import_fonttools()
    total_removed = 0
    for path in fonts:
        if not args.no_backup:
            backup = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup)
            print(f"  已备份: {backup.name}")

        tmp = path.with_suffix(path.suffix + ".tmp")
        try:
            removed, _ = subset_font(
                path,
                tmp,
                excluded,
                Options=Options,
                Subsetter=Subsetter,
                TTFont=TTFont,
            )
            total_removed += removed
            if removed:
                tmp.replace(path)
            else:
                tmp.unlink(missing_ok=True)
        except Exception:
            tmp.unlink(missing_ok=True)
            raise

    print(f"完成，共移除 {total_removed} 个字形实例。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
