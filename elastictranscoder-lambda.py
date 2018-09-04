import boto3
import json

# Set all these variables 
bucket_name = 'shiwang-et-input'
origin_prefix='origin'
new_prefix='new'
thumbnail_prefix='thumbnail'
pipeline_id='1535903746953-p94lxb' # use your pipeline_id instead

# Semi-constant stuff
preset_id='1351620000001-100010' # This is System Preset: MP4 H.264 Generic 720
region_name='us-east-1' # N.Virginia 

# While a file shows up in the origin bucket, starts Elastic Transcoder
def start_et_handler(event, context):

    print ("Processing start handler")

    try:
        if (event!=None and event.has_key('Records') and
            len(event.get('Records'))==1 and
            event.get('Records')[0].has_key('s3') and
            event.get('Records')[0].get('s3').has_key('object') and
            event.get('Records')[0].get('s3').get('object').has_key('key')):

            s3_object = event.get('Records')[0].get('s3').get('object')
            infile_key = s3_object.get('key')

            if (infile_key.startswith(unconverted_prefix)):
                outfile_key = converted_prefix+('.'.join(infile_key[len(unconverted_prefix):].split('.')[:-1]) + '.mp4')
                thumbnail_pattern = thumbnail_prefix+('.'.join(infile_key[len(unconverted_prefix):].split('.')[:-1]) + '-{count}')
                print("Starting processing on {0} to {1} thumbnail {2}", format(infile_key), format(outfile_key), format(thumbnail_pattern))
                start_transcode(infile_key,outfile_key,thumbnail_pattern)
                print("Started ok, subscribe to the SNS queue to find out when finished")
                return {'status' : 'ok'}
            else :
                return {'status' : 'ignored', 'message' : 'wrong path'}

        else :
            return {'status' : 'ignored', 'message':'Invalid input'}

    except Exception as exception:
        return {'status' : 'error',
                'message' : exception.message}


def start_transcode(in_file, out_file, thumbnail_pattern):
    """
    Submit a job to transcode a file by its filename. The
    built-in web system preset is used for the single output.
    """
    transcoder = boto3.client('elastictranscoder', region_name)
    transcoder.create_job(
            PipelineId=pipeline_id,
            Input={
                'Key': in_file,
                'FrameRate': 'auto',
                'Resolution': 'auto',
                'AspectRatio': 'auto',
                'Interlaced': 'auto',
                'Container': 'auto'
            },
            Outputs=[{
                'Key': out_file,
                #'ThumbnailPattern': thumbnail_pattern, turning this off for now
                'PresetId': preset_id
            }]
)