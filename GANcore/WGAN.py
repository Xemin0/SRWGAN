import tensorflow as tf

from WGAN_Core import WGAN_Core

class WGAN(WGAN_Core):
    '''
    WGAN Class with Gradient Penalty and ContentLoss(a pretrained model)
    '''
    def __init__(self, pretrained = 'resnet50', hyperimg_ids = [0,2,5,11,12,15,20] , *args, **kwargs):
        super().__init__(*args, **kwargs)
        '''
        Pretrained Models for Content Loss.
        Currently Support:
                    - ResNet50
                    - ResNet101

                    - FCN101
        '''
        if 'resnet50' == pretrained.lower():
            self.pretrained = 
            # hyperimg_ids =  [0,11,12,13] for CAM
        elif 'resnet101' == pretrained.lower():
            self.pretrained = 
            # hyperimg_ids = [2,22,24,25,27,28,29] for CAM
            # hyperimg_ids = [0,19,27,28,29,30]
        else:
            raise Exception('Only supports resnet50 and resnet 101 for ContentLoss')

        self.hyper_ids = hyperimg_ids

    # MSE of Hyperimages(fake - real)
    # Hyper Images are constructed by taking intermediate output feature maps
    # from a Pretrained model (ResNet108)
    def contentLoss(img_fake:tf.Tensor, img_real:tf.Tensor):
        return 0

    def gradient_penalty(self, batch_size, x_fake, x_real):
        '''
        Calculate the Gradient Penalty.

        This loss is calculated on an interpolated image and added to the Discriminator Loss.
        '''

        # Get the interpolated image
        e_norm = tf.random.normal([batch_size, 1, 1, 1], 0.0, 1.0) # Normal Distribution? Uniform Distribution?
        diff = x_fake - x_real
        interpolates = x_real + e_norm * diff

        # Gradients
        with tf.GradientTape() as tape:
          tape.watch(interpolates)
          # 1. Output of Critic using the interpolates
          pred = self.crt_model(interpolates, training = True)

        # Graidents w.r.t. the input = interpolates
        grads = tape.gradient(pred, [interpolates])[0]

        # Calculate the norm of the gradients
        norm = tf.sqrt(tf.reduce_sum(tf.square(grads), axis = [1,2,3])) # All dimensions except for the batch dimension
        gradient_penalty = tf.reduce_mean((norm - 1.0) ** 2)

        return gradient_penalty
    
    def test_step(self, data): ###### New Z_samp every weight update instead of every complete training step
        x_real, l_real = data
        batch_size = tf.shape(x_real)[0]

        ## - x_real: Real Images from dataset
        ## - d_real: The discriminator's prediction of the reals
        ## - x_fake: Images generated by generator
        ## - d_fake: The discriminator's prediction of the fakes
        z_samp = self.sample_z(batch_size, training = False)
        x_fake = self.generate(z_samp, training = False)
        d_fake = self.criticize(x_fake, training = False)
        d_real = self.criticize(x_real, training = False)

        ###################################

        metrics = dict()

        all_funcs = {**self.loss_funcs, **self.acc_funcs}

        for key, func in all_funcs.items():
          metrics[key] = func(d_fake, d_real)

        return metrics
    
    def train_step(self, data):
        x_real, l_real = data
        batch_size = tf.shape(x_real)[0]

        # For each Batch, as laid out in the original paper:
        # 1. Train the Discriminator and Get the Discriminator Loss
        # 2. Train the Generator and Get the generator Loss
        # 3. Calculate the Gradient Penalty
        # 4. Multiply this gradient Penalty with a constant weight
        # 5. Add the Gradient Penalty to the discriminator Loss
        # 6. Return the Generator and Discriminator Losses as a loss dictionary

        # Train the Discriminator First.
        # The original paper recommends training
        # the discriminator for 'n' more steps (typically 5) as compared to
        # one step of the generator. 

        # Train for Discriminator/Critic
        loss_fn = self.loss_funcs['d_loss']
        optimizer = self.optimizers['d_opt']

        for i in range(self.dis_steps):
          z_samp = self.sample_z(batch_size) ## New z_samp every update?
          # Gradient Tape
          with tf.GradientTape() as tape:
            # Generated Fake images from the Z_samp
            x_fake = self.generate(z_samp, training = True) # True for Gradient Penalty
            # Logits/Criticism from Discriminator for the Fake images
            d_fake = self.criticize(x_fake, training = True)
            # Logits/Criticism from Discriminator for the Real images
            d_real = self.criticize(x_real, training = True)

            # Default Discriminator Loss 
            d_cost = loss_fn(d_fake, d_real)
            # Gradient Penalty
            gp = self.gradient_penalty(batch_size, x_fake, x_real)
            # Total loss = Default D Loss + Gradient-Penalty
            d_loss = d_cost + gp * self.gp_weight

          # Get the Gradients of d_loss w.r.t. the Discriminator's parameters
          g = tape.gradient(d_loss, self.crt_model.trainable_variables)
          optimizer.apply_gradients(zip(g, self.crt_model.trainable_variables))

        
        # Train for Generator
        loss_fn = self.loss_funcs['g_loss']
        optimizer = self.optimizers['g_opt']

        for i in range(self.gen_steps):
          z_samp = self.sample_z(batch_size)
          # Gradient Tape
          with tf.GradientTape() as tape:
            # Generated Fake images from the z_samp
            x_fake = self.generate(z_samp, training = True)
            # Logits/Criticism from Discriminator for the fake images
            d_fake = self.criticize(x_fake, training = True)
            # Generator Loss 
            g_loss = loss_fn(d_fake, None)

          # Get the gradients of g_loss w.r.t. the Generator's parameters
          g = tape.gradient(g_loss, self.gen_model.trainable_variables)
          optimizer.apply_gradients(zip(g, self.gen_model.trainable_variables))

          # Compute Final states for metric computation
          # new z_samp??
          z_samp = self.sample_z(batch_size)

          x_fake = self.generate(z_samp, training = False)

          d_fake = self.discriminate(x_fake, training = False)

          d_real = self.discriminate(x_real, training = False)

          #######################################

          metrics = dict()

          all_funcs = {**self.loss_funcs, **self.acc_funcs}

          for key, func in all_funcs.items():
            metrics[key] = func(d_fake, d_real)

          return metrics
