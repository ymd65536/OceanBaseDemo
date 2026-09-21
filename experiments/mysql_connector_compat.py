import argparse
import json
import os
import platform
import sys
import traceback
from datetime import datetime
from pathlib import Path

import mysql.connector


TABLE_NAME = "mysql_connector_compat_experiment"
SESSION_QUERY = """
SELECT
    @@character_set_client,
    @@character_set_connection,
    @@character_set_results,
    @@collation_connection
"""


def required_environment():
    names = (
        "OCEANBASE_HOST",
        "OCEANBASE_PORT",
        "OCEANBASE_USER",
        "OCEANBASE_PASSWORD",
        "OCEANBASE_DATABASE",
    )
    missing = [name for name in names if name not in os.environ]
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

    return {
        "host": os.environ["OCEANBASE_HOST"],
        "port": int(os.environ["OCEANBASE_PORT"]),
        "user": os.environ["OCEANBASE_USER"],
        "password": os.environ["OCEANBASE_PASSWORD"],
        "database": os.environ["OCEANBASE_DATABASE"],
    }


def connection_class_name(connection):
    cls = type(connection)
    return f"{cls.__module__}.{cls.__name__}"


def run_queries(connection, result):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT VERSION()")
        result["server_version"] = cursor.fetchone()[0]

        cursor.execute(SESSION_QUERY)
        session = cursor.fetchone()
        result["session"] = {
            "character_set_client": session[0],
            "character_set_connection": session[1],
            "character_set_results": session[2],
            "collation_connection": session[3],
        }

        cursor.execute("SELECT 1")
        result["select_1"] = "PASS" if cursor.fetchone()[0] == 1 else "FAIL"

        cursor.execute(f"DROP TABLE IF EXISTS `{TABLE_NAME}`")
        cursor.execute(
            f"CREATE TABLE `{TABLE_NAME}` ("
            "id BIGINT PRIMARY KEY, label VARCHAR(100) NOT NULL)"
        )
        cursor.execute(
            f"INSERT INTO `{TABLE_NAME}` (id, label) VALUES (%s, %s)",
            (1, "connector compatibility"),
        )
        connection.commit()
        cursor.execute(f"SELECT id, label FROM `{TABLE_NAME}` WHERE id = %s", (1,))
        row = cursor.fetchone()
        result["crud"] = (
            "PASS" if row == (1, "connector compatibility") else "FAIL"
        )
        result["crud_row"] = list(row) if row is not None else None
    finally:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS `{TABLE_NAME}`")
            connection.commit()
            result["cleanup"] = "PASS"
        except Exception:
            result["cleanup"] = "FAIL"
            result["cleanup_traceback"] = traceback.format_exc()
        cursor.close()


def run_case(name, config, use_pure, charset=None, collation=None):
    result = {
        "case": name,
        "use_pure": use_pure,
        "charset": charset,
        "collation": collation,
        "connection_class": "not returned (connection construction failed)",
        "connect": "FAIL",
        "select_1": "-",
        "crud": "-",
        "cleanup": "-",
        "server_version": None,
        "session": None,
        "exception_class": None,
        "exception_message": None,
        "traceback": None,
    }
    kwargs = {**config, "use_pure": use_pure}
    if charset is not None:
        kwargs["charset"] = charset
    if collation is not None:
        kwargs["collation"] = collation

    connection = None
    try:
        connection = mysql.connector.connect(**kwargs)
        result["connection_class"] = connection_class_name(connection)
        result["connect"] = "PASS"
        run_queries(connection, result)
    except Exception as error:
        result["exception_class"] = f"{type(error).__module__}.{type(error).__name__}"
        result["exception_message"] = str(error)
        result["traceback"] = traceback.format_exc()
    finally:
        if connection is not None and connection.is_connected():
            connection.close()

    return result


def discover_explicit_settings(config):
    discovery = {
        "success": False,
        "charset": None,
        "collation": None,
        "available_collations_for_charset": [],
        "exception_class": None,
        "exception_message": None,
        "traceback": None,
    }
    connection = None
    try:
        connection = mysql.connector.connect(**config, use_pure=True)
        cursor = connection.cursor()
        cursor.execute(SESSION_QUERY)
        session = cursor.fetchone()
        charset = session[1]
        collation = session[3]

        cursor.execute("SHOW COLLATION")
        available = [row[0] for row in cursor.fetchall() if row[1] == charset]
        if collation not in available:
            raise RuntimeError(
                f"Session collation {collation!r} was not present in SHOW COLLATION "
                f"for charset {charset!r}"
            )

        discovery.update(
            {
                "success": True,
                "charset": charset,
                "collation": collation,
                "available_collations_for_charset": available,
            }
        )
        cursor.close()
    except Exception as error:
        discovery["exception_class"] = (
            f"{type(error).__module__}.{type(error).__name__}"
        )
        discovery["exception_message"] = str(error)
        discovery["traceback"] = traceback.format_exc()
    finally:
        if connection is not None and connection.is_connected():
            connection.close()

    return discovery


