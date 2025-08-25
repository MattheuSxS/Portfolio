import json
import apache_beam as beam


def parse_pubsub_message(message) -> dict:
    """
    Parses a Pub/Sub message and returns the result.

    Args:
        message (bytes): The Pub/Sub message to parse.

    Returns:
        dict: The parsed result.

    """

    return message.decode('utf-8')


def split_dict(element) -> list[dict]:
    """
    Splits a dictionary into a list of dictionaries, where each dictionary contains
    a single key-value pair from the original dictionary.

    Args:
        element (dict): The dictionary to be split.

    Returns:
        list: A list of dictionaries, where each dictionary contains a single key-value
        pair from the original dictionary.
    """

    return [{key: value} for key, value in element.items()]


class ConvertToTableRowFn(beam.DoFn):
    """
    A Beam DoFn class that converts a dictionary element into a table row.

    This class takes a dictionary element as input and converts it into a table row format.
    Each key-value pair in the dictionary represents a column-value pair in the table row.

    Args:
        element (dict): The input dictionary element to be converted.

    Yields:
        dict: A table row dictionary with the converted data.

    Example:
        An example usage of this class:

        ```
        data = {'table_name': {'column1': [1, 2, 3], 'column2': ['a', 'b', 'c']}}
        fn = ConvertToTableRowFn()
        result = fn.process(data)
        for row in result:
            print(row)
        ```

        Output:
        ```
        {'table_name': {'column1': 1, 'column2': 'a'}}
        {'table_name': {'column1': 2, 'column2': 'b'}}
        {'table_name': {'column1': 3, 'column2': 'c'}}
        ```
    """

    def process(self, element):
        if 'currently_data' in element:
            pass
        else:
            table_name, data_dict = next(iter(element.items()))

            max_len = max(len(values) for values in data_dict.values())

            for i in range(max_len):
                row = {}
                for key, values in data_dict.items():
                    row[key] = values[i] if i < len(values) else None

                yield {table_name: row}


def _get_schema_bigquery(project:str, dataset:str, table:str) -> str:
    """ This function retrieves the structure of an existing BigQuery
        table and returns that structure. This returned schema can then be used
        to ensure data conformance during the insert operation, ensuring that the
        inserted data matches the table's predefined schema."

    Args:
        project:str = Project Name
        dataset:str = Dataset Name
        table:str = Table Name

    Returns:
        str: returns a string with the field name and its type
        example output:
            dt_hr_evento:TIMESTAMP, cod_evento:INTEGER, cod_origem_evento:STRING, ....
    """

    from google.cloud import bigquery

    client = bigquery.Client(project=project)
    table_ref = client.get_table(f"{project}.{dataset}.{table}")

    field_types = [f"{field.name}:{field.field_type}" for field in table_ref.schema]
    str_schema = ", ".join(field_types)

    return str_schema


def get_schema(project_id:str, dataset_id:str, list_table:list) -> dict:
    """
    Retrieves the schema of multiple tables in a BigQuery dataset and returns a dictionary
    where the keys are the table names and the values are the corresponding schemas.

    Args:
        project_id (str): The ID of the Google Cloud project.
        dataset_id (str): The ID of the BigQuery dataset.
        list_table (list): A list of table names.

    Returns:
        dict: A dictionary where the keys are table names and the values are the corresponding schemas.

        example output:
            {'test: 'dt_hr_evento:TIMESTAMP, cod_evento:INTEGER, cod_origem_evento:STRING, ....'}
    """
    data_dict = {}
    for table in list_table:
        data_dict[table] = _get_schema_bigquery(project_id, dataset_id, table)

    return data_dict


def write_to_bigquery(element:tuple, schema_str:dict, project_id:str, dataset_id:str) -> None:
    """
    Writes data to BigQuery.

    Args:
        element (tuple): A tuple containing the table ID and a list of data.
        schema_str (dict): A dictionary mapping table IDs to schema strings.
        project_id (str): The ID of the Google Cloud project.
        dataset_id (str): The ID of the BigQuery dataset.

    Returns:
        PCollection: A PCollection representing the data written to BigQuery.
    """

    import apache_beam as beam
    from apache_beam.io.gcp.bigquery import WriteToBigQuery

    table_id, data_list = element
    list_data = [data[table_id] for data in data_list]

    list_data | WriteToBigQuery(
        table               = f"{project_id}:{dataset_id}.{table_id}",
        schema              = schema_str[table_id],
        create_disposition  = beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        write_disposition   = beam.io.BigQueryDisposition.WRITE_APPEND,
        method              = "STREAMING_INSERTS"
    )