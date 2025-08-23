# TSAI Projects

## Project 1 — The School of AI  

---

### Assignment 1A: Chrome Plugin Development using Cursor.ai  

#### Overview  
In this session, we explore 1–2 examples of using Cursor to create Chrome Extensions. We are encouraged to get creative and build something unique!  

#### Example Ideas  
- Find and list the latest movies on Netflix  
- Find the next Cricket Match or F1 Grand Prix  
- Change the font on any website to your liking  
- Create a clipboard that stores all "copy" texts in your browser  
- Develop a small web browser-based game  

#### Important Notes  
- Limit your development time to no more than **1 hour** to avoid getting too addicted!  
- Start from scratch rather than fixing an already large project.  
- Improve your prompt with each iteration.  

#### Submission Instructions  
1. Upload a short video of your extension working on YouTube (capture tools: Snip & Sketch, OBS, etc.).  
2. Zip your project folder and share the code.  
3. Optionally, share your work on LinkedIn for **200 bonus points!**  

#### Motivation  
Sharing publicly puts healthy design and aesthetics pressure on you, as feedback and critique help you improve.  
_Remember:_  
> When you stop expecting appreciation and make yourself your own benchmark, the world will start appreciating.  

---

### Assignment 1B: Quiz  

---

## Quiz Results  

- **Score:** 50.33 out of 90  
- **Submitted:** Aug 17 at 2:59 AM  
- **Duration:** 9 minutes  

---

### Question 1 (10 pts)  
**Select the odd one out:**  
- Channel  
- a 11x11 matrix that is used to slide or convolve on an image  
- Kernel  
- Feature Extractor  
- a 3x3 matrix that is used to slide or convolve on an image  

**Correct Answer:** *Channel*  

---

### Question 2 (10 pts)  
**What should be the receptive field of the kernels in the last layer?**  
*(For text models: how many words should the last layer "see" to predict effectively?)*  
- 400x400  
- Equal to the size of the image  
- Equal to the size of the kernel  
- ¯\\_(ツ)_/¯  

**Correct Answer:** *Equal to the size of the image*  

---

### Question 3 (10 pts)  
**What should be the attention span of a transformer model, about to predict the next word?**  
- Last few words  
- Last word  
- As long as the length of all the words encountered till now  
- Half of the length of all the words encountered till now  

**Correct Answer:** *As long as the length of all the words encountered till now*  

---

### Question 4 (10 pts)  
**What are channels?**  
- Output of kernels  
- Output of Fully connected layer  
- Collection of Kernels  
- A collection of neurons that hold contextually similar information  

**Correct Answer:** *Output of kernels*  

---

### Question 5 (10 pts)  
**I'm loving ERA V4 course!**  
- True 😀  
- True 😀  
- Definitely True 😀  

**Correct Answer:** *Whatever you feel*  
*(I put "Definitely True," but was marked wrong 😀)*  

---

### Question 6 (10 pts)  
**Match the following:**  

- Starting Features → Edges and Gradients  
- Slightly complex feature → Textures and Patterns  
- More complex feature → Parts of Objects  
- Very complex feature → Objects  

**Correct Answer:**  
- Starting Features = Edges and Gradients  
- Slightly complex feature = Textures and Patterns  
- More complex feature = Parts of Objects  
- Very complex feature = Objects  

---

### Question 7 (10 pts)  
**Match the following:**  

- Starting Features → Characters  
- Slightly complex feature → Words  
- More complex feature → Sentences  
- Very complex feature → Stories  

**Correct Answer:** *Same order*  

---

### Question 8 (10 pts)  
**What determines how many features we should extract?**  
- Depends on how capable our training hardware is  
- Depends on how varied our dataset and problem statement is  
- How many features are actually there in the images/dataset  
- Depends on how capable our deployment hardware is  
- Depends on how rich we are (so we can afford better hardware)  

**Correct Answer:** *All of the above*  

---

### Question 9 (10 pts)  
**Select the ones that are TRUE:**  
- Kernels and channels are the same things  
- Receptive field of the last layer should be at least equal to the size of the image  
- Total number of channels is determined by the total number of kernels in a convolutional neural network  
- The attention span of a transformer NLP model must be equal to the complete length of the input  

**Correct Answers:**  
- Receptive field of the last layer should be at least equal to the size of the image  
- Total number of channels is determined by the total number of kernels in a CNN  
- The attention span of a transformer NLP model must be equal to the complete length of the input  

---

### Question 10 (10 pts)  
**Select the ones that are FALSE:**  
- The 9 values in a 3x3 kernel are the values which our neural network learns  
- When we convolve, we element-wise multiply the 9 values of the kernel with the 9 values of the image/channel, then sum them to get a single value  
- We use 3x3s because that is what is optimized for speed on most hardware  
- We use 3x3 because 9 is the luckiest number in the world!  

**Correct Answer:** *We use 3x3 because 9 is the luckiest number in the world!*  

---

## Final Quiz Score  
**50.33 out of 90**  





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

