from image_to_video import process_image_to_video
from file_management import download_file

# image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Mozart_Portrait_Croce.jpg/800px-Mozart_Portrait_Croce.jpg"
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Mozart_Family_Croce.jpg/1024px-Mozart_Family_Croce.jpg"

# image_path = download_file(image_url)
# print(image_path)
process_image_to_video(image_url,15,30,0.25,12345)

'''
w, h = 800, 1160

w1, h1 = 1080, 1920

if w > h:
    size = (None, h1)
else:
    size = (w1, None)

'''


# # Example usage
# input_w, input_h = 800, 1160
# target_w, target_h = 1080, 1920

# scaled_w, scaled_h = scale_to_fit(input_w, input_h, target_w, target_h)
# print(f"Scaled dimensions: {scaled_w}x{scaled_h}")