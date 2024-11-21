from flask import Blueprint, jsonify
from app_utils import *
import logging
from services.ffmpeg_toolkit import process_split_cut
from services.authentication import authenticate
from services.cloud_storage import upload_file

combine_bp = Blueprint('split', __name__)
logger = logging.getLogger(__name__)

@combine_bp.route('/split-video', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_url": {"type": "string", "format": "uri"},
        "split_length": {"type": "string"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["video_url", "start_time", "end_time"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def split_video(job_id, data):
    media_url = data['video_url']
    split_length = data['split_length']
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Job {job_id}: Received split-video request for {media_url} videos")

    try:
        output_files = process_split_cut(media_url, split_length, job_id)
        logger.info(f"Job {job_id}: Video splitting process completed successfully")

        cloud_urls = []
        for filepath in output_files:
            cloud_url = upload_file(filepath)
            logger.info(f"Job {job_id}: Video segment uploaded to cloud storage: {cloud_url}")
            cloud_urls.append(cloud_url)

        data = {
            "urls": cloud_urls
        }
        return jsonify(data), "/split-video", 200


    except Exception as e:
        logger.error(f"Job {job_id}: Error during video splitting process - {str(e)}")
        return str(e), "/split-video", 500