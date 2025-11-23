"""
Command-Line Interface for Data Quality Framework
"""

from pathlib import Path

import click
import pandas as pd

from dqf import DQFramework


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Data Quality Framework CLI"""


@main.command()
@click.argument("data_file", type=click.Path(exists=True))
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file")
@click.option("--output", "-o", default="report.html", help="Output report file")
@click.option("--format", "-f", type=click.Choice(["html", "json", "pdf"]), default="html", help="Report format")
def profile(data_file, config, output, format):
    """Profile a dataset and generate a report"""
    click.echo(f"Profiling {data_file}...")

    # Load data
    if data_file.endswith(".csv"):
        df = pd.read_csv(data_file)
    elif data_file.endswith(".parquet"):
        df = pd.read_parquet(data_file)
    else:
        click.echo("Unsupported file format", err=True)
        return

    # Initialize framework
    if config:
        dqf = DQFramework.from_config(config)
    else:
        dqf = DQFramework()

    # Run profiling
    results = dqf.run_quality_check(
        df=df,
        dataset=Path(data_file).stem,
        profile=True,
        validate=False,
        monitor=False,
    )

    # Generate report
    dqf.generate_report(results, output, format=format)

    click.echo(f"✅ Report generated: {output}")


@main.command()
@click.argument("data_file", type=click.Path(exists=True))
@click.option("--config", "-c", type=click.Path(exists=True), required=True, help="Configuration file")
@click.option("--fail-fast", is_flag=True, help="Stop on first validation failure")
def validate(data_file, config, fail_fast):
    """Validate a dataset against rules"""
    click.echo(f"Validating {data_file}...")

    # Load data
    if data_file.endswith(".csv"):
        df = pd.read_csv(data_file)
    elif data_file.endswith(".parquet"):
        df = pd.read_parquet(data_file)
    else:
        click.echo("Unsupported file format", err=True)
        return

    # Initialize framework
    dqf = DQFramework.from_config(config)
    dqf.validator.fail_fast = fail_fast

    # Run validation
    results = dqf.run_quality_check(
        df=df,
        dataset=Path(data_file).stem,
        profile=False,
        validate=True,
        monitor=False,
    )

    validation_result = results.get("validation")

    if validation_result:
        click.echo(validation_result.summary())

        if validation_result.is_valid:
            click.echo("✅ All validations passed!")
        else:
            click.echo(f"❌ {validation_result.failed_rules} validation(s) failed")
            exit(1)


@main.command()
@click.argument("data_file", type=click.Path(exists=True))
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file")
@click.option("--output", "-o", default="quality_report.html", help="Output report file")
def check(data_file, config, output):
    """Run complete quality check (profile + validate + monitor)"""
    click.echo(f"Running quality check on {data_file}...")

    # Load data
    if data_file.endswith(".csv"):
        df = pd.read_csv(data_file)
    elif data_file.endswith(".parquet"):
        df = pd.read_parquet(data_file)
    else:
        click.echo("Unsupported file format", err=True)
        return

    # Initialize framework
    if config:
        dqf = DQFramework.from_config(config)
    else:
        dqf = DQFramework()

    # Run complete check
    results = dqf.run_quality_check(
        df=df,
        dataset=Path(data_file).stem,
        profile=True,
        validate=True,
        monitor=True,
    )

    # Display results
    if results.get("profile"):
        click.echo("\n" + results["profile"].summary())

    if results.get("validation"):
        click.echo("\n" + results["validation"].summary())

    if results.get("metrics"):
        metrics = results["metrics"]
        click.echo(f"\n📊 Quality Score: {metrics.quality_score:.2%}")
        click.echo(f"   Completeness: {metrics.completeness:.2%}")
        click.echo(f"   Validity: {metrics.validity:.2%}")
        click.echo(f"   Uniqueness: {metrics.uniqueness:.2%}")

    # Generate report
    dqf.generate_report(results, output)
    click.echo(f"\n✅ Report generated: {output}")


if __name__ == "__main__":
    main()