#### Q3. How many times do we need to perform 3x3 convolution operation to reach 1x1 from 199x199 (show calculations).

**Ans3.**
99 time we need to perform convolution operation to reach 1X1.

Calculation:
1. 199x199 | 3x3 > 197x197
2. 197x197 | 3x3 > 195x195
3. 195x195 | 3x3 > 193x193
4. 193x193 | 3x3 > 191x191
5. 191x191 | 3x3 > 189x189
6. 189x189 | 3x3 > 187x187
7. 187x187 | 3x3 > 185x185
8. 185x185 | 3x3 > 183x183
9. 183x183 | 3x3 > 181x181
10. 181x181 | 3x3 > 179x179
11. 179x179 | 3x3 > 177x177
12. 177x177 | 3x3 > 175x175
13. 175x175 | 3x3 > 173x173
14. 173x173 | 3x3 > 171x171
15. 171x171 | 3x3 > 169x169
16. 169x169 | 3x3 > 167x167
17. 167x167 | 3x3 > 165x165
18. 165x165 | 3x3 > 163x163
19. 163x163 | 3x3 > 161x161
20. 161x161 | 3x3 > 159x159
21. 159x159 | 3x3 > 157x157
22. 157x157 | 3x3 > 155x155
23. 155x155 | 3x3 > 153x153
24. 153x153 | 3x3 > 151x151
25. 151x151 | 3x3 > 149x149
26. 149x149 | 3x3 > 147x147
27. 147x147 | 3x3 > 145x145
28. 145x145 | 3x3 > 143x143
29. 143x143 | 3x3 > 141x141
30. 141x141 | 3x3 > 139x139
31. 139x139 | 3x3 > 137x137
32. 137x137 | 3x3 > 135x135
33. 135x135 | 3x3 > 133x133
34. 133x133 | 3x3 > 131x131
35. 131x131 | 3x3 > 129x129
36. 129x129 | 3x3 > 127x127
37. 127x127 | 3x3 > 125x125
38. 125x125 | 3x3 > 123x123
39. 123x123 | 3x3 > 121x121
40. 121x121 | 3x3 > 119x119
41. 119x119 | 3x3 > 117x117
42. 117x117 | 3x3 > 115x115
43. 115x115 | 3x3 > 113x113
44. 113x113 | 3x3 > 111x111
45. 111x111 | 3x3 > 109x109
46. 109x109 | 3x3 > 107x107
47. 107x107 | 3x3 > 105x105
48. 105x105 | 3x3 > 103x103
49. 103x103 | 3x3 > 101x101
50. 101x101 | 3x3 > 99x99
51. 99x99 | 3x3 > 97x97
52. 97x97 | 3x3 > 95x95
53. 95x95 | 3x3 > 93x93
54. 93x93 | 3x3 > 91x91
55. 91x91 | 3x3 > 89x89
56. 89x89 | 3x3 > 87x87
57. 87x87 | 3x3 > 85x85
58. 85x85 | 3x3 > 83x83
59. 83x83 | 3x3 > 81x81
60. 81x81 | 3x3 > 79x79
61. 79x79 | 3x3 > 77x77
62. 77x77 | 3x3 > 75x75
63. 75x75 | 3x3 > 73x73
64. 73x73 | 3x3 > 71x71
65. 71x71 | 3x3 > 69x69
66. 69x69 | 3x3 > 67x67
67. 67x67 | 3x3 > 65x65
68. 65x65 | 3x3 > 63x63
69. 63x63 | 3x3 > 61x61
70. 61x61 | 3x3 > 59x59
71. 59x59 | 3x3 > 57x57
72. 57x57 | 3x3 > 55x55
73. 55x55 | 3x3 > 53x53
74. 53x53 | 3x3 > 51x51
75. 51x51 | 3x3 > 49x49
76. 49x49 | 3x3 > 47x47
77. 47x47 | 3x3 > 45x45
78. 45x45 | 3x3 > 43x43
79. 43x43 | 3x3 > 41x41
80. 41x41 | 3x3 > 39x39
81. 39x39 | 3x3 > 37x37
82. 37x37 | 3x3 > 35x35
83. 35x35 | 3x3 > 33x33
84. 33x33 | 3x3 > 31x31
85. 31x31 | 3x3 > 29x29
86. 29x29 | 3x3 > 27x27
87. 27x27 | 3x3 > 25x25
88. 25x25 | 3x3 > 23x23
89. 23x23 | 3x3 > 21x21
90. 21x21 | 3x3 > 19x19
91. 19x19 | 3x3 > 17x17
92. 17x17 | 3x3 > 15x15
93. 15x15 | 3x3 > 13x13
94. 13x13 | 3x3 > 11x11
95. 11x11 | 3x3 > 9x9
96. 9x9 | 3x3 > 7x7
97. 7x7 | 3x3 > 5x5
98. 5x5 | 3x3 > 3x3
99. 3x3 | 3x3 > 1x1

---------------------------------------------------------------------------------------
