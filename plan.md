## Project Overview
I want to build a Smart Train Schedule Optimizer for Moroccan railways (ONCF-inspired). This is a portfolio project using 100% synthetic data - no real APIs or enterprise resources needed. The system should predict delays and optimize train schedules to minimize conflicts and maximize efficiency.

app name :"MarocRail-Optimizer"

## Core Objectives
1.  Create a professional-looking railway scheduling system.
2.  Use machine learning to predict delays.
3.  Optimize schedules automatically to reduce conflicts.
4.  Build an interactive web dashboard to visualize results.
5.  Generate all data synthetically based on realistic patterns.

## Technical Stack
*   **Backend**: Python with Flask framework
*   **Database**: SQLite (simple, file-based, no server needed)
*   **Data Processing**: Pandas for data manipulation
*   **Machine Learning**: Scikit-learn for delay prediction models
*   **Frontend**: HTML, CSS, JavaScript (vanilla or simple library)
*   **Visualization**: Chart.js or Plotly for graphs and charts

## Detailed Requirements

### Phase 1: Data Generation 

#### 1.1 Railway Network Data
Create synthetic data for the Moroccan railway network including:
*   **Stations**: Casa-Port, Casa-Voyageurs, Rabat-Ville, Rabat-Agdal, Kenitra, Meknès, Fès, Marrakech, Tanger, Oujda.
*   **Routes**: Define realistic connections between stations.
    *   Casa-Port to Rabat-Ville: 91 km, ~50 minutes
    *   Rabat-Ville to Fès: 206 km, ~2.5 hours
    *   Casa-Voyageurs to Marrakech: 237 km, ~3 hours
    *   Casa-Port to Tanger: ~350 km, ~4.5 hours
*   **Train Types**:
    *   Al Boraq (high-speed): 300+ km/h, premium pricing
    *   TNR (fast): 160 km/h, standard pricing
    *   Regular: 100 km/h, economy pricing

#### 1.2 Schedule Data
Generate realistic train schedules:
*   Peak hours: 6-9 AM, 5-8 PM (more frequent trains)
*   Off-peak hours: 10 AM-4 PM, 8 PM-6 AM (less frequent)
*   Daily schedules for each route
*   Typical departure/arrival times
*   Platform assignments
*   Train capacity (seats available)

#### 1.3 Historical Delay Data
Create patterns showing why delays happen:
*   **Weather delays**: Rain, fog, extreme heat (5-30 minute delays, 15% of trains)
*   **Technical issues**: Equipment failures (10-60 minute delays, 8% of trains)
*   **Passenger delays**: Boarding issues, medical emergencies (2-10 minute delays, 20% of trains)
*   **Track maintenance**: Scheduled/unscheduled (15-45 minute delays, 5% of trains)
*   **Cascade delays**: One delay causing others (cumulative effect)
*   **Time patterns**: More delays during rush hour and bad weather seasons

#### 1.4 Passenger Flow Data
Simulate passenger demand:
*   Busy routes: Casa-Rabat (business commuters), Casa-Marrakech (tourists)
*   Peak travel times: Morning/evening commutes, Friday/Sunday travel
*   Seasonal variations: Summer (tourism up), Ramadan (pattern changes)
*   Average passengers per train by route and time
*   Booking patterns (advance vs day-of)

### Phase 2: Database Design 

#### 2.1 Database Schema
Design SQLite database with these tables:

**Stations Table**:
*   station_id, name, city, coordinates (lat/long), platform_count, capacity

**Routes Table**:
*   route_id, origin_station_id, destination_station_id, distance_km, typical_duration_minutes

**Trains Table**:
*   train_id, train_type, capacity, operational_status

**Schedules Table**:
*   schedule_id, train_id, route_id, departure_time, arrival_time, platform, status, day_of_week

**Delays Table**:
*   delay_id, schedule_id, delay_minutes, delay_reason, weather_condition, timestamp, resolved

**Passengers Table**:
*   record_id, schedule_id, passenger_count, booking_date, travel_date

#### 2.2 Data Relationships
*   Each schedule links to one train and one route.
*   Each delay links to one schedule.
*   Each passenger record links to one schedule.
*   Maintain referential integrity.

### Phase 3: Machine Learning Model

#### 3.1 Delay Prediction Model
Build a model that predicts if a train will be delayed:

