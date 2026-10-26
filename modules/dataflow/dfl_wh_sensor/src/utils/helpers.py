import json
import logging
import apache_beam as beam
from datetime import datetime


class MessageParser(beam.DoFn):
    def process(self, element):
        try:
            message_str = element.decode('utf-8')
            message = json.loads(message_str)

            if ('warehouse_id' not in message) or ('sensor_id' not in message):
                logging.warning("Message missing warehouse_id or sensor_id, skipping")
                return

            yield message

        except Exception as e:
            logging.error(f"Error parsing message: {e}")
            # TODO: Dead letter


class Kwargs(beam.DoFn):
    def process(self, element):
        yield {
            'warehouse_id': element['warehouse_id'],
            'sensor_id':    element['sensor_id'],
            'time_stamp':   element['time_stamp'],
            'temperature':  element['temperature'],
            'humidity':     element['humidity'],
            'pressure':     element['pressure'],
            'created_at':   datetime.now().isoformat()
        }


class Kwargs(beam.DoFn):
    def process(self, element):
        # Detecta anomalia
        anomaly_type = None
        if element['temperature'] > 30.0:
            anomaly_type = 'temperature_spike'
        elif element['humidity'] < 30:
            anomaly_type = 'humidity_drop'
        elif element['pressure'] < 1000.0:
            anomaly_type = 'pressure_drop'

        yield {
            'warehouse_id': element['warehouse_id'],
            'sensor_id':    element['sensor_id'],
            'time_stamp':   element['time_stamp'],
            'temperature':  element['temperature'],
            'humidity':     element['humidity'],
            'pressure':     element['pressure'],
            'created_at':   datetime.now().isoformat(),
            **({'anomaly_type': anomaly_type} if anomaly_type else {})
        }


def write_to_bigquery(project_id, dataset_id, table_id, bq_schema):
    return beam.io.WriteToBigQuery(
        table                   = f"{project_id}.{dataset_id}.{table_id}",
        schema                  = bq_schema,
        create_disposition      = beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        write_disposition       = beam.io.BigQueryDisposition.WRITE_APPEND,
        method                  = beam.io.WriteToBigQuery.Method.STREAMING_INSERTS
    )