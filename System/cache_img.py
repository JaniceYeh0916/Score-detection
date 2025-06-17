import cv2
import os
import time

def take_photos_phone():
    save_dir = "./img_ori"
    os.makedirs(save_dir, exist_ok=True)
    
    phone_camera_url = "http://10.22.142.32:8080/video"
    camera = cv2.VideoCapture(phone_camera_url)
    
    if not camera.isOpened():
        print("Cannot open the camera!")
        exit()

    image_index = 0
    total_photos = 10
    interval = 10

    print(f"Take a photo every {interval} seconds, total {total_photos} photos.")
    start_time = time.time()

    while image_index < total_photos:
        ret, frame = camera.read()
        if not ret:
            print("Cannot capture the frame from camera!")
            break

        elapsed_time = time.time() - start_time
        remaining_time = max(0, interval - int(elapsed_time))

        display_text = f"Next photo in: {remaining_time} seconds"
        display_frame = frame.copy()
        cv2.putText(display_frame, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Camera Stream", display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Manual termination.")
            break

        if elapsed_time >= interval:
            image_path = os.path.join(save_dir, f"photo_{image_index:03d}.png")
            cv2.imwrite(image_path, frame)
            print(f"Captured photo {image_index}: {image_path}")
            image_index += 1
            start_time = time.time()

    print("Photo capturing finished.")
    camera.release()
    cv2.destroyAllWindows()


def take_photos():
    save_dir = "./img_ori"
    os.makedirs(save_dir, exist_ok=True)

    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Cannot open the camera!")
        exit()

    image_index = 0
    total_photos = 10
    interval = 10

    print(f"Take a photo every {interval} seconds, total {total_photos} photos.")
    start_time = time.time()

    while image_index < total_photos:
        ret, frame = camera.read()
        if not ret:
            print("Cannot capture the frame from camera!")
            break

        elapsed_time = time.time() - start_time
        remaining_time = max(0, interval - int(elapsed_time))

        display_text = f"Next photo in: {remaining_time} seconds"
        display_frame = frame.copy()
        cv2.putText(display_frame, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Camera Stream", display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Manual termination.")
            break

        if elapsed_time >= interval:
            image_path = os.path.join(save_dir, f"photo_{image_index:03d}.png")
            cv2.imwrite(image_path, frame)
            print(f"Captured photo {image_index}: {image_path}")
            image_index += 1
            start_time = time.time()

    print("Photo capturing finished.")
    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    take_photos()
