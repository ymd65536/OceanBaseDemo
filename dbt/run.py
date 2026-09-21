"""Launch dbt with an explicit mysql-connector Pure Python compatibility workaround.

This is a usability path for the currently tested OceanBase/dbt-mysql combination,
not a root-cause fix or an automatic fallback. Compatibility investigation belongs
in experiments/mysql_connector_compat.py.
"""

import mysql.connector


_original_connect = mysql.connector.connect


def connect_with_pure_python(*args, **kwargs):
    # Force one known execution path; never attempt C Extension then fall back.
    kwargs["use_pure"] = True
    return _original_connect(*args, **kwargs)


def main():
    mysql.connector.connect = connect_with_pure_python

    from dbt.cli.main import cli

    cli()


if __name__ == "__main__":
    main()
