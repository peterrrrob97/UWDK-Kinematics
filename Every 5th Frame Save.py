import cv2
import os

def save_every_5th_frame(video_path, output_folder):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if the video file is opened successfully
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get the frames per second (fps) of the video
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Initialize frame count
    frame_count = 0

    while True:
        # Read a frame from the video
        ret, frame = cap.read()

        # Break the loop if the video is finished
        if not ret:
            break

        # Increment the frame count
        frame_count += 1

        # Save every 5th frame
        if frame_count % 5 == 0:
            # Construct the output file name starting at '0231'
            output_file = os.path.join(output_folder, f"frame_{frame_count + 230}.jpg")

            # Save the frame as an image
            cv2.imwrite(output_file, frame)

            print(f"Saved: {output_file}")

    # Release the video capture object
    cap.release()

if __name__ == "__main__":
    # Replace 'your_video_path' with the path to your video file
    video_path = ('D:\\yolov8-gpu\\UWDK_Pose\\UWDK_Videos\\18.mp4')

    # Replace 'output_folder' with the folder where you want to save the frames
    output_folder = 'D:\\yolov8-gpu\\UWDK_Pose\\Data'

    # Call the function to save every 5th frame
    save_every_5th_frame(video_path, output_folder)