**Input Features**:
*   Time of day (hour, minute)
*   Day of week
*   Route information (distance, typical duration)
*   Weather conditions (sunny, rainy, foggy, hot)
*   Train type
*   Historical delay frequency on this route
*   Season/month
*   Is it a holiday or special event day
*   Previous train delays on same route (cascade effect)
*   Passenger load (overcrowding risk)

**Output**:
*   Probability of delay (0-100%)
*   Expected delay duration (minutes)
*   Confidence level

**Model Type**:
*   Start with Random Forest Classifier/Regressor.
*   Consider Gradient Boosting if accuracy needs improvement.
*   Split data: 80% training, 20% testing.
*   Evaluate with accuracy, precision, recall, MAE (mean absolute error).

#### 3.2 Model Training Process
*   Load historical delay data from database.
*   Engineer features from raw data.
*   Handle missing values and outliers.
*   Normalize/standardize numerical features.
*   Encode categorical features (one-hot encoding).
*   Train model and tune hyperparameters.
*   Save trained model to file for reuse.
*   Generate performance metrics and visualizations.

### Phase 4: Schedule Optimization Algorithm ( 3-4)

#### 4.1 Optimization Goals
Create an algorithm that optimizes schedules by:
*   **Minimizing delays**: Identify and resolve scheduling conflicts.
*   **Maximizing capacity utilization**: Fill trains efficiently.
*   **Reducing cascade effects**: Space out trains to prevent domino delays.
*   **Balancing resources**: Distribute trains and platforms evenly.

#### 4.2 Conflict Detection
Identify these scheduling conflicts:
*   **Platform conflicts**: Two trains at same platform at overlapping times.
*   **Train conflicts**: Same train scheduled in two places simultaneously.
*   **Maintenance windows**: Trains scheduled during track maintenance.
*   **Insufficient turnaround time**: Train doesn't have enough time between trips.
*   **Overcrowding risk**: Passenger demand exceeds train capacity.

#### 4.3 Optimization Logic
Algorithm should:
1.  Load current schedule from database.
2.  Run delay prediction model on all scheduled trains.
3.  Identify high-risk trains (>70% delay probability).
4.  Detect scheduling conflicts.
5.  Propose solutions:
    *   Adjust departure times by 5-15 minutes.
    *   Reassign platforms.
    *   Swap train types (use higher capacity train).
    *   Add buffer time between connections.
    *   Cancel/merge low-demand trains.
6.  Calculate optimization score (compare before/after).
7.  Generate optimized schedule.

#### 4.4 Optimization Metrics
Measure improvement with:
*   Total predicted delay reduction (percentage)
*   Number of conflicts resolved
*   Passenger satisfaction score (based on capacity vs demand)
*   Platform utilization efficiency
*   Cost savings estimate

### Phase 5: Web Dashboard (4-5)

#### 5.1 Dashboard Pages

**Home/Overview Page**:
*   Network map showing all stations and routes.
*   Real-time schedule status (on-time, delayed, cancelled).
*   Key metrics: trains operating, average delay, on-time percentage.
*   Quick stats cards with icons.

**Schedule Viewer Page**:
*   Filterable train schedule table.
*   Filter by: route, time, train type, status.
*   Search functionality.
*   Color-coded status (green=on-time, yellow=slight delay, red=major delay).
*   Click train to see details.

**Delay Analytics Page**:
*   Charts showing delay patterns:
    *   Delays by time of day (bar chart)
    *   Delays by reason (pie chart)
    *   Delay trends over time (line chart)
    *   Route comparison (horizontal bar chart)
*   Filter by date range, route, train type.

**Optimization Page**:
*   Show current schedule vs optimized schedule side-by-side.
*   Highlight changes made by optimizer.
*   Display optimization metrics (before/after comparison).
*   "Run Optimization" button to trigger algorithm.
*   Export optimized schedule.

**Prediction Page**:
*   Input form to predict delays for specific trains:
    *   Select route
    *   Select time
    *   Select weather conditions
    *   Select train type
*   Display prediction results with probability and explanation.
*   Show which factors contribute most to prediction.

