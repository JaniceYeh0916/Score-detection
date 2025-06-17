import os
import cv2
from ultralytics import YOLO


def create_folder():
    folder_path = './img_label'
    folder_list = ["/id", "/name", "/score"]

    for i in range(3):
        path = folder_path + folder_list[i]
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"資料夾已創建：{path}")
        else:
            print(f"資料夾已存在：{path}")


def delete_images():
    folder_path = './img_label'
    folder_list = ["/id", "/name", "/score"]

    for i in range(3):
        path = folder_path + folder_list[i]
        if os.listdir(path):
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
    print(f'資料夾已清空'+"\n"+'開始進行分類')


def search_data():
    model = YOLO("../model/Classification/best.pt")

    create_folder()
    delete_images()

    folder_path = "./img_ori"
    image_files = [folder_path + "/" + f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg'))]

    results = model(image_files)

    for i, result in enumerate(results):

        boxes = result.boxes

        image = cv2.imread(image_files[i])

        last_acc = [0, 0, 0]

        if i in range(len(image_files)):

            count = 0
            image_all = []
            conf = []
            for j in range(len(boxes)):

                area = boxes[j].xyxy.tolist()[0]

                if boxes[j].cls == 2:
                    k = 25
                    area = [area[0] - k, area[1] - k, area[2] + k, area[3] + k]

                cropped_image = image[int(area[1]):int(area[3]), int(area[0]):int(area[2])]

                if boxes[j].cls == 0 and last_acc[0] < boxes[j].conf:
                    last_acc[0] = boxes[j].conf
                    cv2.imwrite(f'./img_label/id/{i}.png', cropped_image)
                elif boxes[j].cls == 1 and last_acc[1] < boxes[j].conf:
                    last_acc[1] = boxes[j].conf
                    cv2.imwrite(f'./img_label/name/{i}.png', cropped_image)
                elif boxes[j].cls == 2:
                    conf.append(boxes[j].conf)
                    image_all.append(cropped_image)
                    cv2.imwrite(f'./img_label/score/{i}_{count}.png', cropped_image)
                    count += 1
        
        result.save(filename=f"./img_label/result_{i}.jpg")
    
    print("Classification Finish!")


if __name__ == "__main__":
    search_data()
