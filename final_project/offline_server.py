import time
import numpy as np
import imageio
import cv2
import flask
from ultralytics import YOLO
app = flask.Flask("AXC")

device = "cpu"

# Load YOLO model with CUDA support
model = YOLO("yolo11n.pt")  # Specify 'cuda' to use GPU
model.to(device)

MESSAGES = []
@app.route("/")
def home():
    return "active", 200
@app.route("/uploadvideo", methods=['POST'])
def main():
    file = flask.request.files['files']
    file.save("input.mp4") # noqa, like a BIG NOQA
    
    cap = cv2.VideoCapture("input.mp4")
    
    # Get video properties
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Initialize video writer using imageio
    writer = imageio.get_writer('output.mp4', fps=fps)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("End of video or error reading frame.")
            break
    
        # Perform detection
        results = model(frame)
    
        # Process detections
        points = []
        for result in results:
            boxes = result.boxes.xyxy
            confidences = result.boxes.conf
            class_ids = result.boxes.cls
    
            for i in range(len(boxes)):
                if confidences[i] > 0.5 and class_ids[i] == 0:
                    center_x = int((boxes[i][0] + boxes[i][2]) / 2)
                    center_y = int((boxes[i][1] + boxes[i][3]) / 2)
                    points.append((center_x, center_y))
    
        # Create a density map
        scale_factor = 0.1
        scaled_points = [(int(x * scale_factor), int(y * scale_factor)) for x, y in points]
        density_map = np.zeros((int(height * scale_factor), int(width * scale_factor)), dtype=np.float32)
        for point in scaled_points:
            if 0 <= point[0] < density_map.shape[1] and 0 <= point[1] < density_map.shape[0]:
                density_map[point[1], point[0]] += 1
    
        st = time.time()
    
        small_kernel_size = int(500 * scale_factor) 
        small_kernel_size = small_kernel_size if small_kernel_size % 2 == 1 else small_kernel_size + 1 
        blurred_small = cv2.GaussianBlur(density_map, (small_kernel_size, small_kernel_size), 0)
    
        density_map = cv2.resize(blurred_small, (width, height), interpolation=cv2.INTER_LINEAR)
    
        print(f"Processing time: {time.time() - st:.4f} seconds")
    
        # Normalize the density map for visualization
        density_map = cv2.normalize(density_map, None, 255, 0, cv2.NORM_MINMAX)
        density_map = np.array(density_map, dtype=np.uint8)
    
    
        density_map = cv2.bitwise_not(density_map)
        
        # Create a color map for the density map
        color_density_map = cv2.applyColorMap(density_map, cv2.COLORMAP_JET)

        # Overlay the density map on the original frame
        overlay = cv2.addWeighted(frame, 0.7, color_density_map, 0.3, 0)
    
        print(f"Overlay shape: {overlay.shape}, Data type: {overlay.dtype}")
    
        # Write the overlay frame to the output video
        writer.append_data(overlay)
    
    # Release resources
    cap.release()
    writer.close()
    print("Video saved as 'output.mp4'")
    return flask.send_file("output.mp4", as_attachment=True)
@app.route("/uploadimagejpeg", methods=["POST"])
def upload_image():
    file = flask.request.files['files']
    file.save("input.jpeg")
    frame = cv2.imread("input.jpeg")
    
    height, width, _ = frame.shape
    
    results = model(frame)
    
    points = []
    for result in results:
        boxes = result.boxes.xyxy
        confidences = result.boxes.conf
        class_ids = result.boxes.cls

        for i in range(len(boxes)):
            if confidences[i] > 0.5 and class_ids[i] == 0:
                center_x = int((boxes[i][0] + boxes[i][2]) / 2)
                center_y = int((boxes[i][1] + boxes[i][3]) / 2)
                points.append((center_x, center_y))
    # Create a density map
    scale_factor = 0.1
    scaled_points = [(int(x * scale_factor), int(y * scale_factor)) for x, y in points]
    density_map = np.zeros((int(height * scale_factor), int(width * scale_factor)), dtype=np.float32)
    for point in scaled_points:
        if 0 <= point[0] < density_map.shape[1] and 0 <= point[1] < density_map.shape[0]:
            density_map[point[1], point[0]] += 1

    st = time.time()

    small_kernel_size = int(200 * scale_factor) 
    small_kernel_size = small_kernel_size if small_kernel_size % 2 == 1 else small_kernel_size + 1 
    blurred_small = cv2.GaussianBlur(density_map, (small_kernel_size, small_kernel_size), 0)

    density_map = cv2.resize(blurred_small, (width, height), interpolation=cv2.INTER_LINEAR)

    print(f"Processing time: {time.time() - st:.4f} seconds")

    # Normalize the density map for visualization
    density_map = cv2.normalize(density_map, None, 255, 0, cv2.NORM_MINMAX)
    density_map = np.array(density_map, dtype=np.uint8)

    density_map = cv2.bitwise_not(density_map)

    # Create a color map for the density map
    color_density_map = cv2.applyColorMap(density_map, cv2.COLORMAP_JET)

    cv2.imwrite("output.jpeg", color_density_map)
    return flask.send_file("output.jpeg", as_attachment=True)

app.run(port=8080)