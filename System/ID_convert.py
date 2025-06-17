import cv2
import os
from ultralytics import YOLO
import logging


def id_detection():
    logging.getLogger("ultralytics").setLevel(logging.ERROR)
    model = YOLO("../model/ID_detection/best.pt")

    folder_path = "./img_label/id"
    image_files = [folder_path + "/" + f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg'))]
    image_files.sort(key=lambda x: int(os.path.basename(x).split('.')[0]))

    folder_path_ori = "./img_ori"
    file_count = len([f for f in os.listdir(folder_path_ori) if os.path.isfile(os.path.join(folder_path_ori, f))])

    id_list = []

    for i in range(file_count):
        if os.path.exists(folder_path + f"/{i}.png"):
            img_bgr = cv2.imread(folder_path + f"/{i}.png")
            resized_bgr = cv2.resize(img_bgr, (640, 640), interpolation=cv2.INTER_LINEAR)

            results = model(resized_bgr)

            res = results[0]
            boxes = res.boxes
            names = model.names

            detections = []
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]  # [x_min, y_min, x_max, y_max]
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                class_name = names[cls_id]

                x_min = float(x1)

                detections.append({
                    "cls_id": cls_id,
                    "class_name": class_name,
                    "conf": conf,
                    "x1": x_min,
                    "y1": float(y1),
                    "x2": float(x2),
                    "y2": float(y2),
                })

                detections_sorted = sorted(detections, key=lambda d: d["x1"])

                result = ""

                for det in detections_sorted:
                    if det['conf'] > 0.3:
                        result += det['class_name']

            id_list.append(result)
            # print(result)
        else:
            id_list.append("-1")
    return id_list


if __name__ == '__main__':
    id_list = id_detection()
    print(id_list)