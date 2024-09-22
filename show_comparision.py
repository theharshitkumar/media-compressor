import os
import tkinter as tk
from tkinter import Label, Canvas, Scrollbar, Frame
from PIL import Image, ImageTk
import cv2

# Paths
input_folder = 'input'
log_file = 'compression_results.txt'

# Load log data
def load_log_data():
    data = {}
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split(', ')
                filename = parts[0]
                info = parts[1:]
                data[filename] = info
    return data

# Create a Tkinter window
class CompareApp:
    def __init__(self, root, image_file, video_file, log_data):
        self.root = root
        self.image_file = image_file
        self.video_file = video_file
        self.log_data = log_data

        self.root.title("Visual Comparison")

        self.frame = Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas for displaying the image and video
        self.canvas = Canvas(self.frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar
        self.scrollbar = Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", self.on_frame_configure)

        # Load and display image and video
        self.display_comparison()

    def display_comparison(self):
        # Load image
        image_path = os.path.join(input_folder, self.image_file)
        image = Image.open(image_path)
        image = image.resize((300, 300))  # Resize image for display
        self.image_photo = ImageTk.PhotoImage(image)

        # Display image
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_photo)
        self.canvas.create_text(150, 20, text=f"Image: {self.image_file}", fill="black")

        # Load video
        video_path = os.path.join(input_folder, self.video_file)
        video_cap = cv2.VideoCapture(video_path)
        self.video_frames = []
        while True:
            ret, frame = video_cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.video_frames.append(Image.fromarray(frame))
        video_cap.release()

        # Display video
        self.update_video(0)

        # Display log info
        self.display_log_info()

    def update_video(self, frame_idx):
        if frame_idx < len(self.video_frames):
            video_image = self.video_frames[frame_idx]
            video_image = video_image.resize((300, 300))  # Resize video frame for display
            self.video_photo = ImageTk.PhotoImage(video_image)
            self.canvas.create_image(320, 0, anchor=tk.NW, image=self.video_photo)
            self.canvas.create_text(470, 20, text=f"Video: {self.video_file}", fill="black")
            self.root.after(100, self.update_video, (frame_idx + 1) % len(self.video_frames))

    def display_log_info(self):
        if self.image_file in self.log_data:
            info = self.log_data[self.image_file]
            info_text = "\n".join(info)
            self.canvas.create_text(150, 340, text=info_text, fill="black", anchor=tk.NW)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

# Main execution
if __name__ == '__main__':
    log_data = load_log_data()
    root = tk.Tk()

    # Example files; replace these with actual filenames from your dataset
    image_file = 'example_image.jpg'  # Replace with actual image file name
    video_file = 'example_video.mp4'  # Replace with actual video file name

    app = CompareApp(root, image_file, video_file, log_data)
    root.mainloop()
