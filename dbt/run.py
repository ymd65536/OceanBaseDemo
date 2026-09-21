import mysql.connector


_original_connect = mysql.connector.connect


def connect_with_pure_python(*args, **kwargs):
    kwargs.setdefault("use_pure", True)
    return _original_connect(*args, **kwargs)


def main():
    mysql.connector.connect = connect_with_pure_python

    from dbt.cli.main import cli

    cli()


if __name__ == "__main__":
    main()
