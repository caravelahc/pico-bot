from pathlib import Path
from typing import NamedTuple
import ffmpeg

class NoVideoStreamError(Exception):
    pass

class VideoTooLongError(Exception):
    pass


def sticker_from_video(video_path: Path, circle_mask: Path = None) -> Path:
    '''
    Converts the given video to a proper format that can be uploaded as a sticker.
    Telegram accepts WEBM VP9 with a maximum size of 512x512 pixels with maximum 3 seconds duration.
    '''
    probe = ffmpeg.probe(video_path)
    video_stream = next(
        (stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None
    )
    if video_stream is None:
        raise NoVideoStreamError('Video stream not found')

    width = int(video_stream['width'])
    height = int(video_stream['height'])
    duration = float(probe['format']['duration'])

    if duration > 3.0:
        raise VideoTooLongError('Video duration exceeds limits')

    width, height = estimate_video_sticker_size(VideoSize(width, height))
    vid_output_path = video_path.with_suffix('.webm')
    in_file = ffmpeg.input(video_path).filter('scale', width, height)
    if circle_mask is None:
        in_file.output(
            filename=vid_output_path.as_posix(),
            format='webm',
            vcodec='libvpx-vp9',
            pix_fmt='yuva420p',
        ).run(overwrite_output=True)
    else:
        mask = ffmpeg.input(circle_mask).filter('alphaextract')
        ffmpeg.filter((in_file, mask), 'alphamerge',).output(
            filename=vid_output_path.as_posix(),
            format='webm',
            vcodec='libvpx-vp9',
            pix_fmt='yuva420p',
        ).run(overwrite_output=True)
    return vid_output_path

class VideoSize(NamedTuple):
    width: int
    height: int

def estimate_video_sticker_size(candidate_size: VideoSize) -> VideoSize:
    '''
    Estimates the frame size to fit Telegram restrictions (maximum size of 512x512 pixels), keeping its aspect ratio.
    '''
    if candidate_size.width >= candidate_size.height:
        ratio = 512 / candidate_size.width
        return VideoSize(512, int(ratio * candidate_size.height))
    else:
        ratio = 512 / candidate_size.height
        return VideoSize(int(ratio * candidate_size.width), 512)
