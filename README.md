## Installation: Windows powershell
```bash
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"

# Set the DB connection and run
$env:DATABASE_URL="postgres://<user>:<pass>@localhost:5432/<db>"

# (optional) additionally test cli works and tests
order-metrics all
pytest -q


## if order-metrics 'command isn't found':

# run via module `python -m` (always works)
python -m order_metrics.cli all

# Or re-open the shell after install and confirm 
# (sometimes PATH refresh issues on Windows):
python -m pip show order-metrics
```

# Order metrics
Display tables of SQL queries on seeded data. 


# Usage:

Run `order-metrics` alongside whichever catagory you'd like to display in the termial.

## Example command:
  - `order-metrics top-products`:

And the resulting query will display in termial like:

![alt text](assets/top-products.png)


Full supported options are: 
- `monthly`, 
- `country`, 
- and `top-products`.

### To see all avalible tables at once, use `all`: 
- `order-metrics all`

And every result will display in the termial at once!


![alt text](assets/all.png)

