# MediMind AI — Intelligent Healthcare Suite & National Health Resource Command Center

> **Google Cloud Hackathon Edition — Track 03: Smart Health & Supply Chain Resilience**  
> *"Solving for India: AI-powered public health supply chain resilience, demand forecasting, stock-out early warnings, and automated cross-district resource redistribution."*

---

## <img src="https://cdn-icons-png.flaticon.com/512/4320/4320371.png" width="20" height="20" style="vertical-align: middle;" /> Platform Architecture Overview

```
                                    MEDIMIND AI PLATFORM
                                             │
               ┌─────────────────────────────┴─────────────────────────────┐
               ▼                                                           ▼
     [CLINICAL SUITE (CITIZEN)]                              [NATIONAL COMMAND CENTER (TRACK 03)]
   • Health & Symptom Assessment                           • Public Health Telemetry & Facility Hierarchy
   • Medical Report & Rx OCR Analyzer                      • Essential Medicine Inventory (NLEM 2022)
   • Nearby Healthcare & Emergency Map                     • Predictive AI Demand Forecasting
   • Health Records & Clinical History                     • Stock-out Early Warning & Epidemic Stress Tests
   • About MediMind AI                                     • Smart Cross-District Redistribution Optimizer
                                                           • Workforce & Bed Capacity Intelligence
                                                           • National Health Geospatial Heatmap
                                                           • Federated Learning Simulation Node
```

---

## <img src="https://cdn-icons-png.flaticon.com/512/595/595764.png" width="20" height="20" style="vertical-align: middle;" /> Data Provenance & Source Transparency

| Data Dimension | Source Classification | Description / Standards |
|---|---|---|
| **Medicine Formulary** | **Real / Standard Reference** | NLEM 2022 (National List of Essential Medicines — Paracetamol, Amoxicillin, ORS, Insulin, Anti-venom, etc.) |
| **Facility Structure** | **Real / Standard Reference** | IPHS (Indian Public Health Standards) / MoHFW State $\to$ District $\to$ PHC/CHC Hierarchy |
| **Geographic & Routing** | **Real / Live API** | Google Maps Platform (Maps JS, Places, Geocoding) + Haversine Pre-filtering + Routes ETA |
| **Generative AI** | **Google AI / Live API** | Google Gemini API (gemini-1.5-flash) with localized prompts (English, Hindi, Gujarati) & offline fallback |
| **Operational Telemetry** | **Simulated Telemetry** | Simulated PHC inventory on hand, daily consumption rates, bed occupancy, staff attendance & outbreak spikes |
| **Federated Learning** | **Simulation Prototype** | State-level decentralized model training simulation with FedAvg model aggregation & differential privacy |

---

## 8 Core Sub-Modules in National Command Center

1. **<img src="https://cdn-icons-png.flaticon.com/512/404/404621.png" width="16" height="16" style="vertical-align: middle;" /> Network Overview & Infrastructure KPIs**:
   - Jurisdiction filtering: All India $\to$ 36 States/UTs $\to$ 146 Districts $\to$ 225 Facilities.
   - Outbreak stress scenario toggles: Baseline, Monsoon Dengue/Malaria, Heatwave Dehydration, Winter Respiratory, Himalayan Cold Wave, River Basin Flood, Coastal Cyclone.
   - Live metrics: Monitored Facilities, Formulary Health %, Bed Occupancy %, Doctor Attendance %.

2. **<img src="https://cdn-icons-png.flaticon.com/512/5228/5228598.png" width="16" height="16" style="vertical-align: middle;" /> Essential Medicine Inventory Tracker**:
   - Real-time stock, daily consumption burn rate, and Days of Inventory Remaining (DOIR).
   - Triage statuses: <img src="https://cdn-icons-png.flaticon.com/128/4381/4381635.png" width="12" height="12" style="vertical-align: middle;" /> Healthy ($>14$ days), <img src="https://cdn-icons-png.flaticon.com/512/12087/12087823.png" width="12" height="12" style="vertical-align: middle;" /> Warning ($5-14$ days), <img src="https://cdn-icons-png.flaticon.com/512/594/594739.png" width="12" height="12" style="vertical-align: middle;" /> Critical ($<5$ days).

3. **<img src="https://cdn-icons-png.flaticon.com/128/12512/12512364.png" width="16" height="16" style="vertical-align: middle;" /> Predictive AI Demand Forecasting**:
   - Multi-factor time-series demand forecasting (historical trend + seasonality + OPD surge + weather index).
   - Interactive Plotly fan charts with 95% confidence intervals and predicted zero-stock date.

4. **<img src="https://cdn-icons-png.flaticon.com/128/14658/14658441.png" width="16" height="16" style="vertical-align: middle;" /> Early Warning Center & Google Gemini Reasoning**:
   - Automated stock-out risk detection during emergencies.
   - Google Gemini generates root-cause analysis and actionable administrative guidance in English, Hindi (हिंदी), and Gujarati (ગુજરાતી).

5. **<img src="https://cdn-icons-png.flaticon.com/512/17514/17514906.png" width="16" height="16" style="vertical-align: middle;" /> Automated Cross-District Redistribution Optimizer**:
   - Two-stage logistics solver: Haversine distance pre-filter $\to$ Google Routes transit ETA calculation.
   - 1-Click **Approve & Dispatch**: Deducts donor stock, fulfills recipient deficit, and generates an official Government Health Resource Transfer Manifest.

6. **<img src="https://cdn-icons-png.flaticon.com/512/387/387561.png" width="16" height="16" style="vertical-align: middle;" /> Workforce & Bed Capacity Intelligence**:
   - Medical Officer, Staff Nurse, Pharmacist, and Lab Technician attendance tracking & deficit alarms.
   - Bed occupancy (General, ICU, Maternity, Oxygen-supported) with 7-day occupancy projections.

7. **<img src="https://cdn-icons-png.flaticon.com/128/486/486505.png" width="16" height="16" style="vertical-align: middle;" /> National Health Geospatial Map**:
   - Interactive Leaflet map with Marker Clustering color-coded by supply and capacity risk.

8. **<img src="https://cdn-icons-png.flaticon.com/512/16951/16951293.png" width="16" height="16" style="vertical-align: middle;" /> Federated Learning Simulation Node**:
   - State-level decentralized training simulation demonstrating privacy-preserving shared intelligence without centralizing raw data.

---

## <img src="https://cdn-icons-png.flaticon.com/512/3127/3127109.png" width="20" height="20" style="vertical-align: middle;" /> Verification & Testing

Run the automated test suite verifying all 10 supply chain, AI forecasting, redistribution, and map engines:

```bash
python verify_supply_chain.py
```

Expected output:
```
=======================================================
[SUCCESS] ALL 10 TEST SUITES PASSED FLAWLESSLY WITH 100% SUCCESS!
=======================================================
```

---

## <img src="https://cdn-icons-png.flaticon.com/512/13530/13530296.png" width="20" height="20" style="vertical-align: middle;" /> How to Run Locally

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys in `.env`**:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   GOOGLE_MAPS_API_KEY=your_google_maps_key
   ```

3. **Start the MediMind AI Platform**:
   ```bash
   streamlit run app.py
   ```

