# Job Schema Replication
# This code facilitates the replication of a specified schema to a user-defined target catalog.
# Ensure the system schema is enabled as a prerequisite.
# Ensure the job runs periodically to avoid missing any data.
# Avoid pausing the job for extended periods to prevent data loss and stream failures. If this occurs, the user must set an option to ignore missing files.
# This notebook is reusable across different system schema replications.
# You need to create the volume path as a prerequisite and pass it as a checkpoint. The table name will be the checkpoint name for every stream.

# Widgets to capture user inputs for catalog, schema, target_catalog, and checkpoint
dbutils.widgets.text("catalog", "system")
dbutils.widgets.text("schema", "lakeflow")
dbutils.widgets.text("target_catalog", "")
dbutils.widgets.text("checkpoint", "/Volumes/default/streams_1")

# Retrieving the values entered by the user in the widgets
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
target_catalog = dbutils.widgets.get("target_catalog")
checkpoint = dbutils.widgets.get("checkpoint")


def get_tables_list(catalog, schema, target_catalog):
    """
    Retrieves a list of tables from the specified catalog and schema, and formats them with the target catalog and schema.

    Parameters:
    catalog (str): The catalog from which to retrieve the tables.
    schema (str): The schema from which to retrieve the tables.
    target_catalog (str): The target catalog to prepend to the table names.

    Returns:
    list: A list of table names formatted with the target catalog and schema.
    """
    target_namespace = f"{target_catalog}.{schema}"
    tables_df = spark.sql(f"SHOW TABLES IN {catalog}.{schema}")
    tables_list = tables_df.select("tableName").rdd.flatMap(lambda x: x).collect()
    tables_list = [f"{target_namespace}.{tbl}" for tbl in tables_list]
    return tables_list

tables_list = get_tables_list(catalog, schema, target_catalog)
tables_list

def backup_table(table_name, checkpoint):
    """
    Backs up a specified table using structured streaming.

    Parameters:
    table_name (str): The full name of the table to back up, in the format 'catalog.schema.table'.
    checkpoint (str): The location to store checkpoint data.

    Returns:
    DataStreamWriter: The streaming query object.
    """
    namespace = table_name.split(".")
    df = spark.readStream.option("skipChangeCommits", "true").table(f"system.{namespace[1]}.{namespace[2]}")
    stream = df.writeStream \
        .option("checkpointLocation", f"{checkpoint}/{namespace[2]}") \
        .option("mergeSchema", "true") \
        .trigger(availableNow=True) \
        .toTable(f"{table_name}")
    return stream


spark.sql(f"CREATE SCHEMA IF NOT EXISTS {target_catalog}.{schema}")


for tbl in tables_list:
    print(f"Processing table name {tbl}")
    namespace = tbl.split('.')
    backup_table(tbl,checkpoint)