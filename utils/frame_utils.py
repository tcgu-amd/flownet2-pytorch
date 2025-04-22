import numpy as np  
from os.path import *  
import imageio.v2 as imageio
from . import flow_utils  
  
def read_gen(file_name):  
    ext = splitext(file_name)[-1].lower()   
  
    if ext in ['.png', '.jpeg', '.ppm', '.jpg']:  
        try:  
            im = imageio.imread(file_name)  
            im = np.asarray(im)  
            if im.ndim == 3 and im.shape[2] > 3:  
                return im[:, :, :3]  
            else:  
                return im  
        except Exception as e:  
            print(f"Error reading image file {file_name}: {e}")  
            return [] 
  
    elif ext in ['.bin', '.raw']:  
        try:  
            return np.load(file_name)  
        except Exception as e:  
            print(f"Error reading numpy file {file_name}: {e}")  
            return None  
  
    elif ext == '.flo':  
        try:  
            return flow_utils.readFlow(file_name).astype(np.float32)  
        except Exception as e:  
            print(f"Error reading flow file {file_name}: {e}")  
            return None  
  
    print(f"Unsupported file extension: {ext} for file {file_name}")  
    return []