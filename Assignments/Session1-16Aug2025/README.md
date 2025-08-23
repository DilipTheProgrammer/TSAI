# TSAI Projects

## Project 1 — The School of AI

### Assignment 1A: Chrome Plugin Development using Cursor.ai

#### Overview  
In this session, we explore 1–2 examples of using Cursor to create Chrome Extensions. You are encouraged to get creative and build something unique!

#### Example Ideas  
- Find and list the latest movies on Netflix  
- Find the next Cricket Match or F1 Grand Prix  
- Change the font on any website to your liking  
- Create a clipboard that stores all "copy" texts in your browser  
- Develop a small web browser-based game  

#### Important Notes  
- Limit development time to **no more than 1 hour** to avoid getting addicted  
- Start from scratch rather than fixing a large existing project  
- Improve your prompt with each iteration  

#### Submission Instructions  
1. Upload a short video of your extension working on YouTube  
   _(Use tools like Snip & Sketch, OBS, etc. to capture video)_  
2. Zip your project folder and share the code  
3. Optionally, share your work on LinkedIn for **200 bonus points!**  

#### Motivation  
Sharing publicly puts healthy design and aesthetic pressure on you, as feedback and critique help you improve.  
_Remember:_  
> When you stop expecting appreciation and make yourself your own benchmark, the world will start appreciating.

---

## Assignment 1B: Quiz

### Quiz Results  
- **Score:** 50.33 out of 90  
- **Submitted:** Aug 17 at 2:59 AM  
- **Duration:** 9 minutes  

### Question 1 (10 pts)  
**Select the odd one out:**  
- Channel  
- An 11x11 matrix that is used to slide or convolve on an image  
- Kernel  
- Feature Extractor  
- A 3x3 matrix that is used to slide or convolve on an image  

**Correct answer:** *Channel*  

### Question 2 (10 pts)  
**What should be the receptive field of the kernels in the last layer?**  
_(For text models: how many words should the last layer "see" to predict effectively?)_  
- 400x400  
- Equal to the size of the image  
- Equal to the size of the kernel  
- ¯\\_(ツ)_/¯  

**Correct answer:** *Equal to the size of the image*  

### Question 3 (10 pts)  
**What should be the attention span of a transformer model, about to predict the next word?**  
- Last few words  
- Last word  
- As long as the length of all the words encountered till now  
- Half of the length of all the words encountered till now  

**Correct answer:** *As long as the length of all the words encountered till now*  

### Question 4 (10 pts)  
**What are channels?**  
- Output of kernels  
- Output of Fully connected layer  
- Collection of Kernels  
- A collection of neurons that hold contextually similar information  

**Correct answer:** *Output of kernels*  

### Question 5 (10 pts)  
**I'm loving ERA V4 course!**  
- True 😀  
- True 😀  
- Definitely True 😀  

**Correct answer:** *Whatever you feel*  
_(Note: "Definitely True" was marked wrong 😀)_  

### Question 6 (10 pts)  
**Match the following:**  

| Feature Complexity       | Description          |
|-------------------------|---------------------|
| Starting Features        | Edges and Gradients  |
| Slightly complex feature | Textures and Patterns|
| More complex feature     | Parts of Objects     |
| Very complex feature     | Objects              |

**Correct answer:** Same as above  

### Question 7 (10 pts)  
**Match the following:**  

| Feature Complexity       | Description          |
|-------------------------|---------------------|
| Starting Features        | Characters           |
| Slightly complex feature | Words                |
| More complex feature     | Sentences            |
| Very complex feature     | Stories              |

**Correct answer:** *Same order*  

### Question 8 (10 pts)  
**What determines how many features we should extract?**  
- Depends on how capable our training hardware is  
- Depends on how varied our dataset and problem statement is  
- How many features are actually there in the images/dataset  
- Depends on how capable our deployment hardware is  
- Depends on how rich we are (so we can afford better hardware)  

**Correct answer:** *All of the above*  

### Question 9 (10 pts)  
**Select the ones that are TRUE:**  
- Kernels and channels are the same things  
- Receptive field of the last layer should be at least equal to the size of the image  
- Total number of channels is determined by the total number of kernels in a convolutional neural network  
- The attention span of a transformer NLP model must be equal to the complete length of the input  

**Correct answers:**  
- Receptive field of the last layer should be at least equal to the size of the image  
- Total number of channels is determined by the total number of kernels in a CNN  
- The attention span of a transformer NLP model must be equal to the complete length of the input  

### Question 10 (10 pts)  
**Select the ones that are FALSE:**  
- The 9 values in a 3x3 kernel are the values which our neural network learns  
- When we convolve, we element-wise multiply the 9 values of the kernel with the 9 values of the image/channel, then sum them to get a single value  
- We use 3x3s because that is what is optimized for speed on most hardware  
- We use 3x3 because 9 is the luckiest number in the world!  

