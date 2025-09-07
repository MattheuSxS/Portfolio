import json
import logging
import apache_beam as beam
from datetime import datetime


class MessageParser(beam.DoFn):
    """Parseia mensagens do Pub/Sub (um por vez, deixa o BigQuery lotear)"""

    def process(self, element):
        try:
            message_str = element.decode('utf-8')
            message = json.loads(message_str)

            if 'delivery_id' not in message:
                logging.debug("Message missing delivery_id, skipping")
                return

            message['updated_at'] = datetime.utcnow().isoformat()
            yield message

        except Exception as e:
            logging.debug(f"Error parsing message: {e}")
            # TODO: Dead letter


class SelectFields(beam.DoFn):
    def process(self, element):
        columns = \
            [
                'delivery_id',
                'vehicle_id',
                'purchase_id',
                'remaining_distance_km',
                'estimated_time_min',
                'delivery_difficulty',
                'status',
                'created_at',
                'updated_at'
            ]

        yield {key: element[key] for key in columns if key in element}

