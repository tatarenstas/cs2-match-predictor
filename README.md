# 🧠 CS2 Match Predictor

A machine learning pipeline to **predict the winner of a Counter-Strike 2 match** based on match data 🎯  
This repository includes everything: scraping, feature engineering, model training, and prediction.

---

## 📁 Project Structure

```
CS2_github/
├── pipeline.py                   # Main pipeline (training + prediction)
│
├── model/
│   └── cs2_model.pkl             # Trained machine learning model
│
├── data/
│   ├── raw/                      # Raw scraped match data
│   │   └── matches_data.json
│   ├── processed/                
│   │   └── 2381361.json          # Processed match data (for inference)
│   └── urls/
│       └── processed_urls.json   # List of scraped URLs
│
├── src/
│   ├── scraping/
│   │   └── main.py               # Web scraping logic
│   │
│   ├── features/
│   │   └── prepare_match.py      # Convert raw match data into features
│   │
│   ├── training/
│   │   └── train.py              # Train the prediction model
│   │
│   └── prediction/
│       └── predict.py            # Predict match outcome
│
├── requirements.txt              # Project dependencies
└── README.md                     # Documentation (this file)
```

---

## ⚙️ How to Use

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Scrape match data**:
   ```bash
   python src/scraping/main.py
   ```

3. **Generate features from matches**:
   ```bash
   python src/features/prepare_match.py
   ```

4. **Train the model**:
   ```bash
   python src/training/train.py
   ```

5. **Run predictions**:
   ```bash
   python src/prediction/predict.py
   ```

Or run the full pipeline:
```bash
python pipeline.py
```

---

## 🧪 Technologies Used

- Python 🐍
- scikit-learn
- pandas, numpy, JSON
- Custom data pipeline
- Web scraping

---

## 📊 What Does the Model Do?

🔍 Takes match data as input  
🛠️ Extracts meaningful features  
🎓 Trains a machine learning model  
🧠 Predicts which team will win based on match features

---

## 🗂️ Data Structure

- **raw/** — Raw match data scraped from the web
- **processed/** — Cleaned and processed match data (for prediction)
- **urls/** — URLs that have already been scraped

---

## 🧑‍💻 Authors

Created with ❤️ by [@tatarenstas](https://github.com/tatarenstas)  
📬 Contact: [tatarenstas@gmail.com](mailto:tatarenstas@gmail.com)

---

## 🎮 GL HF!

> Good luck, have fun, and may your predictions be accurate! 🏆