from flask import Flask, jsonify, request
from flask_restx import Resource, Api
from dotenv import load_dotenv

from moviepy.editor import *

import boto3


load_dotenv(verbose=True)


# s3 영상 업로드
def upload_file_to_s3(file_path, username, title):
    bucket = BUCKET_NAME
    location = S3_LOCATION
    s3_client = boto3.client(
        's3',
        aws_access_key_id = ACCESS_KEY,
        aws_secret_access_key = SECRET_KEY
    )
    path = f'/user/{username}/{title}/{title}.mp4'

    try:
        s3_client.upload_file(file_path, bucket, path)
    except:
        return False
    return f'https://{bucket}.s3.{location}.amazonaws.com/{path}'


# flask
app = Flask(__name__)
api = Api(app, version='0.1.0', title="픽북, 용수철 팀, 2023 코너톤")
app.config['DEBUG'] = True
app.config['JSON_AS_ASCII'] = False     # 한글 깨짐 방지


@api.route('/api/videoEdit')
class videoEditAPI(Resource):
    def post(self):
        title = request.json.get('title')
        username = request.json.get('nickname')
        photos = request.json.get('photos')
        music = request.json.get('music')
        lengths = request.json.get('lengths')

        clips = [VideoFileClip(i).set_duration(float(l)) for i, l in zip(photos, lengths)]
        audio = AudioFileClip(music).fx(afx.audio_fadeout, 1)
        width = clips[0].w

        FINAL_PATH = BASIC_PATH + title + ".mp4"

        final_clip = concatenate_videoclips(clips)
        final_clip.audio = CompositeAudioClip([audio])
        final_clip.rotate(-90).resize(width=width).write_videofile(FINAL_PATH)

        video_s3_address = upload_file_to_s3(FINAL_PATH, username, title)
        return jsonify({ "success": True, 'video': video_s3_address })


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
