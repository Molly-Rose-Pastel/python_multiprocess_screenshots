import multiprocessing as mp
import time
import sys, os
import d3dshot
from PIL import Image

target_fps = 144
runtime_s = 1
frame_amount = runtime_s*target_fps    
process_start_delay = 1/target_fps    

def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__

def take_screenshot():   
    # d3dshot is a singleton so only 1 instance per process
    # it will print this information when we try to create  
    # so we block this to not spam the console
    blockPrint() 
    d = d3dshot.create("numpy")
    enablePrint()

    retval = {}
    retval[time.time()] = d.screenshot()
    return retval


if __name__ == "__main__":   

    # create process pool, one for each available cpu core
    pool = mp.Pool(mp.cpu_count())
    res_dump = []

    # start taking screenshot
    start = time.time()    
    for x in range(frame_amount):
        res_dump.append(pool.apply_async(take_screenshot))        
        time.sleep(process_start_delay)
    
    pool.close()
    pool.join()    
    finish = time.time()

    # merge the dictionaries from the processes into one 
    all_data = {}
    for dictionary in res_dump:
        all_data.update(dictionary.get())
    
    # update the timestamps by subtracting them from the finish time
    relative_data = {}
    for key in all_data:
        new_key = finish - key
        relative_data[new_key] = all_data[key]

    # sort them by key, which is the timestamp
    dictionary_items = relative_data.items()
    sorted_items = sorted(dictionary_items)

    # save images to disk, using the timestamp as part of the name
    counter = 1
    for tuple_item in sorted_items:
        key = tuple_item[0]
        timestamp = str(key)
        img = Image.fromarray(relative_data[key])
        output = "./images_d3d/" + str(counter) + "_" + timestamp +".png"
        img.save(output)
        counter += 1