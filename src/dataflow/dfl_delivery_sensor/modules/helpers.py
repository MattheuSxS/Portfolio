import json
import logging
import apache_beam as beam
from datetime import datetime
from typing import Dict, Any, List


class ParseMessage(beam.DoFn):
    """Parseia mensagens do Pub/Sub"""
    def process(self, element):
        try:
            message = json.loads(element.decode('utf-8'))

            if 'delivery_id' not in message:
                logging.warning("The message is missing the delivery_id field.")
                raise

            message['updated_at'] = datetime.now().isoformat()

            yield message

        #TODO: Send to dead letter topic
        except Exception as e:
            logging.error(f"Error parsing message: {e}")
            # yield beam.pvalue.TaggedOutput('dead_letter', element)



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


class MergeDelivery(beam.DoFn):
    def process(self, element):
        delivery_id, delivery_messages = element

        latest_message = max(
            delivery_messages,
            key=lambda x: self._get_timestamp(x)
        )

        yield latest_message


    def _get_timestamp(self, delivery: Dict[str, Any]) -> str:
        return (delivery.get('created_at') or
                delivery.get('updated_at') or
                datetime.utcnow().isoformat())
