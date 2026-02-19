# 🏗️ SYSTEM ARCHITECTURE

## Overview

This system implements a complete CNN → LLM pipeline for plant disease detection and treatment recommendation.

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACES                             │
├─────────────────┬──────────────────┬──────────────────┬─────────┤
│  Streamlit UI   │   CLI Tool       │  Python API      │         │
│   (app.py)      │   (cli.py)       │  (pipeline.py)   │  Mobile │
└────────┬────────┴────────┬─────────┴─────────┬────────┴─────────┘
         │                 │                   │
         └─────────────────┼───────────────────┘
                           │
                           ▼
         ┌─────────────────────────────────────┐
         │   PlantDiseaseAssistant (Pipeline)  │
         │       (plant_disease_pipeline.py)   │
         └──────────┬────────────────┬──────────┘
                    │                │
         ┌──────────▼──────┐  ┌──────▼──────────┐
         │   CNN Model     │  │   LLM Client    │
         │  MobileNetV2    │  │     Ollama      │
         │  (cnn.py)       │  │    (llm.py)     │
         └──────────┬──────┘  └──────┬──────────┘
                    │                │
         ┌──────────▼──────┐  ┌──────▼──────────┐
         │ PyTorch Model   │  │  Ollama Server  │
         │  (3.5M params)  │  │  (localhost)    │
         └─────────────────┘  └─────────────────┘
```

---

## Data Flow

### 1. Image Input → CNN Detection

```
Leaf Image (any size)
    │
    ├─► Resize to 256×256
    ├─► Center crop to 224×224
    ├─► Normalize (ImageNet stats)
    └─► Convert to Tensor [1, 3, 224, 224]
         │
         ▼
    MobileNetV2 (frozen backbone)
         │
         ├─► Feature extraction (1280 features)
         └─► Classifier (trainable)
              │
              ▼
         Softmax output [N classes]
              │
              ├─► argmax → Predicted class
              ├─► max → Confidence score
              └─► all values → Probability distribution
                   │
                   ▼
         {
           "plant": "Tomato",
           "disease": "Early blight",
           "confidence": 0.92,
           "is_confident": true,
           "top_5": [...]
         }
```

### 2. CNN Output → LLM Prompt

```
Detection Result
    │
    ├─► Extract: plant, disease, confidence
    ├─► Check: is_confident (threshold)
    └─► Generate structured prompt
         │
         ▼
    If CONFIDENT:
    "You are an expert... Plant: Tomato, Disease: Early blight,
     Confidence: 92%. Provide: Overview, Symptoms, Actions,
     Treatment, Prevention..."
    
    If UNCERTAIN:
    "Low confidence (65%). Explain why, what to look for,
     general precautions, when to seek help..."
         │
         ▼
    Send to Ollama API
```

### 3. LLM Response → User

```
Ollama LLM (llama3.2:3b)
    │
    ├─► Process prompt with context
    ├─► Generate treatment advice
    └─► Return formatted text
         │
         ▼
    {
      "advice": "Disease Overview: Early blight...",
      "success": true,
      "model_used": "llama3.2:3b"
    }
         │
         ▼
    Display to user via UI/CLI
```

---

## Model Architecture Details

### MobileNetV2 Structure

```
Input: [batch, 3, 224, 224]
    │
    ├─► Conv2d (32 channels)
    ├─► Inverted Residuals (frozen) ◄─── 17 bottleneck blocks
    ├─► Conv2d (1280 features)
    │
    └─► Classifier (trainable):
         ├─► Dropout(0.2)
         └─► Linear(1280 → N classes)
              │
              ▼
Output: [batch, N]  (logits)
```

**Parameters:**
- Total: ~3.5M
- Trainable: ~1.2M (classifier only)
- Frozen: ~2.3M (backbone)

**Why MobileNetV2?**
- ✅ Lightweight (200MB RAM)
- ✅ Fast inference (50ms CPU, 5ms GPU)
- ✅ Mobile-friendly
- ✅ Transfer learning efficient
- ✅ Proven for image classification

---

## Training Strategy

```
Dataset (ImageFolder format)
    │
    ├─► train/ (80%)
    │    ├─► Apple___Apple_scab/
    │    ├─► Tomato___Early_blight/
    │    └─► ...
    │
    └─► val/ (20%)
         ├─► Apple___Apple_scab/
         └─► ...
              │
              ▼
    Load pretrained MobileNetV2 (ImageNet weights)
              │
              ├─► Freeze all backbone layers
              └─► Replace final classifier
                   │
                   ▼
    Train ONLY classifier (1.2M params)
              │
              ├─► Optimizer: Adam (lr=0.001)
              ├─► Loss: CrossEntropyLoss
              ├─► Scheduler: ReduceLROnPlateau
              ├─► Augmentation: Flip, Rotate, ColorJitter
              └─► Epochs: 10-20
                   │
                   ▼
    Save best model (highest val accuracy)
```

**Why Transfer Learning?**
- ✅ Faster training (10 epochs vs 100+)
- ✅ Less data needed (100s vs 1000s per class)
- ✅ Better generalization
- ✅ Lower compute requirements

---

## LLM Integration

### Ollama Architecture

```
User Query
    │
    ▼
