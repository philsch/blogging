# MIT License
#
# Copyright (c) 2019 Philipp Schmiedel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#
# IMPORTANT
# ---------
# Adjust the transformation logic in CellTransformDoFn to match your particular case !!!
#


import logging
import apache_beam as beam
from apache_beam.metrics import Metrics
from apache_beam.options.pipeline_options import PipelineOptions

try:
    from avro.schema import Parse  # avro-python3 library for python3
except ImportError:
    from avro.schema import parse as Parse  # avro library for python2

BIG_TABLE_SCHEMA = Parse('''
{
    "type": "record",
    "name": "BigtableRow",
    "namespace": "com.google.cloud.teleport.bigtable",
    "fields": [
        {
            "name": "key",
            "type": "bytes"
        },
        {
            "name": "cells",
            "type": {
                "type": "array",
                "items": {
                    "type": "record",
                    "name": "BigtableCell",
                    "fields": [
                        {
                            "name": "family",
                            "type": "string"
                        },
                        {
                            "name": "qualifier",
                            "type": "bytes"
                        },
                        {
                            "name": "timestamp",
                            "type": "long",
                            "logicalType": "timestamp-micros"
                        },
                        {
                            "name": "value",
                            "type": "bytes"
                        }
                    ]
                }
            }
        }
    ]
}
''')


class AvroTransformOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument(
            '--input',
            help='Path of the avro file to read from')
        parser.add_value_provider_argument(
            '--output',
            help='Output avro file to write results to')
        parser.add_value_provider_argument(
            '--fastavro',
            default=False,
            help='When set, use fastavro for Avro I/O')


class CellTransformDoFn(beam.DoFn):
    def __init__(self):
        super(CellTransformDoFn, self).__init__()
        self.total_counter = Metrics.counter(self.__class__, 'total')

    def map_hash_to_new_prefix(self, old_hash):
        """
        Our new rowkey should have a prefix 0 - 3, as 4 is our expected number of nodes in the BigTable cluster

        :param old_hash:
        :return:
        """
        hash_first_char = old_hash[0].lower()

        if hash_first_char == 'a':
            return 2
        if hash_first_char == 'b':
            return 3
        if hash_first_char == 'c':
            return 0
        if hash_first_char == 'd':
            return 1
        if hash_first_char == 'e':
            return 2
        if hash_first_char == 'f':
            return 3

        return int(hash_first_char) % 4

    def create_row_key(self, cell):
        """
        Transform existing row key <hash>_YYYYmmDD_HHMMSS_ff to [0-3]_YYYYmmDD_HHMMSS_ff_<hash>

        :param cell:
        :return:
        """
        old_row_key_parts = cell.get('key').split('_')

        return "{}_{}_{}_{}_{}".format(
            self.map_hash_to_new_prefix(old_row_key_parts[0]),  # 0-4 prefix
            old_row_key_parts[1],  # date
            old_row_key_parts[2],  # time
            old_row_key_parts[3],  # ms
            old_row_key_parts[0]  # random hash
        )

    def process(self, element, *args, **kwargs):
        element['key'] = self.create_row_key(element)
        self.total_counter.inc()

        yield element


def run():
    logging.info('Starting main function')

    pipeline_options = PipelineOptions()
    pipeline = beam.Pipeline(options=pipeline_options)
    options = pipeline_options.view_as(AvroTransformOptions)

    steps = (
            pipeline
            | 'Create' >> beam.Create(['%s*' % options.input])
            | 'ReadData' >> beam.io.ReadAllFromAvro(use_fastavro=options.fastavro)
            | 'Transaform rowkey' >> beam.ParDo(CellTransformDoFn())
            | 'WriteData' >> beam.io.WriteToAvro(options.output, BIG_TABLE_SCHEMA, use_fastavro=options.fastavro))

    result = pipeline.run()
    result.wait_until_finish()

    # Query metrics only when template has actual run (not the case for GCP template creation)
    if hasattr(result, 'has_job') and result.has_job:
        metrics = result.metrics().query()

        for counter in metrics['counters']:
            logging.info("Counter: %s", counter)

        for dist in metrics['distributions']:
            logging.info("Distribution: %s", dist)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
