import os
import subprocess
import logging
# from services.file_management import download_file
from file_management import download_file
from PIL import Image

STORAGE_PATH = "/tmp/"
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def process_image_to_video(image_url, length, frame_rate, zoom_speed, job_id, webhook_url=None):
    try:
        # Download the image file
        image_path = download_file(image_url, STORAGE_PATH)
        logger.info(f"Downloaded image to {image_path}")

        # Get image dimensions using Pillow
        with Image.open(image_path) as img:
            width, height = img.size
        logger.info(f"Original image dimensions: {width}x{height}")

        # Prepare the output path
        output_path = os.path.join(STORAGE_PATH, f"{job_id}.mp4")

        # Determine orientation and set appropriate dimensions
        # s_width, s_height = 7680, 4320
        scale = 1.5
        s1_width, s1_height = 1080, 1920

        i_width, i_height = scale_to_cover(width, height, s1_width, s1_height)
        
        scale_dims = f"w={i_width}:h={i_height}"

        output_dims = f"{s1_width}:{s1_height}"



        # Calculate total frames and zoom factor
        total_frames = int(length * frame_rate)
        zoom_factor = (zoom_speed * length)


        logger.info(f"Using scale dimensions: {scale_dims}, output dimensions: {output_dims}")
        logger.info(f"Video length: {length}s, Frame rate: {frame_rate}fps, Total frames: {total_frames}")
        logger.info(f"Zoom speed: {zoom_speed}/s, Final zoom factor: {zoom_factor}")



        # Prepare FFmpeg command
        cmd = [
            'ffmpeg', 
            '-framerate', str(frame_rate), 
            '-loop', 
            '1', 
            '-i', 
            image_path,
            '-vf', 
            f"scale={scale_dims},crop={output_dims},pad={output_dims}:(( (ow - iw)/2 )):(( (oh - ih)/2 ))",
            # f"scale={scale_dims}",
            # f"scale={scale_dims},zoompan=z='max(1+{zoom_speed}*{total_frames}/on, {zoom_factor})':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={output_dims}",
            # f"scale={scale_dims},crop={output_dims},zoompan=z='1.5-on/duration*0.5':d=125:s={output_dims}",
            '-c:v', 
            'libx264', 
            '-t', 
            str(length), 
            '-pix_fmt', 
            'yuv420p', 
            output_path
        ]

        logger.info(f"Running FFmpeg command: {' '.join(cmd)}")

        # Run FFmpeg command
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"FFmpeg command failed. Error: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)

        logger.info(f"Video created successfully: {output_path}")

        # Clean up input file
        os.remove(image_path)

        return output_path
    except Exception as e:
        print("Error: ", str(e))
        logger.error(f"Error in process_image_to_video: {str(e)}", exc_info=True)
        raise





def scale_to_cover(input_width, input_height, target_width, target_height):
    """
    Scale width and height to cover within the target dimensions while maintaining aspect ratio.
    
    Args:
        input_width (int): The original width of the input.
        input_height (int): The original height of the input.
        target_width (int): The width of the target area.
        target_height (int): The height of the target area.
    
    Returns:
        tuple: A tuple containing the scaled width and height.
    """
    # Scale based on width and height independently
    scale_width = target_width / input_width
    scale_height = target_height / input_height

    # Use the smaller scale factor to ensure it fits within both dimensions
    scale_factor = max(scale_width, scale_height)

    # Calculate the scaled dimensions
    scaled_width = int(input_width * scale_factor)
    scaled_height = int(input_height * scale_factor)
    
    return scaled_width, scaled_height