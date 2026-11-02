# ID generator for .md files

The script creates an empty `.md` file in the specified folder. The file name
is a generated ID like `ABC-1234`: letters, a dash, digits. The number of
letters and digits is configurable (3 letters and 4 digits by default).

## Usage

```
python generate_id.py
```

Requires only Python 3, no third-party libraries.
`config.json` must be located in the same folder as the script.

## Settings (config.json)

```json
{
  "output_dir": "C:/Users/Name/Documents/notes",
  "letters_mode": "list",
  "letters": ["A", "B", "C", "D", "E", "F"],
  "fixed_letters": "ABC",
  "strategy": "sequential",
  "letters_count": 3,
  "digits_count": 4
}
```

| Option | Values | Description |
|---|---|---|
| `output_dir` | path | Folder where files are created. An absolute path is recommended (see below). The folder is created automatically if it doesn't exist. |
| `letters_mode` | `"list"` / `"fixed"` | Where the letters come from (see below). Default: `"list"`. |
| `letters` | list of letters | Letters used in `list` mode. Case-insensitive, duplicates are removed. |
| `fixed_letters` | string | Your own string used in `fixed` mode. Its length must equal `letters_count`. |
| `strategy` | `"sequential"` / `"random"` | Generation order: in sequence or random. Default: `"random"`. |
| `letters_count` | integer, 1 or more | Number of letters in the ID. Default: 3. |
| `digits_count` | integer, 1 or more | Number of digits in the ID. Default: 4. |

## Folder path (`output_dir`)

The folder can be anywhere on your computer. Use an absolute path:

- Windows: `"C:/Users/Name/Documents/notes"`. Forward slashes work on Windows and are safe in JSON.
  If you prefer backslashes, they must be doubled: `"C:\\Users\\Name\\Documents\\notes"`.
  A single `\` is invalid in JSON; the script will show an error with a hint in that case.
- macOS / Linux: `"/home/name/notes"` or `"/Users/name/notes"`.
- `~` and environment variables are supported: `"~/notes"`, `"%USERPROFILE%/notes"` (Windows), `"$HOME/notes"` (macOS/Linux).
- A relative path (for example, `"notes"`) also works, but it is resolved from the script's folder, not from the terminal's current directory.

## Letter modes (`letters_mode`)

**`"list"`**: letters are taken from the `letters` list. The result depends on `strategy`:

- `random`: random letters from the list and random digits, for example `DBA-5071`.
- `sequential`: enumerates in the order of the list: `AAA-0000`, `AAA-0001`, ... `AAA-9999`,
  then `AAB-0000`, and so on. The letter order is the order in the list.

**`"fixed"`**: the letters are always the same, taken from `fixed_letters`
(English letters only, case-insensitive, converted to upper case;
the length must match `letters_count`). Only the number changes:

- `random`: random digits, for example `ABC-3829`.
- `sequential`: `ABC-0000`, `ABC-0001`, `ABC-0002`, ... The next number is the maximum
  among existing files with these letters, plus 1.

## Number of letters and digits

- `letters_count: 2`, `digits_count: 3` gives IDs like `AB-042`.
- `letters_count: 4`, `digits_count: 6` gives IDs like `ABCD-000123`.
- The number is always left-padded with zeros to `digits_count` digits.
- If you change these values in a folder that already contains files, old files with a different
  ID length are ignored (the script treats them as regular files, not IDs).

## How "sequential" works

There is no separate counter file. The script looks at the `.md` files in `output_dir`
and takes the ID that follows the largest one found. This means:

- if you delete the latest file, its ID will be issued again;
- files whose names don't match the ID format are ignored;
- with the `random` strategy the script guarantees that the file doesn't already exist.

## Examples

Random letters from your own list, random digits:
```json
{
  "output_dir": "D:/Work/notes",
  "letters_mode": "list",
  "letters": ["X", "Y", "Z"],
  "strategy": "random",
  "letters_count": 3,
  "digits_count": 4
}
```

Always `DOC`, sequential numbers with 5 digits:
```json
{
  "output_dir": "/home/name/notes",
  "letters_mode": "fixed",
  "fixed_letters": "DOC",
  "strategy": "sequential",
  "letters_count": 3,
  "digits_count": 5
}
```

## Errors

The script stops with a clear message if:

- `config.json` is missing or has a syntax error (for example, single `\` in a path);
- `output_dir` is not specified;
- `strategy` or `letters_mode` has an unknown value;
- `letters_count` or `digits_count` is not an integer or is less than 1;
- in `list` mode, the `letters` list is empty;
- in `fixed` mode, the length or characters of `fixed_letters` don't match `letters_count`;
- all possible IDs have been used up.