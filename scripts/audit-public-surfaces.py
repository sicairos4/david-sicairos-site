import asyncio
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('responsive_audit', Path(__file__).with_name('audit-responsive.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
audit.PAGES = list(dict.fromkeys(audit.PAGES + ['library.html', 'intelligence/index.html']))
audit.THEMES = list(dict.fromkeys(audit.THEMES + ['civic-gold']))
raise SystemExit(asyncio.run(audit.main()))
