import os

import matplotlib.pyplot as plt
import numpy as np
import rootpath

rootpath.append()
from paths import FIRE_LABEL_PATH


def get_file_list():
    walker = os.walk(FIRE_LABEL_PATH)
    return [os.path.splitext(name)[0] for _, _, names in walker for name in names
            if os.path.splitext(name)[1] == '.npy']


# generate images of fire-labels
def showA(filename: str):
    mat = np.load(os.path.join(FIRE_LABEL_PATH, f'{filename}.npy'))
    plt.imshow(mat)
    plt.imsave(os.path.join(FIRE_LABEL_PATH, f'{filename}.png'), mat)


if __name__ == '__main__':
    for file_name in get_file_list():
        showA(file_name)
