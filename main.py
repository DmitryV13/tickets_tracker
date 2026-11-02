import json
import os
import random
import re
import sys
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"


@dataclass
class Config:
    letters: list
    letters_mode: str
    fixed_letters: str
    strategy: str
    letters_count: int
    digits_count: int
    out_dir: Path

    @property
    def max_num(self):
        return 10 ** self.digits_count - 1

    def fmt(self, prefix, num):
        return f"{prefix}-{num:0{self.digits_count}d}"


def load_config():
    try:
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"Config file not found: {CONFIG_PATH}")
    except json.JSONDecodeError as e:
        sys.exit(
            f"Error in config.json: {e}\n"
            'Hint: in Windows paths use C:/Users/Name/notes or C:\\\\Users\\\\Name\\\\notes '
            "(a single backslash is not valid in JSON)."
        )

    try:
        letters_count = int(raw.get("letters_count", 3))
        digits_count = int(raw.get("digits_count", 4))
    except (TypeError, ValueError):
        sys.exit("letters_count and digits_count must be integers.")
    if letters_count < 1 or digits_count < 1:
        sys.exit("letters_count and digits_count must be at least 1.")

    if "output_dir" not in raw:
        sys.exit("output_dir is not set in config.json.")
    out_dir = Path(os.path.expandvars(os.path.expanduser(str(raw["output_dir"]))))
    if not out_dir.is_absolute():
        out_dir = BASE_DIR / out_dir  # a relative path is resolved from the script's folder

    cfg = Config(
        letters=list(dict.fromkeys(str(c).upper() for c in raw.get("letters", []))),
        letters_mode=str(raw.get("letters_mode", "list")).lower(),
        fixed_letters=str(raw.get("fixed_letters", "")).upper(),
        strategy=str(raw.get("strategy", "random")).lower(),
        letters_count=letters_count,
        digits_count=digits_count,
        out_dir=out_dir,
    )

    if cfg.strategy not in ("sequential", "random"):
        sys.exit('strategy must be "sequential" or "random".')
    if cfg.letters_mode not in ("list", "fixed"):
        sys.exit('letters_mode must be "list" or "fixed".')
    return cfg


def existing_ids(cfg):
    """Return a list of (letters, number) for IDs already present in the folder."""
    rx = re.compile(rf"^([A-Z]{{{cfg.letters_count}}})-(\d{{{cfg.digits_count}}})$")
    result = []
    for f in cfg.out_dir.glob("*.md"):
        m = rx.match(f.stem)
        if m:
            result.append((m.group(1), int(m.group(2))))
    return result


def fixed_id(cfg):
    prefix = cfg.fixed_letters
    if not re.fullmatch(rf"[A-Z]{{{cfg.letters_count}}}", prefix):
        sys.exit(
            f"fixed_letters must consist of exactly {cfg.letters_count} "
            f'English letters (got: "{cfg.fixed_letters}").'
        )

    used = {n for p, n in existing_ids(cfg) if p == prefix}
    if len(used) > cfg.max_num:
        sys.exit(f"All numbers for {prefix} are used up.")

    if cfg.strategy == "sequential":
        num = max(used) + 1 if used else 0
        if num > cfg.max_num:
            sys.exit(f"All numbers for {prefix} are used up.")
    else:
        num = random.randint(0, cfg.max_num)
        while num in used:
            num = random.randint(0, cfg.max_num)
    return cfg.fmt(prefix, num)


def list_random_id(cfg):
    taken = set(existing_ids(cfg))
    space = len(cfg.letters) ** cfg.letters_count * (cfg.max_num + 1)
    if len(taken) >= space:
        sys.exit("All possible IDs are used up.")
    while True:
        prefix = "".join(random.choice(cfg.letters) for _ in range(cfg.letters_count))
        num = random.randint(0, cfg.max_num)
        if (prefix, num) not in taken:
            return cfg.fmt(prefix, num)


def list_sequential_id(cfg):
    letters, n, L = cfg.letters, len(cfg.letters), cfg.letters_count
    pos = {c: i for i, c in enumerate(letters)}
    step = cfg.max_num + 1

    # find the highest existing ID and take the next one
    last = -1
    for prefix, num in existing_ids(cfg):
        if all(ch in pos for ch in prefix):
            value = 0
            for ch in prefix:
                value = value * n + pos[ch]
            last = max(last, value * step + num)

    idx = last + 1
    num, combo = idx % step, idx // step
    if combo >= n ** L:
        sys.exit("All possible IDs are used up.")
    chars = []
    for _ in range(L):
        combo, r = divmod(combo, n)
        chars.append(letters[r])
    return cfg.fmt("".join(reversed(chars)), num)


def main():
    cfg = load_config()
    cfg.out_dir.mkdir(parents=True, exist_ok=True)

    if cfg.letters_mode == "fixed":
        new_id = fixed_id(cfg)
    else:
        if not cfg.letters:
            sys.exit("The letters list in config.json is empty.")
        new_id = list_sequential_id(cfg) if cfg.strategy == "sequential" else list_random_id(cfg)

    path = cfg.out_dir / f"{new_id}.md"
    path.touch()
    print(f"Created file: {path}")


if __name__ == "__main__":
    main()