**Correct answer:** *We use 3x3 because 9 is the luckiest number in the world!*  

---

## Final Quiz Score  
**50.33 out of 90**  

---

# Additional Questions

## Q1. What are Channels and Kernels (according to EVA)?

**Answer:**  
- **Channels:** A channel is a bag of similar features. Objects with similar features/characteristics/properties can be considered one channel.  
  _Example:_ In vegetable biryani, all peas can be one channel, all carrots another, etc.  

- **Kernels:** Kernels are feature extractors that perform convolution over the image to extract features.  
  _Example:_ In the biryani example, the observer who differentiates peas, carrots, rice is the kernel.  

## Q2. Why should we only (mostly) use 3x3 Kernels?

**Answer:**  
- 3x3 kernels help build anything we want efficiently.  
- Big companies like NVIDIA, INTEL, and AMD hardware-accelerate 3x3 kernels.  
- 3x3 kernels are odd-sized, providing symmetry with a center line, unlike even-sized kernels.  

## Q3. How many times do we need to perform 3x3 convolutions to reach 1x1 from 199x199?  

**Answer:**  
- 99 times  

**Calculation:**  
1. 199x199 → 197x197  
2. 197x197 → 195x195  
3. 195x195 → 193x193  
4. 193x193 → 191x191  
5. 191x191 → 189x189  
6. 189x189 → 187x187  
7. 187x187 → 185x185  
8. 185x185 → 183x183  
9. 183x183 → 181x181  
10. 181x181 → 179x179  
11. 179x179 → 177x177  
12. 177x177 → 175x175  
13. 175x175 → 173x173  
14. 173x173 → 171x171  
15. 171x171 → 169x169  
16. 169x169 → 167x167  
17. 167x167 → 165x165  
18. 165x165 → 163x163  
19. 163x163 → 161x161  
20. 161x161 → 159x159  
21. 159x159 → 157x157  
22. 157x157 → 155x155  
23. 155x155 → 153x153  
24. 153x153 → 151x151  
25. 151x151 → 149x149  
26. 149x149 → 147x147  
27. 147x147 → 145x145  
28. 145x145 → 143x143  
29. 143x143 → 141x141  
30. 141x141 → 139x139  
31. 139x139 → 137x137  
32. 137x137 → 135x135  
33. 135x135 → 133x133  
34. 133x133 → 131x131  
35. 131x131 → 129x129  
36. 129x129 → 127x127  
37. 127x127 → 125x125  
38. 125x125 → 123x123  
39. 123x123 → 121x121  
40. 121x121 → 119x119  
41. 119x119 → 117x117  
42. 117x117 → 115x115  
43. 115x115 → 113x113  
44. 113x113 → 111x111  
45. 111x111 → 109x109  
46. 109x109 → 107x107  
47. 107x107 → 105x105  
48. 105x105 → 103x103  
49. 103x103 → 101x101  
50. 101x101 → 99x99  
51. 99x99 → 97x97  
52. 97x97 → 95x95  
53. 95x95 → 93x93  
54. 93x93 → 91x91  
55. 91x91 → 89x89  
56. 89x89 → 87x87  
57. 87x87 → 85x85  
58. 85x85 → 83x83  
59. 83x83 → 81x81  
60. 81x81 → 79x79  
61. 79x79 → 77x77  
62. 77x77 → 75x75  
63. 75x75 → 73x73  
64. 73x73 → 71x71  
65. 71x71 → 69x69  
66. 69x69 → 67x67  
67. 67x67 → 65x65  
68. 65x65 → 63x63  
69. 63x63 → 61x61  
70. 61x61 → 59x59  
71. 59x59 → 57x57  
72. 57x57 → 55x55  
73. 55x55 → 53x53  
74. 53x53 → 51x51  
75. 51x51 → 49x49  
76. 49x49 → 47x47  
77. 47x47 → 45x45  
78. 45x45 → 43x43  
79. 43x43 → 41x41  
80. 41x41 → 39x39  
81. 39x39 → 37x37  
82. 37x37 → 35x35  
83. 35x35 → 33x33  
84. 33x33 → 31x31  
85. 31x31 → 29x29  
86. 29x29 → 27x27  
87. 27x27 → 25x25  
88. 25x25 → 23x23  
89. 23x23 → 21x21  
90. 21x21 → 19x19  
91. 19x19 → 17x17  
92. 17x17 → 15x15  
93. 15x15 → 13x13  
94. 13x13 → 11x11  
95. 11x11 → 9x9  
96. 9x9 → 7x7  
97. 7x7 → 5x5  
98. 5x5 → 3x3  
99. 3x3 → 1x1  
