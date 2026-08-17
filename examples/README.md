# Examples

Short, runnable scripts. Each one is a starting point to modify, not a finished
tool — the point is to change something and see what happens.

| Script | What it shows |
|---|---|
| `01_hello_sky.py` | Where the Sun and Moon are right now |
| `02_a_month_of_moonrise.py` | The Harvest Moon effect, in your own data |
| `03_check_a_published_value.py` | Validating against independent sources |

Run them from the repository root, with your venv active:

```bash
python examples/01_hello_sky.py
```

Scripts 01 and 02 use your saved location:

```bash
moonfield config set-location --lat 51.48 --lon 0.0 --name "Greenwich"
```

Remember longitude is **east-positive**.
