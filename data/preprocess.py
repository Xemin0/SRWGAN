import tensorflow as tf
import os
from os import listdir
from os.path import join

from PIL import Image



def TrainDatasetFromFolder(dataset_dir = './Datasets'):
    '''
    High Resolution Shape: (800, 256, 256, 3)
    Low Resolution Shape:  (800, 64, 64, 3)
    '''
    dataset_dir = join(dataset_dir, "DIV2K_train_HR/DIV2K_train_HR/")
    image_filenames = [join(dataset_dir, i) for i in listdir(dataset_dir)]
    lr_images = []
    hr_images = []

    crop_size = 256
    upscale_factor = 4

    crop_size = crop_size - (crop_size % upscale_factor)
    #print('crop_size', crop_size)
    for image_filename in image_filenames:
        #print(image_filename)
        hr_image = tf.keras.utils.load_img(image_filename)
        hr_image = tf.convert_to_tensor(hr_image)
        #print(hr_image.shape)
        
        hr_transform = tf.image.random_crop(hr_image, size = [crop_size,crop_size, hr_image.shape[-1]])
        lr_transform = tf.image.resize(hr_transform, size = (crop_size // upscale_factor, crop_size // upscale_factor))
        
        lr_images.append(lr_transform)
        hr_images.append(hr_transform)

    lr_images = tf.stack(lr_images)
    hr_images = tf.stack(hr_images)

    print('*******************************************')
    print('Successfully Loaded Data from:', dataset_dir)
    print(f'Total: {lr_images.shape[0]} Low-Res Images \t {hr_images.shape[0]} High-Res Images')
    print(f'Shapes: {lr_images.shape[1:]}\t{hr_images.shape[1:]}')
    print('*******************************************')

    return tf.cast(lr_images, dtype = tf.float32), tf.cast(hr_images, dtype = tf.float32)

#TrainDatasetFromFolder()





