"""Small, dependency-free utilities shared by the four portfolio projects."""
import csv
import html
import json
import sqlite3
from pathlib import Path


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError('Cannot infer CSV schema from empty rows')
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def database(path, tables):
    """Build a fresh local SQLite warehouse; table identifiers are code-owned."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    for name, rows in tables.items():
        types = {k: 'INTEGER' if isinstance(v, int) else 'REAL' if isinstance(v, float) else 'TEXT'
                 for k, v in rows[0].items()}
        db.execute('CREATE TABLE ' + name + ' (' + ','.join(f'"{k}" {v}' for k, v in types.items()) + ')')
        db.executemany('INSERT INTO ' + name + ' VALUES (' + ','.join('?' for _ in types) + ')',
                       [tuple(row.values()) for row in rows])
    db.commit()
    return db


def query(db, sql):
    return [dict(row) for row in db.execute(sql)]


def export_query(db, sql_path, destination):
    rows = query(db, Path(sql_path).read_text())
    write_csv(destination, rows)
    return rows


def report(root, title, metrics, tables, findings, caveat):
    """Export a self-contained offline BI report with filterable chart and table.

    Tables carry pre-computed metrics at their declared grain. Filtering selects
    rows; it deliberately does not average ratios or recompute a causal estimate.
    """
    root = Path(root)
    out = root / 'outputs'
    out.mkdir(exist_ok=True)
    payload = dict(title=title, metrics=metrics, tables=tables, findings=findings, caveat=caveat)
    (out / 'results.json').write_text(json.dumps(payload, indent=2, allow_nan=False))
    template = (Path(__file__).parent / 'dashboard-template.html').read_text()
    encoded = json.dumps(payload, allow_nan=False).replace('<', '\\u003c')
    (out / 'dashboard.html').write_text(template.replace('__DATA__', encoded))
    lines = ['# ' + title, '', '> Independent, AI-assisted portfolio study. All data are synthetic.', '',
             '## Decision brief', '', *['- ' + s for s in findings], '', '## Results', '']
    lines += ['| Metric | Value |', '|---|---|']
    lines += [f'| {k} | {v} |' for k, v in metrics.items()]
    lines += ['', '## Interpretation limits', '', caveat, '', '## Review with Growth Marketing', '',
              'Confirm the decision, measurement window, constraints, and alternative explanations before acting. '
              'Document feedback and rerun the analysis when assumptions change.', '',
              'Open `dashboard.html` locally for interactive charts and tables. `results.json` is the exact report input.']
    (out / 'decision-brief.md').write_text('\n'.join(lines) + '\n')
    # A GitHub-renderable, exact SVG preview: no generated imagery.
    labels = list(metrics.items())[:4]
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="300" viewBox="0 0 1100 300">',
           '<rect width="1100" height="300" fill="#101d2c"/>',
           '<text x="35" y="48" fill="#6fe5bc" font-family="Arial" font-size="14">GROWTH ANALYTICS / SYNTHETIC PORTFOLIO STUDY</text>',
           f'<text x="35" y="90" fill="white" font-family="Arial" font-size="26">{html.escape(title)}</text>']
    for i, (key, value) in enumerate(labels):
        x = 35 + i * 265
        svg += [f'<text x="{x}" y="165" fill="#b8c8da" font-family="Arial" font-size="14">{html.escape(key)}</text>',
                f'<text x="{x}" y="209" fill="white" font-family="Arial" font-size="29">{html.escape(str(value))}</text>']
    svg += ['<text x="35" y="270" fill="#b8c8da" font-family="Arial" font-size="13">Reproducible SQL + Python • Open the HTML dashboard for charts, filters, and evidence.</text>', '</svg>']
    (out / 'preview.svg').write_text('\n'.join(svg))


def table(name, rows, category, value, unit=''):
    return dict(name=name, rows=rows, category=category, value=value, unit=unit)
