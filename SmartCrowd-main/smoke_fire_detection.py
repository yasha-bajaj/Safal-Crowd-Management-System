
import cv2
import numpy as np

class SmokeFireDetection:
    def __init__(self, model_path, config_path, classes_path):
        self.net = cv2.dnn.readNet(model_path, config_path)
        with open(classes_path, 'r') as f:
            self.classes = f.read().strip().split('\n')

    def detect(self, frame):
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        layer_outputs = self.net.forward(self.get_output_layers())

        boxes = []
        confidences = []
        class_ids = []

        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    box = detection[0:4] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
                    (centerX, centerY, width, height) = box.astype("int")
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        results = []
        if len(indices) > 0:
            for i in indices.flatten():
                x, y, w, h = boxes[i]
                results.append((x, y, w, h, self.classes[class_ids[i]], confidences[i]))

        return results

    def get_output_layers(self):
        layer_names = self.net.getLayerNames()
        return [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

# Example usage:
# detector = SmokeFireDetection('yolov3.weights', 'yolov3.cfg', 'coco.names')
# frame = cv2.imread('test_image.jpg')
# detections = detector.detect(frame)
# for (x, y, w, h, label, confidence) in detections:
#     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#     cv2.putText(frame, f"{label}: {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
# cv2.imshow('Frame', frame)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
