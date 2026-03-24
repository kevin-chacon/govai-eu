"""CLI entry point for govai using Typer."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from govai.classifier import classify_inventory, parse_input_file
from govai.models import ConfidenceSource, RiskTier
from govai import __version__
from govai.reporter import write_reports

_HELP_EPILOG = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 API KEY SETUP — How to connect your LLM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 govai uses a language model to classify tools not
 found in its registry. You need an API key from
 your chosen provider.

 STEP 1 — Get an API key from your provider:
   Anthropic (Claude):  console.anthropic.com
   OpenAI (GPT-4o):     platform.openai.com
   Mistral AI:          console.mistral.ai
   Google (Gemini):     aistudio.google.com
   DeepSeek:            platform.deepseek.com

 STEP 2 — Set it as an environment variable:

   On Mac or Linux — run this in your terminal:
     export ANTHROPIC_API_KEY="your-key-here"

   On Windows — run this in Command Prompt:
     set ANTHROPIC_API_KEY=your-key-here

   On Windows PowerShell:
     $env:ANTHROPIC_API_KEY="your-key-here"

 STEP 3 — Run govai scan normally:
   govai scan tools.csv

 To make it permanent (so you don't have to set it
 again each time):

   On Mac/Linux — add the export line to ~/.zshrc
                  or ~/.bashrc
   On Windows   — set it via System Properties >
                  Environment Variables (search
                  "environment variables" in the
                  Start menu)

 NO API KEY? Use a local model instead — completely
 free, no account needed, no data leaves your machine:

   1. Install Ollama from: ollama.com
   2. Run in terminal: ollama pull llama3.2
   3. Run govai:
      govai scan tools.csv --llm-model ollama/llama3.2

 Run `govai models` to see all supported models.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

app = typer.Typer(
    name="govai",
    help="EU AI Act compliance inventory from a software list.",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"govai-eu {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """govai — EU AI Act compliance inventory from a software list."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        console.print(_HELP_EPILOG)


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

    # API key warning
    key_issues = [
        r for r in report.results
        if r.risk_tier == RiskTier.UNCLEAR
        and r.notes
        and ("API key not found" in r.notes or "API key invalid" in r.notes)
    ]
    if key_issues:
        warning_text = (
            f"[bold]{len(key_issues)} tool(s)[/bold] could not be classified "
            f"because the API key for [cyan]{llm_model}[/cyan] was not found.\n\n"
            f"These tools are marked UNCLEAR in the report.\n"
            f"Run [bold]govai --help[/bold] for instructions on setting up "
            f"your API key, or switch to a local model:\n\n"
            f"  [cyan]govai scan tools.csv --llm-model ollama/llama3.2[/cyan]\n\n"
            f"No API key or installation required for local models."
        )
        console.print()
        console.print(Panel(
            warning_text,
            title="⚠  API Key Warning",
            border_style="yellow",
            padding=(1, 2),
        ))

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

    # --- API key setup guide ---
    console.print()
    console.print(Panel(
        (
            "[bold]STEP 1[/bold] — Get a key from your chosen provider:\n"
            "\n"
            "  Anthropic (Claude)  →  console.anthropic.com\n"
            "  OpenAI (GPT-4o)     →  platform.openai.com\n"
            "  Mistral AI          →  console.mistral.ai\n"
            "  Google (Gemini)     →  aistudio.google.com\n"
            "  DeepSeek            →  platform.deepseek.com\n"
            "  Groq                →  console.groq.com\n"
            "\n"
            "[bold]STEP 2[/bold] — Set it as an environment variable:\n"
            "\n"
            "  Mac / Linux — run in your terminal:\n"
            '    export ANTHROPIC_API_KEY="your-key-here"\n'
            "\n"
            "  Windows Command Prompt:\n"
            "    set ANTHROPIC_API_KEY=your-key-here\n"
            "\n"
            "  Windows PowerShell:\n"
            '    $env:ANTHROPIC_API_KEY="your-key-here"\n'
            "\n"
            "[bold]STEP 3[/bold] — Run govai scan normally:\n"
            "    govai scan tools.csv\n"
            "\n"
            "  govai picks up the key automatically — you do not\n"
            "  need to include it in the command."
        ),
        title="HOW TO SET UP YOUR API KEY",
        border_style="cyan",
        padding=(1, 2),
    ))

    console.print(Panel(
        (
            "  Mac / Linux:\n"
            "    Add the export line to ~/.zshrc or ~/.bashrc\n"
            "    Then run: source ~/.zshrc\n"
            "\n"
            "  Windows:\n"
            '    Search "environment variables" in the Start menu\n'
            '    Open "Edit the system environment variables"\n'
            '    Click "Environment Variables"\n'
            '    Under "User variables" click New\n'
            "    Variable name:  ANTHROPIC_API_KEY\n"
            "    Variable value: your-key-here"
        ),
        title="TO MAKE IT PERMANENT",
        subtitle="so you never have to set it again",
        border_style="dim",
        padding=(1, 2),
    ))

    console.print(Panel(
        (
            "  Local models run entirely on your machine.\n"
            "  No account, no key, no data sent anywhere.\n"
            "\n"
            "  1. Install Ollama from: ollama.com\n"
            "  2. Pull a model — run in your terminal:\n"
            "       ollama pull llama3.2\n"
            "  3. Run govai:\n"
            "       govai scan tools.csv --llm-model ollama/llama3.2\n"
            "\n"
            "  Other local models: ollama pull qwen2.5\n"
            "                      ollama pull deepseek-r1\n"
            "                      ollama pull mistral"
        ),
        title="NO API KEY? USE A LOCAL MODEL INSTEAD",
        border_style="green",
        padding=(1, 2),
    ))

