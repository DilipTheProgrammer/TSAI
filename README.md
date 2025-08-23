# ERA v4- The School of AI  <br />

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-397/) [![PyTorch 2.0+](https://img.shields.io/badge/PyTorch-2.0+-green.svg)](https://pytorch.org/) [![torchvision 0.15+](https://img.shields.io/badge/torchvision-0.15+-blue.svg)](https://pypi.org/project/torchvision/) [![torch-summary 1.4](https://img.shields.io/badge/torchsummary-1.4+-green.svg)](https://pypi.org/project/torch-summary/)


The repository presents the assignments for all the sessions covered as part of the course ERA-V4, presented by [SchoolOfAI](https://theschoolof.ai/) and [Rohan Shravan](https://www.linkedin.com/in/rohanshravan/)

# **Course Details**

Program Name: ERA V4 <br />
Commencement Date: 16 Aug 2025 <br />
<hr/>

### ERA V4 Course Objectives

| S.No. | Objective | Description |
|-------|-----------|-------------|
| 1 | Real-World, Full-Scale LLM Training | Gain hands-on experience training a large-scale (70B parameter) model end-to-end, including instruction tuning, with a focus on practical exposure to compute and optimization challenges. |
| 2 | Practical CoreSet Focus | Understand and apply the principles of CoreSet selection and data efficiency, moving beyond just dataset exposure to strategies that maximize model performance with fewer resources. |
| 3 | Multi-GPU ImageNet Training | Develop practical skills in distributed training by training on the full ImageNet dataset across multiple GPUs, simulating real-world research lab conditions. |
| 4 | Quantization-Aware Training (QAT) | Learn QAT as a first-class method for scaling models efficiently, gaining the ability to train and deploy models with 100B+ parameters while considering deployment constraints. |
| 5 | Balanced Exposure to RL, VLMs, and Embeddings | Explore reinforcement learning, vision-language models, and embeddings in a balanced way, covering modern modalities and techniques with an emphasis on practical deployment. |

---

### ERA V4 Program Session Plan

### **Course Sessions**
<hr/>

- **Session 1** - Introduction to AI, NN, Dev tools
- **Session 2** - Python Essentials, Version control using git/uv, Web Dev, Cloud AWS EC2 revisit
- **Session 3** -
- **Session 4** -
- **Session 5** - 
- **Session 6** - 
- **Session 7** - 
- **Session 8** - 
- **Session 9** - 
- **Session 10** -




### Session 1: Introduction to AI, Neural Networks and Development Tools
- What is AI? Evolution and real-world applications.  
- Neural Network fundamentals: perceptrons, activations, weights, bias.  
- Overview of course flow: how we go from scratch to training a 70B LLM.  
- Setting up dev environment: Python, VS Code, CUDA drivers.  
- Install PyTorch, WandB, Git, and use Cursor for coding acceleration.  

### Session 2: Python Essentials, Version Control, and Web Development Basics
- Python for ML: Essential Python syntax and data structures relevant to AI programming.  
- Git/GitHub workflow: Basic commands, branching, merging, and collaboration workflows.  
- Basic HTML/CSS/JS and Flask – serve static frontend.  
- Launch a web UI to visualize model outputs early.  

### Session 3: PyTorch Fundamentals and AWS EC2 101
- Introduction to PyTorch and Tensors: Understanding tensors, tensor operations, and PyTorch basics.  
- AutoGrad and Computational Graphs: Mechanism of automatic differentiation in PyTorch.  
- Building Simple Neural Networks: Constructing basic neural networks using PyTorch.  
- Implementing Training Loops: Writing loops for training and validating models.  
- Spin up EC2 instance and connect via SSH.  

### Session 4: Building First Neural Network and Training on Cloud
- Build first MLP with PyTorch for MNIST.  
- Visualize loss curves with WandB.  
- Train on Colab and EC2.  
- Save checkpoints and load model weights.  
- Build a Flask API + frontend to display predictions.  

### Session 5: CNNs and Backpropagation
- Basics of CNNs: Understanding convolution operations, filters, feature maps, and receptive fields.  
- Implementing CNNs in PyTorch: Building and training CNN models on image datasets.  
- Backpropagation: The fundamentals of the backbone of training Neural Networks.  
- Architectural Basics: How do we structure a neural network together?  
- Training CNNs: Techniques for effective training and avoiding overfitting.  

### Session 6: In-Depth Coding Practice – CNNs
- Hands-On Practice with CNNs: Extensive coding session focused on deepening understanding of CNN implementation.  
- Advanced CNN Architectures: Exploring more complex CNN structures like VGG and Inception networks.  
- Data Augmentation for CNNs: Applying data augmentation techniques to improve CNN performance.  
- Model Evaluation and Debugging: Practical examples on how to evaluate CNNs’ performance, debug issues, and fine-tune models.  
- Use WeightWatcher to analyze and visualize weight distributions.  

### Session 7: Advanced CNN Architectures & Training
- Advanced Concepts: Image Normalization, Batch, Group & Layer Normalization, Regularization  
- Regularizations: Batch Size, Early Stopping, DropOut, and L1/L2 Regularizations  
- Advanced Convolutions: Pointwise, Atrous, Transpose, Pixel Shuffle, Depthwise, and Group Convolutions  
- Data Augmentation: PMDAs, Elastic Distortion, CutOut, MixUp, RICAP, RMDAs and Strategy.  
- Use CoreSets to reduce dataset without losing performance.  
- Compare performance of full vs subset training.  

### Session 8: One Cycle Policy and CoreSet Training
- Larger than Life Receptive Fields: What happens when we go deeeeeeper!  
- Advent of "many" receptive fields: Modern Neural Networks have "many receptive fields" 🤔  
- ResNets: The "final" Convolution architecture  
- Learning rate schedules, warmups, cosine decay.  
- One Cycle Policy training for fast convergence.  
- Use CoreSet sampling for image data – improve generalization.  
- Live run: CIFAR-10 or TinyImageNet with OneCycle + CoreSets.  

### Session 9: Multi-GPU Training of ResNet from Scratch on Full ImageNet
- Set up DDP (Distributed Data Parallel) in PyTorch.  
- Train ResNet-50 from scratch on full ImageNet.  
- Use EC2 for multi-GPU training.  
- Visualize training progress, speedup from parallelism.  

### Session 10: Introduction to Transformers and Emergent Abilities in LLMs
- Self-attention, multi-head attention, positional encodings.  
- Implement transformer block from scratch.  
- Vision Transformers (ViT) vs CNNs – pros and cons.  
- Introduction to emergent abilities of large models (in-context learning, tool use).  

### Session 11: Embeddings, Tokenization, and CoreSets
- Intro to tokenization and BPE.  
- Implement BPE tokenizer from scratch.  
- CoreSets for text datasets – token diversity preservation.  
- Embedding spaces: cosine similarity, t-SNE/UMAP visualizations.  
- Prep text dataset for LLM training.  

### Session 12: Transformer Architectures, MHA and LLM Training
- Decoder-only architecture (GPT-style): MHA, FFN, layer norm.  
- RoPE (rotary positional embedding) – why and how.  
- Implement training loop with causal



---

# **Course Achievement**
**Successfully completed the EVA Course with distinction.**
