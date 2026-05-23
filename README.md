# depwatch

> GitHub Action that monitors dependency changelogs and summarizes breaking changes in PRs

## Installation

```bash
pip install depwatch
```

## Usage

Add the following to your GitHub Actions workflow (`.github/workflows/depwatch.yml`):

```yaml
name: Dependency Watch

on:
  pull_request:
    paths:
      - 'requirements*.txt'
      - 'pyproject.toml'

jobs:
  depwatch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run depwatch
        uses: your-org/depwatch@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          files: 'requirements.txt'
```

When a PR updates a dependency, **depwatch** will automatically fetch the relevant changelog entries and post a summary comment highlighting any breaking changes.

### Local Usage

You can also run depwatch locally to preview the output:

```bash
depwatch --file requirements.txt --base main
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `files` | `requirements.txt` | Dependency file(s) to monitor |
| `post_comment` | `true` | Post summary as a PR comment |
| `fail_on_breaking` | `false` | Fail the action if breaking changes are found |

## License

MIT © [your-org](https://github.com/your-org)