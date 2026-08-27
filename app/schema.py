from sqlalchemy import inspect
from database import engine


SCHEMA_NAME = "analytics"


def get_database_schema():
    inspector = inspect(engine)

    tables = inspector.get_table_names(schema=SCHEMA_NAME)

    schema_info = {}

    for table in tables:
        columns = inspector.get_columns(
            table_name=table,
            schema=SCHEMA_NAME
        )

        schema_info[table] = [
            {
                "name": column["name"],
                "type": str(column["type"])
            }
            for column in columns
        ]

    return schema_info


def get_database_relationships():
    inspector = inspect(engine)

    tables = inspector.get_table_names(schema=SCHEMA_NAME)

    relationships = []

    for table in tables:
        foreign_keys = inspector.get_foreign_keys(
            table_name=table,
            schema=SCHEMA_NAME
        )

        for fk in foreign_keys:
            constrained_columns = fk.get("constrained_columns", [])
            referred_columns = fk.get("referred_columns", [])
            referred_table = fk.get("referred_table")
            referred_schema = fk.get("referred_schema") or SCHEMA_NAME

            for source_column, target_column in zip(
                constrained_columns,
                referred_columns
            ):
                relationships.append(
                    {
                        "source_table": table,
                        "source_column": source_column,
                        "target_schema": referred_schema,
                        "target_table": referred_table,
                        "target_column": target_column
                    }
                )

    return relationships


if __name__ == "__main__":

    schema = get_database_schema()

    print("\n================ DATABASE SCHEMA ================\n")

    for table, columns in schema.items():

        print(f"TABLE: {table}")

        for column in columns:
            print(
                f"  - {column['name']} ({column['type']})"
            )

        print()

    relationships = get_database_relationships()

    print("\n================ RELATIONSHIPS ================\n")

    for relationship in relationships:

        print(
            f"{relationship['source_table']}."
            f"{relationship['source_column']}"
            f" -> "
            f"{relationship['target_table']}."
            f"{relationship['target_column']}"
        )