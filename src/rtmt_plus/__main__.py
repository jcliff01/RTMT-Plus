"""Allows `python -m rtmt_plus`, which works even when the rtmt-plus command isn't on the PATH."""
from .cli import main

raise SystemExit(main())
