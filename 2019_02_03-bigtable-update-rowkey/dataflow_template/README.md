avro_transform.py
=================

Updating the row keys for a complete BigTable table consists of the following steps:

1. Use the pre-defined Google Dataflow template *Cloud BigTable to Cloud Storage Avro files* to export the table
1. Apply this pipeline 
1. Write the resulting Avro-File back into BigTable using the pre-defined Google Dataflow template 
*Cloud Storage Avro files to Cloud BigTable*

### Adjust the transformation logic

Replace the transformation logic in `CellTransformDoFn.process` to match your particular case. You can
use this pipeline of course also to change other fields of your data, not just the row key.

### Running locally

You can run the pipeline logic locally with an Avro file that's not too big by executing:

``` 
python -m template.avro_transform --input /path/to/avroFile  --output /path/to/out/avroFile
```

### Deploy the pipeline

You'll need a Google Storage Bucket to deploy and use the pipeline in Google Dataflow. Assuming your bucket
is called `bigtable-transform` the deploy command looks like this:

```
python -m template.avro_transform \
    --runner DataflowRunner \
    --staging_location gs://bigtable-transform/staging \ 
    --temp_location gs://bigtable-transform/tmp \
    --template_location gs://bigtable-transform/templates/avro_transform 
    --project usc-api-199318 
```

Additionally you have to place the metadata file in the template directory:

```
gsutil cp ./template/avro_transform_metadata gs://bigtable-transform/templates/avro_transform_metadata
```

Now you can select your template in Google Dataflow via Create job from template > Custom template and 
pointing to the template file `bigtable-transform/templates/avro_transform` in your Cloud Storage.