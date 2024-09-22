import os
import time
import concurrent.futures
from PIL import Image
import ffmpeg
from tqdm import tqdm  # For progress bar

input_folder = "input"
output_folder = "output"
log_file = "compression_results.txt"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)


# Helper functions
def compress_image(input_image_path, output_image_path):
    """Compress image using Pillow with format conversion and lossy compression"""
    start_time = time.time()

    with Image.open(input_image_path) as img:
        # Convert to WebP if not already a lossy format
        if input_image_path.lower().endswith((".png", ".tiff")):
            img = img.convert("RGB")  # Convert to RGB before saving as WebP
            img.save(output_image_path, "WEBP", quality=70)  # Adjust quality as needed
        else:
            img.save(output_image_path, optimize=True, quality=70)  # For JPEG, etc.

    end_time = time.time()

    input_size = os.path.getsize(input_image_path)
    output_size = os.path.getsize(output_image_path)

    # Overwrite output file with input file if the input file is smaller
    if input_size < output_size:
        os.replace(input_image_path, output_image_path)

    return (
        input_size,
        os.path.getsize(output_image_path),
        end_time - start_time,
    )


def compress_video(input_video_path, output_video_path):
    """Compress video using GPU-accelerated NVENC with advanced settings"""
    start_time = time.time()

    try:
        # Using GPU acceleration with ffmpeg's NVENC encoder (h264_nvenc or hevc_nvenc)
        (
            ffmpeg.input(input_video_path)
            .output(
                output_video_path,
                vcodec="hevc_nvenc",  # Use HEVC for better compression
                preset="slow",  # Better quality, longer encoding time
                crf=30,  # Lower CRF for better quality
                maxrate="2M",  # Maximum bitrate
                bufsize="4M",  # Buffer size
                b="1500k",  # Average bitrate
            )
            .run(quiet=True)  # Set quiet to False to see full output
        )
    except ffmpeg.Error as e:
        print("FFmpeg failed:")
        print(e.stderr.decode("utf-8"))  # Print the stderr output for debugging
        raise e  # Re-raise the exception to stop execution if necessary

    end_time = time.time()

    input_size = os.path.getsize(input_video_path)
    output_size = os.path.getsize(output_video_path)

    # Overwrite output file with input file if the input file is smaller
    if input_size < output_size:
        os.replace(input_video_path, output_video_path)

    return (
        input_size,
        os.path.getsize(output_video_path),
        end_time - start_time,
    )


def log_results(filename, before_size, after_size, time_taken):
    """Log the compression results to a text file"""
    compression_percentage = (
        100 * (before_size - after_size) / before_size if before_size else 0
    )
    with open(log_file, "a") as f:
        f.write(
            f"{filename}, Time: {time_taken:.2f}s, Before: {before_size/1024/1024} MB, After: {after_size/1024/1024} MB, Compression: {compression_percentage:.2f}%\n"
        )


def process_file(file):
    """Process individual files (image or video)"""
    input_path = os.path.join(input_folder, file)
    output_path = os.path.join(output_folder, file)

    if file.lower().endswith((".png", ".jpg", ".jpeg", ".tiff")):
        before_size, after_size, time_taken = compress_image(input_path, output_path)
    elif file.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
        before_size, after_size, time_taken = compress_video(input_path, output_path)
    else:
        return  # Skip files that are not images or videos

    log_results(file, before_size, after_size, time_taken)


# Main execution
if __name__ == "__main__":
    # Clear log file
    open(log_file, "w").close()

    # Get all files from input folder
    files = os.listdir(input_folder)

    with tqdm(total=len(files), desc="Compressing files", unit="file") as pbar:
        for file in files:
            process_file(file)
            pbar.update(1)

    # # Use ThreadPoolExecutor for parallel processing, leveraging 12 threads
    # with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
    #     # Create a progress bar
    #    . with tqdm(total=len(files), desc="Compressing files", unit="file") as pbar:
    #         # Map function to files with progress tracking
    #         futures = [executor.submit(process_file, file) for file in files]
    #         for future in concurrent.futures.as_completed(futures):
    #             pbar.update(1)
