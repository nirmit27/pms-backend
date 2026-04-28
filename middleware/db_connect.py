"""
Databricks connection - TEST
"""

import sys
from os import getenv
from dotenv import load_dotenv

from databricks import sql


load_dotenv()


def main():
    # NOTE: Querying sample table data
    query = """select name
from workspace.default.sample_data
where substring(id, -1, 1) = '3';
"""

    server_hostname = getenv("DATABRICKS_SERVER_HOSTNAME")
    http_path = getenv("DATABRICKS_HTTP_PATH")
    access_token = getenv("DATABRICKS_TOKEN")

    # NOTE: Checking env. vars.
    if not all([server_hostname, http_path, access_token]):
        print("ERROR: Missing required environment variables!", file=sys.stderr)
        print(
            "Please set DATABRICKS_SERVER_HOSTNAME, DATABRICKS_HTTP_PATH, and DATABRICKS_TOKEN.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        with sql.connect(
            server_hostname=server_hostname,
            http_path=http_path,
            access_token=access_token,
        ) as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query, [2])
                    result = cursor.fetchall()

                if result:
                    for row in result:
                        print(row)
                else:
                    print("No results returned from query.")

            except sql.Error as e:
                print(f"ERROR: Query execution failed: {e}", file=sys.stderr)
                sys.exit(2)

    except sql.Error as e:
        print(f"ERROR: Connection to Databricks failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(3)


# Driver
if __name__ == "__main__":
    main()
