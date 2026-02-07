---
name: xlsx-create
description: Create and edit Excel spreadsheets using openpyxl
model: haiku
version: 1.0.0
triggers:
  - spreadsheet
  - excel
  - xlsx
  - data table
  - csv to excel
dependencies:
  - openpyxl>=3.1.0
  - pandas>=2.0.0
---

# Excel Spreadsheet Creation Skill

> **Script-first**: This skill generates spreadsheets via openpyxl/pandas scripts. No LLM generation needed.

Create and manipulate Excel files using openpyxl and pandas.

## Installation

```bash
pip install openpyxl pandas
```

## Quick Reference

### Create Basic Spreadsheet

```python
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

wb = Workbook()
ws = wb.active
ws.title = "Results"

# Add data
ws["A1"] = "Method"
ws["B1"] = "Accuracy"
ws["C1"] = "F1 Score"

data = [
    ["Baseline", 0.82, 0.79],
    ["Ours", 0.94, 0.92],
]

for row_idx, row_data in enumerate(data, start=2):
    for col_idx, value in enumerate(row_data, start=1):
        ws.cell(row=row_idx, column=col_idx, value=value)

wb.save("results.xlsx")
```

### From Pandas DataFrame

```python
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

df = pd.DataFrame({
    "Method": ["Baseline", "Ours (ablation)", "Ours (full)"],
    "Accuracy": [0.82, 0.89, 0.94],
    "F1": [0.79, 0.86, 0.92],
    "Params (M)": [125, 125, 125],
})

wb = Workbook()
ws = wb.active

for r in dataframe_to_rows(df, index=False, header=True):
    ws.append(r)

wb.save("dataframe_export.xlsx")
```

### Cell Formatting

```python
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

# Bold header row
header_font = Font(bold=True, size=12)
for cell in ws[1]:
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center")

# Number formatting
for row in ws.iter_rows(min_row=2, min_col=2, max_col=3):
    for cell in row:
        cell.number_format = "0.00%"  # Percentage
        # Or: "0.000" for 3 decimal places
        # Or: "#,##0" for thousands separator

# Column widths
ws.column_dimensions["A"].width = 20
ws.column_dimensions["B"].width = 12
ws.column_dimensions["C"].width = 12

# Auto-fit (approximate)
for col in ws.columns:
    max_length = max(len(str(cell.value or "")) for cell in col)
    ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2
```

### Conditional Formatting

```python
from openpyxl.formatting.rule import ColorScaleRule, FormulaRule
from openpyxl.styles import PatternFill

# Color scale (green-yellow-red)
color_scale = ColorScaleRule(
    start_type="min", start_color="FF0000",
    mid_type="percentile", mid_value=50, mid_color="FFFF00",
    end_type="max", end_color="00FF00"
)
ws.conditional_formatting.add("B2:B10", color_scale)

# Highlight cells above threshold
green_fill = PatternFill(start_color="90EE90", fill_type="solid")
ws.conditional_formatting.add(
    "B2:B10",
    FormulaRule(formula=["B2>0.9"], fill=green_fill)
)
```

### Multiple Sheets

```python
wb = Workbook()

# First sheet (default)
ws1 = wb.active
ws1.title = "Summary"

# Additional sheets
ws2 = wb.create_sheet("Raw Data")
ws3 = wb.create_sheet("Analysis")

# Reorder sheets
wb.move_sheet("Summary", offset=1)  # Move after Raw Data

wb.save("multi_sheet.xlsx")
```

### Formulas

```python
# Basic formulas
ws["D2"] = "=B2+C2"
ws["B10"] = "=AVERAGE(B2:B9)"
ws["B11"] = "=STDEV(B2:B9)"

# Named ranges for clarity
from openpyxl.workbook.defined_name import DefinedName

# Define named range
wb.defined_names["accuracy_scores"] = DefinedName(
    name="accuracy_scores",
    attr_text="Results!$B$2:$B$10"
)

# Use in formula
ws["B12"] = "=AVERAGE(accuracy_scores)"
```

### Charts

