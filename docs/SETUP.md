# 🚀 QUICK SETUP GUIDE

## Step 1: Install Python Packages

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

For GPU support (optional):
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

---

## Step 2: Install Ollama (LLM)

### Linux/macOS:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows:
Download from: https://ollama.com/download

---

## Step 3: Start Ollama & Pull Model

```bash
# Start Ollama server (keep this running)
ollama serve

# In a new terminal, pull the model
ollama pull llama3.2:3b
```

**Alternative models:**
- `llama3.2:1b` - Lighter (1GB RAM)
- `mistral` - Alternative (7B)
- `llama3.2:3b` - Recommended (3GB RAM)

---

## Step 4: Test Installation

```bash
python test_system.py
```

This will verify:
- ✓ All packages installed
- ✓ PyTorch working
- ✓ Model loads correctly
- ✓ Ollama connected
- ✓ Pipeline functional

---

## Step 5: Run the System

### Option A: Web Interface (Recommended)
```bash
streamlit run app.py
```
Open browser to: http://localhost:8501

### Option B: Command Line
```bash
# Analyze single image
python cli.py image.jpg

# Analyze folder
python cli.py --folder images/

# Interactive mode
python cli.py --interactive

# Run with options
python cli.py image.jpg --save --confidence 0.8
```

### Option C: Python Script
```python
from plant_disease_pipeline import PlantDiseaseAssistant

assistant = PlantDiseaseAssistant()
result = assistant.analyze_and_display('leaf.jpg')
```

---

## ⚡ Quick Test (No Setup)

Even without Ollama, you can test the CNN:

```python
from plant_disease_cnn import PlantDiseaseCNN

model = PlantDiseaseCNN()
result = model.predict('leaf_image.jpg')
print(result)
```

The system will use fallback advice if Ollama is not running.

---

## 🔧 Troubleshooting

**Problem:** "Cannot connect to Ollama"
```bash
# Solution: Make sure Ollama is running
ollama serve
```

**Problem:** "Out of memory"
```python
# Solution: Use CPU-only mode
# PyTorch will automatically use CPU if CUDA unavailable
```

**Problem:** "Model not found"
```bash
# Solution: Pull the model
ollama pull llama3.2:3b
```

**Problem:** "ModuleNotFoundError"
```bash
# Solution: Install requirements
pip install -r requirements.txt
```

---

## 📦 What's Included

1. **plant_disease_cnn.py** - MobileNetV2 model
2. **plant_disease_llm.py** - Ollama integration
3. **plant_disease_pipeline.py** - Complete pipeline
4. **app.py** - Streamlit web interface
5. **cli.py** - Command-line interface
6. **train.py** - Training script
7. **test_system.py** - Installation tester
8. **README.md** - Full documentation

---

## 🎯 Next Steps

1. **Test with your images:**
   ```bash
   streamlit run app.py
   ```

2. **Train on your dataset:**
   ```bash
   python train.py
   ```

3. **Customize the system:**
   - Edit class names in `plant_disease_cnn.py`
   - Adjust prompts in `plant_disease_llm.py`
   - Modify UI in `app.py`

---

## 💡 Pro Tips

- Use good quality, well-lit leaf images
- Center the diseased area in the photo
- Avoid images with multiple diseases
- Start with confidence threshold = 0.7
- Train for at least 10 epochs

---

## 🆘 Need Help?

1. Run `python test_system.py` to diagnose issues
2. Check the README.md for detailed docs
3. Review error messages carefully
4. Make sure Ollama is running for LLM features

---

**Ready to detect plant diseases! 🌿**