Local Ollama Server (localhost:11434)
    │
    ├─► Model: llama3.2:3b (3GB RAM)
    ├─► Context: 8K tokens
    └─► Temperature: 0.3 (focused)
         │
         ▼
    Generate response
         │
         ├─► Structured advice
         ├─► Farmer-friendly language
         └─► Actionable steps
              │
              ▼
    Return JSON response
```

**Why Ollama?**
- ✅ Fully local (privacy)
- ✅ No API costs
- ✅ Offline capable
- ✅ Easy model switching
- ✅ Fast inference

**Fallback Strategy:**
```
Try Ollama
    │
    ├─► Success? → Use LLM advice
    │
    └─► Failed? → Use rule-based fallback
         │
         ├─► Check if healthy/diseased
         ├─► Provide basic recommendations
         └─► Suggest consulting expert
```

---

## File Organization

```
plant-disease-detection/
│
├── Core Components
│   ├── plant_disease_cnn.py       # CNN model (MobileNetV2)
│   ├── plant_disease_llm.py       # LLM client (Ollama)
│   └── plant_disease_pipeline.py  # Complete pipeline
│
├── Interfaces
│   ├── app.py                      # Streamlit web UI
│   └── cli.py                      # Command-line tool
│
├── Training & Testing
│   ├── train.py                    # Model training script
│   └── test_system.py              # Installation tester
│
├── Documentation
│   ├── README.md                   # Full documentation
│   ├── SETUP.md                    # Quick setup guide
│   └── ARCHITECTURE.md             # This file
│
└── Configuration
    └── requirements.txt            # Python dependencies
```

---

## Deployment Options

### Option 1: Local Development
```
Python 3.8+
    ├─► Install dependencies
    ├─► Run Ollama locally
    └─► Start Streamlit/CLI
```

### Option 2: Cloud Deployment
```
Server (2GB RAM minimum)
    ├─► Install PyTorch (CPU)
    ├─► Install Ollama
    ├─► Deploy as web service
    └─► nginx → Streamlit
```

### Option 3: Mobile App (Future)
```
React Native
    ├─► Export model to ONNX/CoreML
    ├─► On-device inference
    └─► Cloud LLM (optional)
```

### Option 4: API Service
```
FastAPI Backend
    ├─► /predict endpoint (CNN)
    ├─► /advice endpoint (LLM)
    └─► /analyze endpoint (full pipeline)
```

---

## Performance Characteristics

### CNN Inference
- **CPU:** ~50ms per image
- **GPU:** ~5ms per image
- **Memory:** 200MB RAM
- **Batch:** ~100 images/sec (GPU)

### LLM Generation
- **Latency:** 2-5 seconds
- **Memory:** 3GB RAM (llama3.2:3b)
- **Throughput:** ~30 tokens/sec
- **Context:** 8K tokens

### Complete Pipeline
- **Total time:** 3-6 seconds
- **Memory:** 3.5GB total
- **Concurrent:** 5-10 users (8GB RAM)

---

## Scalability Considerations

### Horizontal Scaling
```
Load Balancer
    │
    ├─► CNN Server 1 (GPU)
    ├─► CNN Server 2 (GPU)
    ├─► CNN Server 3 (GPU)
    │
    └─► Ollama Cluster
         ├─► LLM Instance 1
         ├─► LLM Instance 2
         └─► LLM Instance 3
```

### Optimization Strategies
1. **CNN:**
   - Model quantization (INT8)
   - TensorRT/ONNX Runtime
   - Batch processing
   - Model distillation

2. **LLM:**
   - Response caching
   - Smaller models (1B params)
   - Prompt optimization
   - Async processing

3. **Infrastructure:**
   - CDN for static assets
   - Redis for caching
   - Queue system (Celery)
   - Database for results

---

## Security & Privacy

### Data Handling
```
User Image
    │
    ├─► Process in memory (no storage)
    ├─► Delete after analysis
    └─► No personally identifiable info
```

### Local-First Design
- CNN runs locally (PyTorch)
- LLM runs locally (Ollama)
- No external API calls
- No data transmission
- Full privacy guarantee

### Production Considerations
- HTTPS for web deployment
- Input validation (file size, type)
- Rate limiting
- Error handling
- Logging (no sensitive data)

---

## Future Enhancements

### Technical
- [ ] Explainable AI (Grad-CAM visualizations)
- [ ] Multi-disease detection
- [ ] Severity scoring
- [ ] Temporal tracking
- [ ] Weather integration

### Features
- [ ] Multilingual support (10+ languages)
- [ ] Voice input/output
- [ ] Mobile app
- [ ] Offline mode (fully cached)
- [ ] Community database

### Models
- [ ] EfficientNet-B0 (better accuracy)
- [ ] Custom lightweight model
- [ ] Ensemble predictions
- [ ] Active learning

---

## References

**CNN Architecture:**
- MobileNetV2: https://arxiv.org/abs/1801.04381
- Transfer Learning: https://cs231n.github.io/transfer-learning/

**LLM:**
- Ollama: https://ollama.com
- Llama 3.2: https://ai.meta.com/llama/

**Frameworks:**
- PyTorch: https://pytorch.org
- Streamlit: https://streamlit.io

---

**Last Updated:** 2024
**Version:** 1.0
**Author:** Your Name
