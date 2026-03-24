"""CLI entry point for govai using Typer."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from govai.classifier import classify_inventory, parse_input_file
from govai.models import ConfidenceSource, RiskTier
from govai.reporter import write_reports

app = typer.Typer(
    name="govai",
    help="EU AI Act compliance inventory from a software list.",
    add_completion=False,
)

console = Console()


@app.callback()
def callback() -> None:
    """govai — EU AI Act compliance inventory from a software list."""


@app.command()
def scan(
    input: Path = typer.Argument(
        ...,
        help="CSV or plain text file of tools to classify.",
        exists=False,  # We handle validation ourselves for better messages
    ),
    output_dir: Path = typer.Option(
        Path("."),
        "--output-dir",
        "-o",
        help="Directory to write reports (default: current directory).",
    ),
    format: str = typer.Option(
        "all",
        "--format",
        "-f",
        help=(
            "Output format: markdown | json | html | both | all. "
            "'both' = markdown + json (default). "
            "'all' = markdown + json + html. "
            "The HTML report is suitable for sharing with legal or "
            "compliance teams."
        ),
    ),
    llm_model: str = typer.Option(
        "claude-sonnet-4-6",
        "--llm-model",
        "-m",
        help=(
            "LiteLLM model string for fallback classification. "
            "Run `govai models` to see all options with setup instructions. "
            "Examples: gpt-4o, ollama/llama3.2, mistral/mistral-large-latest, "
            "deepseek/deepseek-chat, ollama/qwen2.5. "
            "Default: claude-sonnet-4-6"
        ),
    ),
    no_llm: bool = typer.Option(
        False,
        "--no-llm",
        help="Skip LLM fallback. Unknown tools marked UNCLEAR.",
    ),
) -> None:
    """Scan a list of software tools and classify them under EU AI Act risk tiers."""

    # Validate input file exists
    if not input.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input}")
        raise typer.Exit(code=1)

    # Validate format
    valid_formats = ("markdown", "json", "html", "both", "all")
    if format not in valid_formats:
        console.print(
            f"[red]Error:[/red] Invalid format '{format}'. "
            f"Must be one of: {', '.join(valid_formats)}"
        )
        raise typer.Exit(code=1)

    # Parse input file
    try:
        tools = parse_input_file(input)
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)

    if not tools:
        console.print("[yellow]Warning:[/yellow] No tools found in input file.")
        raise typer.Exit(code=0)

    console.print(
        f"\n[bold]govai[/bold] — Classifying {len(tools)} tool(s)...\n"
    )

    # Classify
    report = classify_inventory(
        tools=tools,
        model=llm_model,
        no_llm=no_llm,
        input_file=str(input),
    )

    # Write reports
    written = write_reports(report, output_dir, format)

    # Summary table
    table = Table(title="Classification Summary")
    table.add_column("Tool", style="cyan")
    table.add_column("Risk Tier", style="bold")
    table.add_column("Confidence", style="dim")

    for result in report.results:
        tier_style = {
            RiskTier.UNACCEPTABLE: "red bold",
            RiskTier.HIGH: "red",
            RiskTier.LIMITED: "yellow",
            RiskTier.MINIMAL: "green",
            RiskTier.UNCLEAR: "dim",
        }.get(result.risk_tier, "")

        table.add_row(
            result.tool_name,
            f"[{tier_style}]{result.risk_tier.value}[/{tier_style}]",
            result.confidence_source.value,
        )

    console.print(table)

    # Footer stats
    registry_count = sum(
        1 for r in report.results
        if r.confidence_source == ConfidenceSource.REGISTRY_MATCH
    )
    inferred_count = sum(
        1 for r in report.results
        if r.confidence_source == ConfidenceSource.INFERRED
    )
    unclear_count = sum(
        1 for r in report.results if r.risk_tier == RiskTier.UNCLEAR
    )

    console.print(
        f"\n{registry_count} registry matches, "
        f"{inferred_count} inferred, "
        f"{unclear_count} UNCLEAR"
    )
    console.print(
        f"Reports written to: {', '.join(str(p) for p in written)}"
    )
    console.print(
        "Tip: run `govai models` to see all supported LLM options.\n"
    )


@app.command()
def models() -> None:
    """Show all supported LLM model strings with setup instructions."""
    table = Table(
        title="Supported LLM Models",
        show_lines=False,
        pad_edge=True,
    )
    table.add_column("Model String", style="cyan", no_wrap=True)
    table.add_column("Provider", style="bold")
    table.add_column("API Key Env Var", style="dim")
    table.add_column("Notes")

    # --- CLOUD — PROPRIETARY ---
    table.add_row(
        "[bold underline]CLOUD — PROPRIETARY[/bold underline]",
        "", "", "", style="dim",
    )
    table.add_row(
        "claude-sonnet-4-6", "Anthropic",
        "ANTHROPIC_API_KEY", "Default. Best accuracy.",
    )
    table.add_row(
        "claude-opus-4-6", "Anthropic",
        "ANTHROPIC_API_KEY", "Slower, highest accuracy.",
    )
    table.add_row(
        "gpt-4o", "OpenAI",
        "OPENAI_API_KEY", "Strong alternative.",
    )
    table.add_row(
        "gpt-4o-mini", "OpenAI",
        "OPENAI_API_KEY", "Faster, lower cost.",
    )
    table.add_row(
        "gemini/gemini-2.0-flash", "Google",
        "GEMINI_API_KEY", "Fast. EU data options.",
    )

    # --- EU-BASED PROVIDERS ---
    table.add_row(
        "[bold underline]EU-BASED PROVIDERS[/bold underline]",
        "", "", "", style="dim",
    )
    table.add_row(
        "mistral/mistral-large-latest", "Mistral AI",
        "MISTRAL_API_KEY", "French company, EU data residency.",
    )
    table.add_row(
        "mistral/mistral-small-latest", "Mistral AI",
        "MISTRAL_API_KEY", "Faster, lower cost.",
    )

    # --- OTHER CLOUD ---
    table.add_row(
        "[bold underline]OTHER CLOUD[/bold underline]",
        "", "", "", style="dim",
    )
    table.add_row(
        "deepseek/deepseek-chat", "DeepSeek",
        "DEEPSEEK_API_KEY", "Strong reasoning, very low cost.",
    )
    table.add_row(
        "groq/llama-3.3-70b-versatile", "Groq",
        "GROQ_API_KEY", "Very fast inference.",
    )
    table.add_row(
        "cohere/command-r-plus", "Cohere",
        "COHERE_API_KEY", "Strong structured outputs.",
    )

    # --- LOCAL VIA OLLAMA ---
    table.add_row(
        "[bold underline]LOCAL VIA OLLAMA (no data leaves machine)[/bold underline]",
        "", "", "", style="dim",
    )
    table.add_row("ollama/llama3.2", "Ollama", "None", "ollama pull llama3.2")
    table.add_row("ollama/qwen2.5", "Ollama", "None", "ollama pull qwen2.5")
    table.add_row("ollama/qwen3", "Ollama", "None", "ollama pull qwen3")
    table.add_row("ollama/deepseek-r1", "Ollama", "None", "ollama pull deepseek-r1")
    table.add_row("ollama/mistral", "Ollama", "None", "ollama pull mistral")
    table.add_row("ollama/phi4", "Ollama", "None", "ollama pull phi4")

    console.print(table)
    console.print()
    console.print("Usage:  govai scan tools.csv --llm-model <model-string>")
    console.print(
        "Any other LiteLLM model: docs.litellm.ai/docs/providers"
    )
    console.print()
    console.print(
        "Local models (ollama/*) keep all data on your machine."
    )
    console.print(
        "Cloud models produce more accurate EU AI Act classifications."
    )
    console.print("Install Ollama from: ollama.com")