def skipped_case(name, use_pure, discovery):
    return {
        "case": name,
        "use_pure": use_pure,
        "charset": None,
        "collation": None,
        "connection_class": None,
        "connect": "SKIP",
        "select_1": "-",
        "crud": "-",
        "cleanup": "-",
        "server_version": None,
        "session": None,
        "exception_class": discovery["exception_class"],
        "exception_message": "Explicit settings unavailable: "
        + (discovery["exception_message"] or "discovery failed"),
        "traceback": discovery["traceback"],
    }


def print_report(report):
    print("MySQL Connector Compatibility Experiment")
    print("=" * 40)
    print(f"mysql-connector-python: {report['environment']['connector_version']}")
    print(f"Python: {report['environment']['python_version']}")
    print(f"Platform: {report['environment']['platform']}")
    print()

    discovery = report["explicit_settings_discovery"]
    if discovery["success"]:
        print("Explicit settings discovered from OceanBase session and SHOW COLLATION:")
        print(f"  charset:   {discovery['charset']}")
        print(f"  collation: {discovery['collation']}")
    else:
        print("Explicit settings discovery: FAIL")
        print(f"  {discovery['exception_class']}: {discovery['exception_message']}")
    print()

    print(f"{'Case':32} {'Connect':8} {'SELECT 1':10} {'CRUD':8} {'Cleanup':8}")
    print("-" * 72)
    for result in report["cases"]:
        print(
            f"{result['case']:32} {result['connect']:8} "
            f"{result['select_1']:10} {result['crud']:8} {result['cleanup']:8}"
        )

    for result in report["cases"]:
        print(f"\n[{result['case']}]")
        print(f"use_pure: {result['use_pure']}")
        print(f"charset: {result['charset'] or '(not specified)'}")
        print(f"collation: {result['collation'] or '(not specified)'}")
        print(f"connection_class: {result['connection_class'] or '-'}")
        print(f"server_version: {result['server_version'] or '-'}")
        if result["session"]:
            for key, value in result["session"].items():
                print(f"{key}: {value}")
        if result["exception_class"]:
            print(f"exception_class: {result['exception_class']}")
            print(f"exception_message: {result['exception_message']}")
            print("full_traceback:")
            print(result["traceback"].rstrip())

    print("\nFACTS")
    for fact in report["facts"]:
        print(f"- {fact}")
    print("\nHYPOTHESES")
    for hypothesis in report["hypotheses"]:
        print(f"- {hypothesis}")


def build_report(config):
    default_cext = run_case("C Extension / default", config, use_pure=False)
    default_pure = run_case("Pure Python / default", config, use_pure=True)
    discovery = discover_explicit_settings(config)

    if discovery["success"]:
        explicit_cext = run_case(
            "C Extension / explicit",
            config,
            use_pure=False,
            charset=discovery["charset"],
            collation=discovery["collation"],
        )
        explicit_pure = run_case(
            "Pure Python / explicit",
            config,
            use_pure=True,
            charset=discovery["charset"],
            collation=discovery["collation"],
        )
    else:
        explicit_cext = skipped_case("C Extension / explicit", False, discovery)
        explicit_pure = skipped_case("Pure Python / explicit", True, discovery)

    cases = [default_cext, default_pure, explicit_cext, explicit_pure]
    facts = [
        f"{result['case']}: connect={result['connect']}, "
        f"SELECT 1={result['select_1']}, CRUD={result['crud']}."
        for result in cases
    ]
    hypotheses = [
        "A failure may be related to charset/collation negotiation or MySQL protocol metadata handling.",
        "Differences between the C Extension and Pure Python protocol implementations may affect the result.",
        "This experiment does not by itself assign the defect to OceanBase, mysql-connector-python, or dbt-mysql.",
    ]

    return {
        "generated_at": datetime.now().astimezone().isoformat(),
        "environment": {
            "connector_version": mysql.connector.__version__,
            "python_version": sys.version,
            "platform": platform.platform(),
            "target": {
                "host": config["host"],
                "port": config["port"],
                "database": config["database"],
                "user": config["user"],
                "password": "<redacted>",
            },
        },
        "explicit_settings_discovery": discovery,
        "cases": cases,
        "facts": facts,
        "hypotheses": hypotheses,
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compare mysql-connector-python C Extension and Pure Python paths against OceanBase."
    )
    parser.add_argument(
        "--json",
        type=Path,
        dest="json_path",
        help="Write the complete experiment report to this JSON file.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config = required_environment()
    report = build_report(config)
    print_report(report)

    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\nJSON report written to {args.json_path}")


if __name__ == "__main__":
    main()
