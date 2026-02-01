# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies (2 minutes)

```bash
cd /Users/junyi.yao/Desktop/Xai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 2: Setup API Key (1 minute)

1. Go to [console.x.ai](https://console.x.ai)
2. Get your API key
3. Redeem promo code: `grok_eng_9a9e9f2a` for $20 free credits
   - Navigate: Manage → Billing → Free credits → Redeem promo code

4. Create `.env` file:
```bash
cat > .env << EOF
XAI_API_KEY=your_api_key_here
EOF
```

### Step 3: Verify Setup (1 minute)

```bash
# Test imports and data
python3 test_imports.py

# Should show:
# ✓ Grok imports successful
# ✓ Agent imports successful
# ✓ Tools imports successful
# ✓ data files exist
```

### Step 4: Run Your First Query! (1 minute)

```bash
# Try a simple query
python main.py --query "What are users saying about AI safety on X?"
```

## 🎯 Next Steps

### Interactive Mode
```bash
python main.py --interactive
```

### Run Benchmark
```bash
# Test on 5 queries
python evaluation/run_benchmark.py --max-queries 5
```

### Compare Models
```bash
# Compare different Grok variants
python evaluation/compare_models.py --max-queries 3
```

## 📊 Sample Queries to Try

```bash
# Sentiment analysis
python main.py --query "Analyze sentiment trends about climate change"

# Research comparison
python main.py --query "Compare quantum computing methodologies from 2020 vs 2025"

# Citation analysis
python main.py --query "Find the most influential machine learning papers"

# Cross-domain
python main.py --query "How does X discourse on biotechnology compare to academic research?"
```

## 🐳 Docker Alternative

If you prefer Docker:

```bash
# Build
docker-compose build

# Run
docker-compose up
```

## 📚 Full Documentation

- **README.md** - Project overview
- **SETUP.md** - Detailed setup instructions
- **TECHNICAL.md** - Architecture and design
- **TROUBLESHOOTING.md** - Common issues
- **DEMO.md** - Video demo guide

## ✅ System Requirements

- Python 3.10+
- 4GB RAM minimum
- Internet connection (for Grok API)
- ~2GB disk space (for dependencies and datasets)

## 🆘 Getting Help

If you encounter issues:
1. Check `TROUBLESHOOTING.md`
2. Verify API key is set correctly
3. Ensure virtual environment is activated
4. Try regenerating datasets: `python scripts/generate_datasets.py`

---

**Ready to research!** 🎉

