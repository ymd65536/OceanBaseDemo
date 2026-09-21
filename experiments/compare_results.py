import argparse
import json
from pathlib import Path


def load_reports(paths):
    reports = []
    target_names = set()
    for path in paths:
        report = json.loads(path.read_text(encoding="utf-8"))
        target_name = report["environment"]["target"]["name"]
        if target_name in target_names:
            raise ValueError(f"Duplicate target name: {target_name}")
        target_names.add(target_name)
        reports.append((path, report))
    return reports


def server_version(report):
    for case in report["cases"]:
        if case["server_version"]:
            return case["server_version"]
    return "NOT RECORDED"


def case_result(case):
    return f"{case['connect']} / {case['select_1']} / {case['crud']}"


def render_markdown(reports):
    lines = [
        "# MySQL Connector Compatibility Comparison",
        "",
        "This table contains only recorded experiment results. No missing target or case is inferred.",
        "",
        "## Environments",
        "",
        "| Target | Server version | Connector version | Python version | Evidence |",
        "|---|---|---|---|---|",
    ]
    for path, report in reports:
        environment = report["environment"]
        target = environment["target"]
        python_version = environment["python_version"].splitlines()[0]
        lines.append(
            f"| {target['name']} | {server_version(report)} | "
            f"{environment['connector_version']} | {python_version} | `{path.as_posix()}` |"
        )

    ordered_cases = []
    for _, report in reports:
        for case in report["cases"]:
            if case["case"] not in ordered_cases:
                ordered_cases.append(case["case"])

    lines.extend(
        [
            "",
            "## Results",
            "",
            "Each result is `Connect / SELECT 1 / CRUD`.",
            "",
            "| Case | " + " | ".join(report[1]["environment"]["target"]["name"] for report in reports) + " |",
            "|---|" + "---|" * len(reports),
        ]
    )
    for case_name in ordered_cases:
        cells = []
        for _, report in reports:
            matching = next(
                (case for case in report["cases"] if case["case"] == case_name),
                None,
            )
            cells.append(case_result(matching) if matching else "NOT RECORDED")
        lines.append(f"| {case_name} | " + " | ".join(cells) + " |")

    return "\n".join(lines) + "\n"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a Markdown comparison from recorded compatibility JSON files."
    )
    parser.add_argument("results", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main():
    args = parse_args()
    markdown = render_markdown(load_reports(args.results))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
        print(f"Comparison written to {args.output}")
    else:
        print(markdown, end="")


if __name__ == "__main__":
    main()
