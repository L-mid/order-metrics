from __future__ import annotations

from typing import Any, Sequence


def render_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    """
    ## Print query results.
    Computes the width of each column, 
    then prints every row using that width.
    - Columns line up.
    - A header + separator
    - In place string conversion.

    """
    # convert everything to strings
    srows = [[("" if v is None else str(v)) for v in r] for r in rows]
    widths = [len(h) for h in headers]      # start each col width as at least the header width.
    for r in srows:
        for i, cell in enumerate(r):
            widths[i] = max(widths[i], len(cell))

    def fmt_row(cols: Sequence[str]) -> str:
        return " | ".join(c.ljust(widths[i]) for i, c in enumerate(cols))

    # compose the final output as lines.
    line = "-+-".join("-" * w for w in widths)      # separator! (between header and rows)
    out = [fmt_row(headers), line]
    out += [fmt_row(r) for r in srows]
    return "\n".join(out)

