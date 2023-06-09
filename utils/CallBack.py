import tensorflow as tf
import numpy as np
'''
Callback helper fro SRWGAN-GP
'''

import matplotlib.pyplot as plt
from PIL import Image
import io

class EpochVisualizer(tf.keras.callbacks.Callback):
    def __init__(self, model, sample_inputs, **kwargs):
        '''
        sample_inputs = [true_sample, fake_sample] = [high_res, super_res]

        *** All Samples are of Range [-1, 1]
        *** Needs to be Decentralized to Range [0,1] or uint8 [0,255] for plotting
        '''
        super().__init__(**kwargs)
        self.model = model
        self.sample_inputs = sample_inputs
        self.imgs = []

    def on_epoch_end(self, epoch, logs=None):
        x_real, x_fake = self.sample_inputs
        d_real = tf.nn.sigmoid(self.model.dis_model(x_real)) ## Does not exactly represent the Validity
        d_fake = tf.nn.sigmoid(self.model.dis_model(x_fake)) ## Does not exactly represent the Validity
        outputs = tf.concat([x_real, x_fake], axis=0)
        labels  = [f"D(true x) = {np.round(100 * d, 0)}%" for d in d_real]
        labels += [f"D(fake x) = {np.round(100 * d, 0)}%" for d in d_fake]

        #####
        ## Decentralize the output 
        ####
        outputs = (outputs + 1.0)/2.0

        self.add_to_imgs(
            outputs = outputs,
            labels = labels,
            epoch = epoch
        )

    def add_to_imgs(self, outputs, labels, epoch, nrows=1, ncols=4, figsize=(16, 5)):
        '''
        Plot the image samples in outputs in a pyplot figure and add the image
        to the 'imgs' list. Used to later generate a gif.
        '''
        fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
        if nrows == 1: axs = np.array([axs])
        fig.suptitle(f'Epoch {epoch+1}')
        axs[0][0].set_title(f'Epoch {epoch+1}')
        for i, ax in enumerate(axs.reshape(-1)):
            #out_numpy = np.squeeze(outputs[i].numpy(), -1) # For 3 Channel Images, there's no need to squeeze
            out_numpy = outputs[i].numpy()
            ax.imshow(out_numpy) ##, cmap='rgb')
            ax.set_title(labels[i])
        self.imgs += [self.fig2img(fig)]
        plt.close(fig)

    @staticmethod
    def fig2img(fig):
        """
        Convert a Matplotlib figure to a PIL Image and return it
        https://stackoverflow.com/a/61754995/5003309
        """
        buf = io.BytesIO()
        fig.savefig(buf)
        buf.seek(0)
        return Image.open(buf)

    def save_gif(self, filename='SuperResolution', loop=True, duration=500):
        imgs = self.imgs
        self.imgs[0].save(
            filename+'.gif', save_all=True, append_images=self.imgs[1:],
            loop=loop, duration=duration)
