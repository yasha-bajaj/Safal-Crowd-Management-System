import cv2
import os

# Create 'people' directory if it doesn't exist
people_dir = 'people'
if not os.path.exists(people_dir):
    os.makedirs(people_dir)

# Initialize webcam
cap = cv2.VideoCapture(0)

print("Press 's' to save an image, 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow("Webcam", frame)

    key = cv2.waitKey(1)
    if key == ord('s'):
        # Save the image
        img_name = os.path.join(people_dir, "person_{}.jpg".format(len(os.listdir(people_dir)) + 1))
        cv2.imwrite(img_name, frame)
        print(f"Image saved as {img_name}")
    elif key == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()