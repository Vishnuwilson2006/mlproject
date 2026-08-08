# Machine Learning-Based Surrogate Model for Circuit Performance Prediction

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2-green.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.2-orange.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)

> **Final Year ECE Project**  
> A full-stack Django web application that replaces computationally expensive SPICE differential equation solvers (LTspice/HSPICE) with a high-speed Random Forest surrogate model to predict key transistor circuit performance metrics: **Voltage Gain ($A_v$)**, **Cutoff Frequency ($f_c$)**, and **Phase Margin ($\phi_m$)**.

---

## 📌 Project Overview

Analog circuit optimization often requires running thousands of iterative SPICE simulations. Each simulation solves complex non-linear differential equations, leading to significant computation times. This project implements a **Machine Learning Surrogate Model** trained on **12,000+ physics-grounded synthetic samples**.

The surrogate model evaluates circuit parameters in sub-milliseconds with over **99% $R^2$ accuracy** for Voltage Gain.

---

## ⚡ Key Features

- 🏎️ **Instant Circuit Evaluation**: Predicts Gain (dB), Cutoff Frequency (Hz), and Phase Margin (°) in milliseconds.
- 🌲 **Multi-Output Random Forest Regressor**: Trained on 12,000 synthetic rows created via Small-Signal amplifier physics equations.
- 💾 **SQLite Database Log**: Stores every prediction with user mapping, timestamps, and input values.
- 📊 **Admin Analytics Dashboard**: Displays aggregate KPIs (Total Predictions, Avg Gain, Avg $f_c$, Avg Phase Margin), interactive Chart.js trend charts, and model evaluation metrics ($R^2$, MAE, RMSE).
- 🔐 **User Authentication**: Login, Registration, and Logout with Bootstrap feedback cards.
- 🎨 **Modern Glassmorphic UI**: Responsive Bootstrap 5 layout with ambient gradients, loading animations, and demo presets.

---

## 📐 Circuit Topology & Physics Equations

The surrogate model predicts performance metrics for a **Common Emitter BJT Transistor Stage** defined by 6 passive input parameters:

### Input Features
- $R_1$: Upper base biasing resistor ($\Omega$)
- $R_2$: Lower base biasing resistor ($\Omega$)
- $R_C$: Collector load resistor ($\Omega$)
- $R_E$: Emitter stabilization resistor ($\Omega$)
- $C_1$: Input coupling capacitor ($\mu\text{F}$)
- $C_2$: Output coupling capacitor ($\mu\text{F}$)

### Output Target Labels
1. **Voltage Gain ($A_v$)**:
   $$A_v = 20 \log_{10} \left| \frac{R_C}{r_e + R_E} \right| \quad \text{where } r_e = \frac{26\text{mV}}{I_E}$$
2. **Cutoff Frequency ($f_c$)**:
   $$f_c \approx \frac{1}{2\pi (R_{eq1} C_1 + R_C C_2)}$$
3. **Phase Margin ($\phi_m$)**:
   $$\phi_m \approx 180^\circ - \sum \arctan\left(\frac{f}{f_{pole}}\right)$$

---

## 🛠️ Technology Stack

- **Backend**: Python 3.x, Django 4.2, SQLite
- **Machine Learning**: Pandas, NumPy, Scikit-learn, Joblib
- **Frontend**: HTML5, CSS3, Bootstrap 5.3, JavaScript, Chart.js

---

## 📂 Project Structure

```
mlproject/
│
├── generate_dataset.py       # Physics-based synthetic dataset generator (12,000 rows)
├── train_model.py            # ML surrogate training script & evaluation metrics logger
├── circuit_dataset.csv       # Generated dataset CSV
├── circuit_model.pkl         # Trained Joblib model pipeline
├── manage.py                 # Django administrative script
├── requirements.txt          # Python dependencies
├── seed_initial_data.py      # Seed script for initial database entries
│
├── circuit_project/          # Django Project Configuration
│   ├── __init__.py
│   ├── settings.py           # Database, apps, static & template paths
│   ├── urls.py               # Main URL router
│   └── wsgi.py               # WSGI entry point
│
└── surrogate_app/            # Main Application App
    ├── admin.py              # Custom Django Admin configuration
    ├── apps.py
    ├── forms.py              # Input validation and User Registration forms
    ├── models.py             # PredictionHistory SQLite model definition
    ├── urls.py               # Application sub-routing
    ├── views.py              # Prediction inference, history, dashboard & auth logic
    │
    ├── static/
    │   ├── css/custom.css    # Glassmorphism & dark gradient design system
    │   └── js/main.js        # Loading spinner & interactive triggers
    │
    └── templates/
        ├── base.html         # Navbar, footer, toasts, global layout
        ├── home.html         # Landing page & feature highlights
        ├── predict.html      # Interactive prediction form & output cards
        ├── history.html      # Searchable, paginated prediction log
        ├── dashboard.html    # Analytics dashboard & Chart.js visualizations
        ├── about.html        # ECE domain background & equations
        ├── contact.html      # Contact & project team details
        ├── login.html        # User login
        └── register.html     # User registration
```

---

## 🚀 Execution & Setup Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Synthetic Dataset (12,000 rows)
```bash
python generate_dataset.py
```
*Outputs `circuit_dataset.csv`.*

### 3. Train Machine Learning Surrogate Model
```bash
python train_model.py
```
*Evaluates R², MAE, RMSE metrics and exports `circuit_model.pkl`.*

### 4. Run Database Migrations
```bash
python manage.py makemigrations surrogate_app
python manage.py migrate
```

### 5. (Optional) Seed Initial Sample Predictions
```bash
python seed_initial_data.py
```

### 6. Start Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:8000/`**

---

## 📊 Model Performance Report

| Target Parameter | R² Score | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) |
|---|---|---|---|
| **Voltage Gain ($A_v$)** | **0.9942** | 0.4321 dB | 0.5992 dB |
| **Cutoff Frequency ($f_c$)** | **0.5842** | 0.2241 Hz | 2.0283 Hz |
| **Phase Margin ($\phi_m$)** | **0.9742** | 0.8520° | 1.2768° |

---

## 🏆 Project Completion & Verification

All project requirements have been fully generated, trained, migrated, and verified:
- [x] Synthetic dataset generated (`circuit_dataset.csv`, 12,000 rows)
- [x] Random Forest model trained & exported (`circuit_model.pkl`)
- [x] SQLite database schema created & migrated
- [x] Interactive Prediction form with validation & presets
- [x] Responsive Bootstrap 5 Glassmorphism UI
- [x] Prediction History log with search & pagination
- [x] Admin Analytics Dashboard with aggregate KPIs & Chart.js
- [x] User Authentication system (Register, Login, Logout)
