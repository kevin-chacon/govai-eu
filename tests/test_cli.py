"""Tests for govai CLI commands."""

from typer.testing import CliRunner

from govai.cli import app

runner = CliRunner()


class TestModelsCommand:
    """Test the govai models subcommand."""

    def test_models_command_runs(self):
        """Invoke 'govai models' exits 0 and shows default model."""
        result = runner.invoke(app, ["models"])
        assert result.exit_code == 0
        assert "claude-sonnet-4-6" in result.output

    def test_models_command_shows_ollama(self):
        """Models table includes Ollama models."""
        result = runner.invoke(app, ["models"])
        assert "ollama/llama3.2" in result.output

    def test_models_command_shows_eu_provider(self):
        """Models table includes EU-based provider (Mistral)."""
        result = runner.invoke(app, ["models"])
        assert "mistral" in result.output.lower()

    def test_models_command_shows_categories(self):
        """Models table shows all four category headers."""
        result = runner.invoke(app, ["models"])
        output = result.output
        assert "CLOUD" in output
        assert "EU-BASED PROVIDERS" in output
        assert "OLLAMA" in output

    def test_models_command_shows_usage_hint(self):
        """Usage hint appears after the table."""
        result = runner.invoke(app, ["models"])
        assert "govai scan tools.csv --llm-model" in result.output

    def test_models_shows_setup_guide(self):
        """Setup guide with provider URLs appears in output."""
        result = runner.invoke(app, ["models"])
        assert "STEP 1" in result.output
        assert "console.anthropic.com" in result.output

    def test_models_shows_windows_instructions(self):
        """Windows setup instructions appear in output."""
        result = runner.invoke(app, ["models"])
        assert "PowerShell" in result.output
        assert "set ANTHROPIC" in result.output

    def test_models_shows_ollama_no_key_section(self):
        """Ollama no-key alternative section appears in output."""
        result = runner.invoke(app, ["models"])
        assert "No account, no key" in result.output


class TestVersionFlag:
    """Test the --version flag."""

    def test_version_flag(self):
        """govai --version exits 0 and shows version."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
