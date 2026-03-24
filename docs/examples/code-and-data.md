# Code & Data Visualization

Prompts for exploratory data analysis, publication-quality figures, and data cleaning — from raw files to results-ready output.

---

## Who This Is For

If you work with data files (CSV, Excel, HDF5, NetCDF), write Python or no-code analysis, or need figures ready for a paper or slide deck, start here. These prompts work whether you write code or not.

---

## Prerequisites

| For browser prompts | For CLI prompts |
|--------------------|-----------------|
| [Claude.ai](https://claude.ai) account (free tier works) | Claude Code installed (`npm install -g @anthropic-ai/claude-code`) |
| Your data file available to paste or upload | Data file on disk; `cd` to your project directory before running `claude` |
| — | Python environment with `pandas`, `matplotlib`, `seaborn` |

---

## Prompt 1: Exploratory Data Analysis

**Use case:** You have a new dataset and want a rapid understanding of its structure, distributions, and anomalies before doing any modeling.

**Works in:** Browser (paste data inline) or CLI (reference file path)

```
I have a dataset at [path/to/data.csv]. Please:

1. Load it and print: shape, column names, dtypes, missing value counts
2. Generate distribution plots for all numeric columns (histogram + KDE)
3. Generate a correlation heatmap with annotated values
4. Identify the top 3 most interesting patterns or anomalies
5. Save all visualizations to outputs/eda/

Use seaborn with the "colorblind" palette. Summarize key findings in plain language at the end.
```

**Expected output:** A Python script that runs without errors, a set of saved figures, and a plain-English summary. The agent may ask for clarification about column meanings — answer specifically.

**What to verify:**
- Run the script yourself. Does it complete without errors?
- Do the distributions match your domain knowledge? (e.g., are negative values in a column that should be non-negative flagged?)
- Does the agent's interpretation of "interesting patterns" reflect actual domain insights, or is it restating obvious summary statistics?
- Check that output files were actually saved to `outputs/eda/`.

**Related skills:** `publication-figures` (formatting@research-agora), `statistical-validator` (research-agents@research-agora)

---

## Prompt 2: Publication-Quality Figure

**Use case:** You have results and need a figure that meets journal/conference standards: colorblind-safe, vector export, correct font sizes, no chartjunk.

**Works in:** CLI (reads your data file directly)

```
I have a CSV file at [path/to/data.csv] with columns [list column names and what they represent].

Create a publication-quality figure using matplotlib and seaborn that shows [describe the relationship or comparison you want to visualize].

Requirements:
- Colorblind-safe palette (seaborn "colorblind" or Okabe-Ito)
- Axis labels with units, descriptive title, legend
- Font size ≥ 10pt for all text elements
- Export as: figure.pdf (vector) and figure.png (300 dpi)
- No gridlines unless they aid readability; no chartjunk
- Figure size appropriate for a two-column journal layout (3.5 inches wide)

After generating, explain the design choices made.
```

**Expected output:** A Python script, two exported files (`figure.pdf` and `figure.png`), and a brief explanation of layout decisions.

**What to verify:**
- Open the PDF and check it is vector (zoom in — no pixelation).
- Check font sizes are legible at print scale (print a draft page or set zoom to 100%).
- Verify the colorblind palette was actually applied — check the script for `palette="colorblind"` or equivalent.
- Confirm axis labels include units.

**Related skills:** `publication-figures` (formatting@research-agora), `tikz-figures` (formatting@research-agora)

---

## Prompt 3: No-Code Data Analysis from Excel

**Use case:** You have an Excel or CSV file and want analysis and a chart without writing any code.

**Works in:** Browser (upload the file) or CLI

```
I have an Excel file called [file.xlsx] with data about [describe the topic in 1-2 sentences].

I don't write code. Please:
1. Read the file and tell me what's in it — column names, number of rows, what each column likely represents
2. Answer this specific question about the data: [state your question]
3. Make a bar chart showing [variable] grouped by [category], save as chart.png
4. Write a 3-bullet summary I can paste into a report

Explain everything in plain language. Do not show me code unless I ask.
```

**Expected output:** A plain-English description of the dataset, an answer to your specific question, a saved chart, and a report-ready summary.

**What to verify:**
- Does the agent's description of column meanings match your understanding of the data?
- Is the answer to your specific question supported by the actual data values, not a generalization?
- Open the chart — does it represent what you asked for?
- Are the 3 bullet points factually accurate? Check at least one data point manually.

**Related skills:** `publication-figures` (formatting@research-agora)

---

## Further Reading

- [Simon Willison — Coding Agents for Data Analysis (NICAR 2026)](https://simonwillison.net/2026/Mar/16/coding-agents-for-data-analysis/): Full arc from raw data to interactive visualization, with the verification checklist adapted above.
- [Dataquest — Getting Started with Claude Code for Data Scientists](https://www.dataquest.io/blog/getting-started-with-claude-code-for-data-scientists/): EDA pipelines and prompt templates.
- [Claude.ai artifacts](https://claude.ai): Upload a CSV directly in the browser → interactive charts with no installation.
