#!/usr/bin/env python3
import argparse
import asyncio
import importlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    parser = argparse.ArgumentParser(
        description="ProtonMail reader - fetch new emails via Playwright (Firefox)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Don't mark as read/processed")
    parser.add_argument(
        "--handler",
        type=str,
        default="",
        help="Module:func, e.g. examples.print_only:handle",
    )
    parser.add_argument("--max", type=int, default=None, help="Override MAX_PER_RUN")
    args = parser.parse_args()

    if args.max is not None:
        os.environ["MAX_PER_RUN"] = str(args.max)

    from protonmail_reader import ProtonFetcher

    fetcher = ProtonFetcher()

    handler = None
    if args.handler:
        try:
            mod_path, func_name = args.handler.split(":", 1)
            mod = importlib.import_module(mod_path)
            handler = getattr(mod, func_name)
        except Exception as e:
            print(f"[ERROR] Cannot import handler {args.handler}: {e}", file=sys.stderr)
            return 1

    emails = await fetcher.fetch_new(handler=handler, dry_run=args.dry_run)
    print(f"[INFO] Fetched {len(emails)} new email(s)")
    for i, e in enumerate(emails[:5], 1):
        print(f"  {i}. {e.conv_id} | {e.from_addr} | {e.subject[:60]}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        sys.exit(130)
