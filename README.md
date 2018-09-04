# elastictranscoder_lambda
elastictranscoder_lambda on python

# Procedure

1. Create two S3 buckets. One is shiwang-et-input, the other one is shiwang-et-output. Create origin folder in shiwang-et-input. Create new & thumbernail folder in shiwang-et-output.

2. Create IAM policy - shiwang-et-policy

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "1",
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": [
                "arn:aws:s3:::shiwang-et-input/*",
                "arn:aws:s3:::shiwang-et-output/*"
            ]
        },
        {
            "Sid": "2",
            "Effect": "Allow",
            "Action": "ses:SendEmail",
            "Resource": "*"
        },
        {
            "Sid": "3",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Sid": "4",
            "Effect": "Allow",
            "Action": "elastictranscoder:CreateJob",
            "Resource": "*"
        }
    ]
}
3. Create IAM role using this policy - shiwang-et-role.

4. Create elastic transcoder pipeline - shiwang-et-pipeline and remember the pipeline ID

Input bucket: shiwang-et-input
Output bucket: shiwang-et-output
Thumbnail bucket: shiwang-et-output
SNS notifications: create a new one

5. Create lambda function - shiwang-et-lambda, setup S3 as trigger, 
Bucket: shiwang-et-input 
Event type: ObjectCreated
Prefix: origin 

6. Copy the following code

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

7. Save lambda configuration

8. Upload unconverted MP4 file to shiwang-et-input/origin 