```python
from openpyxl.chart import BarChart, Reference

# Create chart
chart = BarChart()
chart.type = "col"
chart.title = "Model Comparison"
chart.x_axis.title = "Method"
chart.y_axis.title = "Score"

# Data range
data = Reference(ws, min_col=2, min_row=1, max_col=3, max_row=4)
categories = Reference(ws, min_col=1, min_row=2, max_row=4)

chart.add_data(data, titles_from_data=True)
chart.set_categories(categories)
chart.shape = 4  # Rectangle

# Position chart
ws.add_chart(chart, "E2")

wb.save("with_chart.xlsx")
```

## Research Data Patterns

### Experiment Results Table

```python
def create_experiment_results(
    methods: list[str],
    metrics: dict[str, list[float]],
    output_path: str,
    highlight_best: bool = True
):
    """
    Create formatted experiment results table.

    Args:
        methods: List of method names
        metrics: Dict of metric_name -> list of values
        output_path: Output file path
        highlight_best: Whether to bold best values
    """
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

    wb = Workbook()
    ws = wb.active
    ws.title = "Results"

    # Header row
    headers = ["Method"] + list(metrics.keys())
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # Data rows
    for row, method in enumerate(methods, 2):
        ws.cell(row=row, column=1, value=method)
        for col, (metric, values) in enumerate(metrics.items(), 2):
            cell = ws.cell(row=row, column=col, value=values[row-2])
            cell.number_format = "0.000"
            cell.alignment = Alignment(horizontal="center")

    # Highlight best values
    if highlight_best:
        for col, values in enumerate(metrics.values(), 2):
            best_idx = values.index(max(values))
            ws.cell(row=best_idx+2, column=col).font = Font(bold=True)
            ws.cell(row=best_idx+2, column=col).fill = PatternFill(
                start_color="90EE90", fill_type="solid"
            )

    # Auto-fit columns
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 15

    wb.save(output_path)
    return output_path

# Usage
create_experiment_results(
    methods=["Baseline", "Ours (w/o aug)", "Ours (full)"],
    metrics={
        "Accuracy": [0.82, 0.89, 0.94],
        "F1 Score": [0.79, 0.86, 0.92],
        "Precision": [0.81, 0.88, 0.93],
    },
    output_path="experiment_results.xlsx"
)
```

### Hyperparameter Search Summary

```python
def create_hyperparam_summary(
    experiments: list[dict],
    output_path: str
):
    """
    Create hyperparameter search summary.

    Args:
        experiments: List of {params: dict, metrics: dict}
        output_path: Output file path
    """
    import pandas as pd
    from openpyxl import Workbook
    from openpyxl.utils.dataframe import dataframe_to_rows

    # Flatten to DataFrame
    rows = []
    for exp in experiments:
        row = {**exp["params"], **exp["metrics"]}
        rows.append(row)

    df = pd.DataFrame(rows)

    # Sort by primary metric
    metric_cols = [c for c in df.columns if c not in experiments[0]["params"]]
    df = df.sort_values(metric_cols[0], ascending=False)

    # Export
    wb = Workbook()
    ws = wb.active

    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)

    wb.save(output_path)
    return output_path
```

## CSV Conversion

```python
import pandas as pd

# CSV to Excel
df = pd.read_csv("data.csv")
df.to_excel("data.xlsx", index=False, engine="openpyxl")

# Excel to CSV
df = pd.read_excel("data.xlsx", engine="openpyxl")
df.to_csv("data.csv", index=False)

# Multiple CSVs to sheets
with pd.ExcelWriter("combined.xlsx", engine="openpyxl") as writer:
    for csv_file in ["train.csv", "val.csv", "test.csv"]:
        df = pd.read_csv(csv_file)
        sheet_name = csv_file.replace(".csv", "")
        df.to_excel(writer, sheet_name=sheet_name, index=False)
```

## Reading Excel Files

```python
from openpyxl import load_workbook

# Load existing file
wb = load_workbook("existing.xlsx")
ws = wb.active

# Read cell values
print(ws["A1"].value)
print(ws.cell(row=1, column=1).value)

# Iterate rows
for row in ws.iter_rows(min_row=2, values_only=True):
    print(row)

# To pandas
import pandas as pd
df = pd.read_excel("existing.xlsx", sheet_name="Results", engine="openpyxl")
```

## Output

```python
# Standard save
wb.save("output.xlsx")
print(f"Saved to: output.xlsx")

# With pandas
df.to_excel("output.xlsx", index=False, engine="openpyxl")
```
