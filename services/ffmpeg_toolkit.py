import os
import ffmpeg
import requests
import re
import math
from subprocess import check_call, PIPE, Popen
import shlex

from file_management import download_file

# Set the default local storage directory
STORAGE_PATH = "/tmp/"

def process_conversion(media_url, job_id, bitrate='128k', webhook_url=None):
    """Convert media to MP3 format with specified bitrate."""
    input_filename = download_file(media_url, os.path.join(STORAGE_PATH, f"{job_id}_input"))
    output_filename = f"{job_id}.mp3"
    output_path = os.path.join(STORAGE_PATH, output_filename)

    try:
        # Convert media file to MP3 with specified bitrate
        (
            ffmpeg
            .input(input_filename)
            .output(output_path, acodec='libmp3lame', audio_bitrate=bitrate)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        os.remove(input_filename)
        print(f"Conversion successful: {output_path} with bitrate {bitrate}")

        # Ensure the output file exists locally before attempting upload
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after conversion.")

        return output_path

    except Exception as e:
        print(f"Conversion failed: {str(e)}")
        raise

def process_video_combination(media_urls, job_id, webhook_url=None):
    """Combine multiple videos into one."""
    input_files = []
    output_filename = f"{job_id}.mp4"
    output_path = os.path.join(STORAGE_PATH, output_filename)

    try:
        # Download all media files
        for i, media_item in enumerate(media_urls):
            url = media_item['video_url']
            input_filename = download_file(url, os.path.join(STORAGE_PATH, f"{job_id}_input_{i}"))
            input_files.append(input_filename)

        # Generate an absolute path concat list file for FFmpeg
        concat_file_path = os.path.join(STORAGE_PATH, f"{job_id}_concat_list.txt")
        with open(concat_file_path, 'w') as concat_file:
            for input_file in input_files:
                # Write absolute paths to the concat list
                concat_file.write(f"file '{os.path.abspath(input_file)}'\n")

        # Use the concat demuxer to concatenate the videos
        (
            ffmpeg.input(concat_file_path, format='concat', safe=0).
                output(output_path, c='copy').
                run(overwrite_output=True)
        )

        # Clean up input files
        for f in input_files:
            os.remove(f)
            
        os.remove(concat_file_path)  # Remove the concat list file after the operation

        print(f"Video combination successful: {output_path}")

        # Check if the output file exists locally before upload
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after combination.")

        return output_path
    except Exception as e:
        print(f"Video combination failed: {str(e)}")
        raise 




re_metadata = re.compile('Duration: (\d{2}):(\d{2}):(\d{2})\.\d+,.*\n.* (\d+(\.\d+)?) fps')

def get_metadata(filename):
    '''
    Get video metadata using ffmpeg
    '''
    p1 = Popen(["ffmpeg", "-hide_banner", "-i", filename], stderr=PIPE, universal_newlines=True)
    output = p1.communicate()[1]
    matches = re_metadata.search(output)
    if matches:
        video_length = int(matches.group(1)) * 3600 + int(matches.group(2)) * 60 + int(matches.group(3))
        video_fps = float(matches.group(4))
        # print('video_length = {}\nvideo_fps = {}'.format(video_length, video_fps))
    else:
        raise Exception("Can't parse required metadata")
    return video_length, video_fps

def process_split_cut(media_url, n, job_id, by='size'):
    '''
    Split video by cutting and re-encoding: accurate but very slow
    Adding "-c copy" speed up the process but causes imprecise chunk durations
    Reference: https://stackoverflow.com/a/28884437/1862500
    '''
    assert n > 0
    assert by in ['size', 'count']
    split_size = n if by == 'size' else None
    split_count = n if by == 'count' else None

    # input_filename = download_file(media_url, os.path.join(STORAGE_PATH, f"{job_id}_input"))
    input_filename = media_url
    print(input_filename)
    # parse meta data
    video_length, video_fps = get_metadata(input_filename)

    # calculate split_count
    if split_size:
        split_count = math.ceil(video_length / split_size)
        if split_count == 1:        
            raise Exception("Video length is less than the target split_size.")    
    else: #split_count
        split_size = round(video_length / split_count)

    print("process_split_cut")
    print("input_filename: ", input_filename)
    print("split_size: ", split_size)
    print("split_count: ", split_count)

    output = []
    for i in range(split_count):
        split_start = split_size * i
        pth, ext = input_filename.rsplit(".", 1)
        output_path = '{}-{}.{}'.format(pth, i+1, ext)
        cmd = 'ffmpeg -hide_banner -loglevel panic -ss {} -t {} -i "{}" -y "{}"'.format(
            split_start, 
            split_size, 
            filename, 
            output_path
        )
        # print(cmd)
        check_call(shlex.split(cmd), universal_newlines=True)
        output.append(output_path)
    
    return output


'''
https://yohanes.gultom.id/2020/04/03/splitting-video-with-ffmpeg-and-python/
'''
def process_split_segment(filename, n, by='size'):
    '''
    Split video using segment: very fast but sometimes innacurate
    Reference https://medium.com/@taylorjdawson/splitting-a-video-with-ffmpeg-the-great-mystical-magical-video-tool-%EF%B8%8F-1b31385221bd
    '''
    assert n > 0
    assert by in ['size', 'count']
    split_size = n if by == 'size' else None
    split_count = n if by == 'count' else None
    
    # parse meta data
    video_length, video_fps = get_metadata(filename)

    # calculate split_count
    if split_size:
        split_count = math.ceil(video_length / split_size)
        if split_count == 1:        
            raise Exception("Video length is less than the target split_size.")    
    else: #split_count
        split_size = round(video_length / split_count)

    pth, ext = filename.rsplit(".", 1)
    cmd = 'ffmpeg -hide_banner -loglevel panic -i "{}" -c copy -map 0 -segment_time {} -reset_timestamps 1 -g {} -sc_threshold 0 -force_key_frames "expr:gte(t,n_forced*{})" -f segment -y "{}-%d.{}"'.format(filename, split_size, round(split_size*video_fps), split_size, pth, ext)
    check_call(shlex.split(cmd), universal_newlines=True)

    # return list of output (index start from 0)
    return ['{}-{}.{}'.format(pth, i, ext) for i in range(split_count)]