#### 5.2 Visual Design
*   Use ONCF-inspired color scheme: Red (#E30613), white, blue accents.
*   Modern, clean interface with card-based layout.
*   Responsive design (works on mobile, tablet, desktop).
*   Include Moroccan railway imagery/styling.
*   Use icons for visual appeal.
*   Smooth transitions and animations.

#### 5.3 Interactive Features
*   Clickable map showing train locations (simulated real-time).
*   Tooltips showing details on hover.
*   Sortable and searchable tables.
*   Date range pickers for filtering.
*   Export data to CSV.
*   Print-friendly views.
*   Dark mode option (bonus).

### Phase 6: Backend API ( 5)

#### 6.1 Flask Routes/Endpoints

**GET /api/schedules**
*   Return all schedules or filtered schedules.
*   Parameters: date, route, status.
*   Returns: JSON array of schedule objects.

**GET /api/schedules/<schedule_id>**
*   Return specific schedule details.
*   Include related train, route, delay info.

**POST /api/predict-delay**
*   Accept schedule parameters.
*   Run ML model.
*   Return prediction results.

**POST /api/optimize-schedule**
*   Trigger optimization algorithm.
*   Return optimized schedule and metrics.

**GET /api/delays**
*   Return delay history.
*   Filter by date range, route, reason.

**GET /api/analytics**
*   Return aggregated statistics.
*   Delay patterns, route performance, etc.

**GET /api/stations**
*   Return all station information.

**GET /api/routes**
*   Return all routes with details.

#### 6.2 Backend Logic
*   Connect to SQLite database.
*   Validate input data.
*   Handle errors gracefully.
*   Return proper HTTP status codes.
*   Log important events.
*   Implement basic security (input sanitization).

### Phase 7: Advanced Features ( 6 - Optional)

#### 7.1 Weather Impact Simulation
*   Integrate weather scenarios into predictions.
*   Show how weather changes affect schedules.
*   Historical weather pattern correlation.

#### 7.2 Real-time Simulation
*   Simulate trains moving through the network.
*   Update positions every few seconds.
*   Show cascading delays in real-time.

#### 7.3 Maintenance Window Planning
*   Add maintenance schedule management.
*   Optimize maintenance timing to minimize impact.
*   Show which trains are affected by maintenance.

#### 7.4 Passenger Notifications
*   Simulate a notification system.
*   Alert for delays, platform changes, cancellations.
*   Show notification history.

#### 7.5 Multi-language Support
*   Add French and Arabic translations.
*   Language switcher in UI.
*   Properly formatted dates/times for locale.

### Phase 8: Documentation ( 6)

#### 8.1 README.md Structure
```
# Smart Train Schedule Optimizer

## Overview
Brief description, what problem it solves

## Features
- Delay prediction with 85%+ accuracy
- Automated schedule optimization
- Interactive dashboard
- Analytics and reporting

## Technology Stack
List all technologies used

## Installation
Step-by-step setup instructions

## Usage
How to run the application
How to use each feature

## Data Generation
Explain the synthetic data approach

## Model Performance
Show accuracy metrics, charts

## Screenshots
Include dashboard images

## Architecture
System architecture diagram

## Future Enhancements
Potential improvements

## License
MIT or your choice
```

#### 8.2 Code Documentation
*   Add docstrings to all functions.
*   Comment complex algorithms.
*   Include type hints in Python code.
*   Create architecture diagrams (system flow).

#### 8.3 Demo Materials
*   Record a 3-5 minute demo video showing:
    *   Dashboard walkthrough
    *   Running predictions
    *   Optimization in action
    *   Key features
*   Create presentation slides.
*   Prepare talking points for interviews.

### Phase 9: Testing & Quality (Ongoing)

#### 9.1 Testing Strategy
*   Test data generation scripts (verify realistic patterns).
*   Test ML model (check accuracy on test set).
*   Test optimization algorithm (verify improvements).
*   Test all API endpoints (correct responses).
*   Test UI in different browsers.
*   Test mobile responsiveness.

#### 9.2 Performance Optimization
*   Ensure page loads quickly (<2 seconds).
*   Optimize database queries (add indexes).
*   Cache frequently accessed data.
*   Minify CSS/JS files.
*   Optimize images.

### Phase 10: Local Setup and Execution

#### 10.1 Project Setup and Dependency Management
*   **Create `requirements.txt`**: List all Python dependencies (e.g., Flask, Pandas, Scikit-learn).
*   **Automate Installation**: Create a setup script (`check_and_install.py`) that automatically checks if the required packages are installed and installs them if they are missing. This ensures the application runs correctly in any local environment.

    *Example `check_and_install.py` script:*
    ```python
    import subprocess
    import sys

    def install_requirements():
        """
        Installs all packages listed in requirements.txt
        """
        try:
            print("Checking and installing dependencies...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("All dependencies are installed.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            sys.exit(1)

    if __name__ == "__main__":
        install_requirements()

    ```
*   **Write `run.py` script**: Create a main script to start the application. This script should first call the dependency installer and then launch the Flask server.

    *Example `run.py` script:*
    ```python
    # run.py
    from check_and_install import install_requirements
    
    # First, ensure all dependencies are installed
    install_requirements()
    
    # Now, import and run the main Flask app
    from app import app # Assuming your Flask app instance is in 'app.py'

    if __name__ == "__main__":
        print("Starting Flask application...")
        app.run(debug=True, port=5000)

    ```
*   **Update README**: The "Installation" section of your README.md should instruct the user to simply run `python run.py`.
*   **Test on a Fresh Environment**: Verify that your setup scripts work correctly on a machine or in a virtual environment that does not have the dependencies pre-installed.
*   **Document Configuration**: Clearly document the port number and any other local configurations in the README file.

## Deliverables Checklist

### Code
*   [ ] Complete synthetic data generation scripts
*   [ ] SQLite database with schema and sample data
*   [ ] Trained ML model for delay prediction
*   [ ] Schedule optimization algorithm
*   [ ] Flask backend with all API endpoints
*   [ ] Complete web dashboard (all pages)
*   [ ] CSS styling (professional appearance)
*   [ ] JavaScript for interactivity
*   [ ] Automated setup and runner scripts

### Documentation
*   [ ] Comprehensive README.md
*   [ ] Code comments and docstrings
*   [ ] Architecture diagrams
*   [ ] Clear installation and usage guide for local execution

### Demo Materials
*   [ ] Screenshots of all major features
*   [ ] Demo video (3-5 minutes)
*   [ ] Performance metrics report
*   [ ] Sample outputs (charts, optimized schedules)

### Portfolio
*   [ ] GitHub repository with clean structure
*   [ ] LinkedIn/Resume bullet points
*   [ ] Project description for portfolio website

## Success Metrics

Your project is successful if:
*   ✅ ML model achieves >80% accuracy in delay prediction.
*   ✅ Optimization algorithm reduces predicted delays by >15%.
*   ✅ Dashboard is visually appealing and fully functional.
*   ✅ All features work without errors.
*   ✅ Code is clean, documented, and well-organized.
*   ✅ Documentation is comprehensive and professional.
*   ✅ Demo effectively showcases capabilities.
*   ✅ Project runs smoothly on a fresh local installation using the run script.

## Interview Talking Points

Be prepared to discuss:
1.  **Technical challenges**: How you handled cascade delays, optimization trade-offs.
2.  **ML approach**: Why Random Forest, how you validated, feature importance.
3.  **Data strategy**: How you created realistic synthetic data.
4.  **Scalability**: How the system could handle real data and more routes.
5.  **Real-world application**: How ONCF could actually use this.
6.  **Trade-offs made**: What you'd do differently with more time/resources.

## Timeline Summary (30-40 Days - Internship Project)

### Week 1-2 (Days 1-14): Foundation & Data
*   **Days 1-3**: Project setup, data generation scripts
*   **Days 4-7**: Database design and synthetic data loading
*   **Days 8-10**: Data validation and quality checks
*   **Days 11-14**: ML model development and training

### Week 3-4 (Days 15-28): Core Features
*   **Days 15-18**: Simplified optimization algorithm (heuristic-based)
*   **Days 19-22**: Flask backend API development
*   **Days 23-28**: Web dashboard (3 core pages: Overview, Schedule Viewer, Analytics)

### Week 5-6 (Days 29-40): Polish & Delivery
*   **Days 29-32**: French language integration
*   **Days 33-35**: Testing, bug fixes, performance optimization
*   **Days 36-38**: Documentation (README, code comments, architecture)
*   **Days 39-40**: Demo materials (video, screenshots, final polish)

**Data Volume (Optimized for ML Training)**:
- 10 stations
- 25 routes
- 80 trains (mixed types)
- 600-800 daily schedules
- 6 months historical data (~8,000-10,000 delay records)
- ~15,000-20,000 passenger flow records

**Simplified Approach**:
- Use heuristic-based optimization (rule-based conflict resolution)
- Focus on core features first, advanced features as time permits
- French language only (Arabic dropped for scope management)
- Responsive design but mobile-optimized later if time allows

logo image if u need it : data:image/png;base64,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

and oncf train logo : data:image/png;base64,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