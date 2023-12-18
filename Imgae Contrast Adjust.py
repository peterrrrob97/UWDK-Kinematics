from PIL import Image, ImageEnhance
import os

def increase_contrast(input_dir, output_dir, factor=1.5):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            image = Image.open(input_path)
            enhanced_image = ImageEnhance.Contrast(image).enhance(factor)
            enhanced_image.save(output_path)

if __name__ == "__main__":
    input_directory = "D:\\yolov8-gpu\\UWDK_Pose\\Data"
    output_directory = "D:\\yolov8-gpu\\UWDK_Pose\\High Contrast Data"
    contrast_factor = 1.5

    increase_contrast(input_directory, output_directory, contrast_factor)