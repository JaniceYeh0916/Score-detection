import re
import os
from ultralytics import YOLO
import logging
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import numpy as np
from scipy.ndimage import binary_dilation
import cv2


def digital_detection():
    logging.getLogger("ultralytics").setLevel(logging.ERROR)
    model = YOLO("../model/Score_detection/best.pt")

    folder_path = "./img_label/score"
    image_files = [folder_path + "/" + f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg'))]
    if not image_files:
        print("No score image files have been detected.")
        return -1
    image_files.sort(key=lambda x: int(os.path.basename(x).split('.')[0]))

    folder_path_ori = "./img_ori"
    file_count = len([f for f in os.listdir(folder_path_ori) if os.path.isfile(os.path.join(folder_path_ori, f))])

    score_list = []
    for i in range(file_count):
        count = 0
        image_file = folder_path + f"/{i}_0.png"
        while True:
            if os.path.exists(image_file):

                result = model(image_file)

                boxes = result[0].boxes
                area = []
                digit = []
                # result.save(filename=f"result{i+1}.jpg")

                for j in range(len(boxes)):
                    conf = boxes[j].conf.tolist()[0]
                    if conf < 0.4:
                        continue
                    tmp = boxes[j].xyxy.tolist()[0]
                    area.append(tmp)
                    tmp2 = boxes[j].cls.tolist()[0]
                    digit.append(tmp2)
                    
                
                if digit != []:
                    combined = list(zip(area, digit))
                    sorted_combined = sorted(combined, key=lambda x: x[0][0])
                    sorted_area, sorted_digit = zip(*sorted_combined)
                    sorted_digit = list(sorted_digit)
                    sorted_area = list(sorted_area)

                    image = Image.open(image_file)
                    width, _ = image.size
                    cut = width // 16

                    count = 0
                    for j in range(len(sorted_area) - 1):
                        if (sorted_area[j-count][0] - cut < sorted_area[j-count + 1][0] < sorted_area[j-count][0] + cut) or (sorted_area[j-count][2] - cut < sorted_area[j-count + 1][2] < sorted_area[j-count][2] + cut):
                            if sorted_digit[j-count] == sorted_digit[j-count + 1]:
                                del sorted_area[j]
                                del sorted_digit[j]
                                count = count + 1

                    convert_list = ["+", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
                    digit = [convert_list[int(j)] for j in sorted_digit]

                    formula = "".join(digit)

                    score = input_expression(formula)
                    score_list.append(score)
                else:
                    count += 1
                    image_file = folder_path + f"/{i}_{count}.png"
                    continue
                    # score_list.append(-1)
            else:
                score_list.append(-1)

            break

    return score_list


def convert_expression(expression):
    '''情況1: "87+2" -> 89'''
    pattern = r'(\d{1,3})([\+-])(\d{1,2})'  # [1-3位數字][+or-][1-2位數字]
    match = re.match(pattern, expression)  # 進行匹配
    if match:  # 如果匹配成功
        num1, operator, num2 = match.groups()
        num1, num2 = int(num1), int(num2)
        if operator == '+':
            return num1 + num2
        elif operator == '-':
            return num1 - num2

    else:
        '''情況2: "99" -> 99'''
        pattern = r'(\d{1,3})'  # [1-3位數字]
        match = re.match(pattern, expression)
        if match:
            return int(match.group(1))
        else:
            # return "Invalid format"
            return -1


def input_expression(result):
    converted_result = convert_expression(result)
    # print(f"Score = {converted_result}")
    return converted_result


def hsv(path):
    image = cv2.imread(path)

    # 將圖片轉換為 HSV 色彩空間
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 定義紅色範圍（紅色可能分佈在兩個範圍內）
    lower_red1 = np.array([0, 30, 30])
    upper_red1 = np.array([20, 255, 255])
    lower_red2 = np.array([165, 40, 40])
    upper_red2 = np.array([180, 255, 255])

    # 創建遮罩
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # 保留紅色部分
    result = cv2.bitwise_and(image, image, mask=mask)

    # 將其他部分變為白色
    white_background = np.full_like(image, 255)
    final_image = np.where(result == 0, white_background, result)
    
    # bgr = cv2.cvtColor(final_image, cv2.COLOR_HSV2BGR)
    # rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    
    filename = "./img_label/score/hsv/" + path.split("/")[-1]
    cv2.imwrite(filename, final_image)

    return filename


def rgb(path):
    image = Image.open(path).convert('RGB')
    image = image.resize((image.width, int(image.height*1.5//1)))

    pixels = image.load()
    for i in range(image.width):
        for j in range(image.height):
            r, g, b = pixels[i, j]
            # 如果是黑色像素 (r, g, b = 0, 0, 0)
            if r < 50 and (r - g) < 1 and (r - b) < 1:
                pixels[i, j] = (255, 255, 255)  # 轉換為白色

    gray_image = image.convert('L')

    enhancer = ImageEnhance.Brightness(gray_image)
    bright_image = enhancer.enhance(1.3)  # 增強亮度，1.5 是增強程度

    # 增強顏色
    enhancer = ImageEnhance.Color(bright_image)
    color_image = enhancer.enhance(2.0)  # 增強顏色飽和度

    # 增強對比度
    enhancer = ImageEnhance.Contrast(color_image)
    contrast_image = enhancer.enhance(2)  # 增強對比度

    # 增強銳度
    enhancer = ImageEnhance.Sharpness(contrast_image)
    sharp_image = enhancer.enhance(2.0)  # 增強銳度

    expanded_image = ImageOps.expand(sharp_image, border=50, fill='white')

    expanded_image = expanded_image.convert('1')

    binary_array = np.array(expanded_image) == 0  # 黑色為 True (前景)
    structure = np.ones((3, 3), dtype=bool)
    dilated_image = binary_dilation(binary_array, structure=structure)

    inverted_array = ~dilated_image
    final_image = Image.fromarray((inverted_array * 255).astype(np.uint8))

    filename = "./img_label/score/rgb/" + path.split("/")[-1]
    final_image.save(filename)
    
    return filename 

if __name__ == '__main__':
    score_list = digital_detection()
    print(score_list)
