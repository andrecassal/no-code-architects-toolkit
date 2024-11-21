from ffmpeg_toolkit import process_split_cut, get_metadata

metadata = get_metadata('maya.mp4')
print(metadata)

# outputs = process_split_cut('maya.mp4', 1, 51123)
# print("Done")
# print(outputs)