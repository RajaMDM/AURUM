"""
AURUM CLI — shellable interface to the pipeline.

Run from the repo root:

    python -m runtimes.cli --help
    python -m runtimes.cli assay shared/sample_data/output/customers_dirty.csv
    python -m runtimes.cli unearth customer shared/sample_data/output/customers_dirty.csv
    python -m runtimes.cli anomaly shared/sample_data/output/customers_dirty.csv
    python -m runtimes.cli demo

The CLI is a thin adapter — every command calls into the same modules
the demo and MCP server use, so behaviour stays consistent across
runtimes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

# Make repo root importable when invoked as `python -m runtimes.cli`
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from assay.schema_inspector.inspector import SchemaInspector
from unearth.profiler.domain_profiler import (
    AssetProfiler,
    CounterpartyProfiler,
    CustomerProfiler,
    EmployeeProfiler,
    LocationProfiler,
    ProductProfiler,
    VendorProfiler,
)

console = Console()

VERSION = "0.1.3"

PROFILERS = {
    "customer":     CustomerProfiler,
    "product":      ProductProfiler,
    "vendor":       VendorProfiler,
    "asset":        AssetProfiler,
    "location":     LocationProfiler,
    "employee":     EmployeeProfiler,
    "counterparty": CounterpartyProfiler,
}


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(VERSION, prog_name="aurum")
def cli() -> None:
    """AURUM — Raw data in. Hallmarked golden records out.

    Five-stage MDM pipeline (ASSAY → UNEARTH → REFINE → UNFURL → MARK).
    """


@cli.command()
@click.argument("csv_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--source-name", default="cli_source", help="Logical source-system name to record on the assay.")
@click.option("--json-out", "json_out", is_flag=True, help="Emit raw JSON instead of formatted output.")
def assay(csv_path: Path, source_name: str, json_out: bool) -> None:
    """ASSAY — inspect a CSV: types, nulls, cardinality, samples."""
    inspector = SchemaInspector(source_name=source_name)
    schema = inspector.inspect(str(csv_path))

    if json_out:
        click.echo(json.dumps(schema, indent=2, default=str))
        return

    console.rule("[bold]ASSAY")
    console.print(f"Source:       [cyan]{schema['source']}[/cyan]")
    console.print(f"Rows:         [cyan]{schema['row_count']}[/cyan]")
    console.print(f"Fields:       [cyan]{schema['field_count']}[/cyan]")
    console.print(f"High-null:    {schema['high_null_fields']}")
    console.print(f"Low-card:     {schema['low_cardinality_fields']}")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Field")
    table.add_column("Type")
    table.add_column("Null %", justify="right")
    table.add_column("Cardinality", justify="right")
    table.add_column("Samples")
    for f in schema["fields"]:
        table.add_row(
            f["field"],
            f["inferred_type"],
            f"{f['null_pct']}%",
            str(f["cardinality"]),
            ", ".join(str(s) for s in f["samples"][:2]),
        )
    console.print(table)


@cli.command()
@click.argument("domain", type=click.Choice(sorted(PROFILERS.keys()), case_sensitive=False))
@click.argument("csv_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--json-out", "json_out", is_flag=True, help="Emit raw JSON instead of formatted output.")
@click.option("--show-issues", default=10, type=int, help="How many individual issues to print (0 for none).")
def unearth(domain: str, csv_path: Path, json_out: bool, show_issues: int) -> None:
    """UNEARTH — run the DQ profiler for one of the 7 domains."""
    profiler = PROFILERS[domain.lower()]()
    result = profiler.profile(str(csv_path))
    summary = result.summary()

    if json_out:
        out = {
            **summary,
            "issues": [
                {"row": i.row_index, "field": i.field, "rule": i.rule, "value": i.value, "severity": i.severity}
                for i in result.issues
            ],
        }
        click.echo(json.dumps(out, indent=2, default=str))
        return

    console.rule(f"[bold]UNEARTH — {domain}")
    console.print(f"Rows profiled:   [cyan]{summary['rows']}[/cyan]")
    console.print(f"DQ issues:       [cyan]{summary['issues']}[/cyan]")
    console.print(f"Quality score:   [bold green]{summary['quality_score_pct']}%[/bold green]")
    console.print(f"Issues by rule:  {summary['by_rule']}")

    if show_issues > 0 and result.issues:
        table = Table(show_header=True, header_style="bold")
        table.add_column("Row", justify="right")
        table.add_column("Field")
        table.add_column("Rule")
        table.add_column("Severity")
        table.add_column("Value")
        for issue in result.issues[:show_issues]:
            severity_color = "red" if issue.severity == "ERROR" else "yellow"
            table.add_row(
                str(issue.row_index),
                issue.field,
                issue.rule,
                f"[{severity_color}]{issue.severity}[/{severity_color}]",
                str(issue.value)[:30],
            )
        console.print(table)
        if len(result.issues) > show_issues:
            console.print(f"[dim]… {len(result.issues) - show_issues} more issues. Use --show-issues to see more.[/dim]")


@cli.command()
@click.argument("csv_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--domain", default="generic", help="Domain label for the result (cosmetic).")
@click.option("--contamination", default=0.1, type=float, help="Expected fraction of anomalous rows (0–0.5).")
@click.option("--json-out", "json_out", is_flag=True, help="Emit raw JSON instead of formatted output.")
@click.option("--show-flagged", default=5, type=int, help="How many flagged rows to print.")
def anomaly(csv_path: Path, domain: str, contamination: float, json_out: bool, show_flagged: int) -> None:
    """UNEARTH — run the Isolation Forest anomaly detector."""
    from unearth.anomaly import AnomalyDetector

    detector = AnomalyDetector(contamination=contamination)
    result = detector.detect(str(csv_path), domain=domain)
    summary = result.summary()

    if json_out:
        out = {
            **summary,
            "flagged": [f.to_dict() for f in result.flagged],
        }
        click.echo(json.dumps(out, indent=2, default=str))
        return

    console.rule(f"[bold]UNEARTH — anomaly ({domain})")
    console.print(f"Rows analysed:   [cyan]{summary['rows']}[/cyan]")
    console.print(f"Flagged rows:    [cyan]{summary['flagged']}[/cyan] ({summary['flagged_pct']}%)")
    console.print(f"Contamination:   {summary['contamination']}")
    console.print(f"Features used:   [cyan]{summary['feature_count']}[/cyan]")

    if show_flagged > 0 and result.flagged:
        table = Table(show_header=True, header_style="bold")
        table.add_column("Row", justify="right")
        table.add_column("Score", justify="right")
        table.add_column("Top driving features (z-score)")
        for f in result.flagged[:show_flagged]:
            features_str = ", ".join(f"{k}={v}" for k, v in f.feature_signal.items())
            table.add_row(str(f.row_index), f"{f.anomaly_score:.3f}", features_str)
        console.print(table)


@cli.command()
def demo() -> None:
    """Run the end-to-end pipeline demo (ASSAY → MARK)."""
    from demo.end_to_end_demo import main as run_demo
    run_demo()


@cli.command()
def domains() -> None:
    """List the 7 AURUM domains."""
    table = Table(show_header=True, header_style="bold")
    table.add_column("Domain")
    table.add_column("Profiler ready?")
    for name, cls in sorted(PROFILERS.items()):
        table.add_row(name, "[green]✓[/green]" if cls else "[red]✗[/red]")
    console.print(table)


if __name__ == "__main__":
    cli()
