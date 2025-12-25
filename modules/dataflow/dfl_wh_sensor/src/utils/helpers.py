import json
import logging
import apache_beam as beam


class MessageParser(beam.DoFn):
    def process(self, element):
        try:
            message_str = element.decode('utf-8')
            message = json.loads(message_str)

            if ('warehouse_id' not in message) or ('sensor_id' not in message):
                logging.debug("Message missing warehouse_id or sensor_id, skipping")
                return

            yield message

        except Exception as e:
            logging.debug(f"Error parsing message: {e}")
            # TODO: Dead letter


class Kwargs(beam.DoFn):
    def process(self, element):
        yield {
            'warehouse_id': element['warehouse_id'],
            'sensor_id': element['sensor_id'],
            'temperature_c': element['temperature_c'],
            'humidity_percent': element['humidity_percent'],
            'battery_voltage': element['battery_voltage'],
            'created_at': element['created_at'],
            'updated_at': element['updated_at']
        }