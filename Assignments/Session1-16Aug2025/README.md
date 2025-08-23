# Additional Questions

## Q1. What are Channels and Kernels (according to EVA)?

**Ans1.**  
- **Channels:** Channel is a bag of similar features. All the objects which have similar features/characteristics/properties can be considered one channel.  
  For example, if we have a vegetable biryani, all the different vegetables and ingredients can be considered as channels: all peas as one channel, all carrots as one channel, and so on.  

- **Kernels:** Kernel is a feature extractor; it helps in extracting features out of the image by performing convolution over the complete image.  
  In the vegetable biryani example, the person who is seeing the dish is the kernel who can differentiate and extract all features [peas, carrot, rice ...].  

## Q2. Why should we only (well mostly) use 3x3 Kernels?

**Ans2.**  
It helps us build anything we want. Also, big companies like NVIDIA, INTEL, and AMD have accelerated 3x3 kernels, so people started to use them more often. It is also an odd-size kernel.  
We don't use even-size kernels because they don’t have a central line and hence no symmetry.

## Q3. How many times do we need to perform 3x3 convolution operation to reach 1x1 from 199x199 (show calculations)?

**Ans3.**  
We need to perform the convolution operation
