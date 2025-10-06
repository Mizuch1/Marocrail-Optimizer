// Language translations for MarocRail Optimizer
const translations = {
    en: {
        // Navigation
        dashboard: "Dashboard",
        schedules: "Schedules",
        analytics: "Analytics",
        predict: "Predict",
        
        // Index page
        appTitle: "MarocRail Optimizer",
        appSubtitle: "Smart Train Schedule Optimizer for Moroccan Railways",
        systemRunning: "✓ System Running",
        mlDescription: "ML-powered delay prediction and schedule optimization system with interactive dashboard",
        openDashboard: "Open Dashboard",
        
        // Dashboard
        systemOverview: "System Overview",
        totalStations: "Total Stations",
        totalRoutes: "Total Routes",
        activeTrains: "Active Trains",
        onTimeRate: "On-Time Rate",
        recentDelays: "Recent Delays",
        todaySchedules: "Today's Schedules",
        train: "Train",
        route: "Route",
        delay: "Delay",
        reason: "Reason",
        weather: "Weather",
        departure: "Departure",
        platform: "Platform",
        status: "Status",
        loading: "Loading...",
        noDelaysFound: "No delays found",
        noSchedulesFound: "No schedules found",
        failedToLoad: "Failed to load",
        
        // Analytics
        delayAnalytics: "Delay Analytics",
        delaysByReason: "Delays by Reason",
        delaysByHour: "Delays by Hour of Day",
        delaysByWeather: "Delays by Weather Condition",
        
        // Predict
        delayPrediction: "Delay Prediction",
        trainParameters: "Train Parameters",
        hourOfDay: "Hour of Day",
        dayOfWeek: "Day of Week",
        monday: "Monday",
        tuesday: "Tuesday",
        wednesday: "Wednesday",
        thursday: "Thursday",
        friday: "Friday",
        saturday: "Saturday",
        sunday: "Sunday",
        weatherCondition: "Weather Condition",
        sunny: "Sunny",
        cloudy: "Cloudy",
        rainy: "Rainy",
        foggy: "Foggy",
        hot: "Hot",
        trainType: "Train Type",
        highSpeed: "Al Boraq (High-speed)",
        fast: "TNR (Fast)",
        regular: "Regular",
        distance: "Distance (km)",
        duration: "Duration (minutes)",
        trainCapacity: "Train Capacity",
        predictDelay: "Predict Delay",
        predictionResult: "Prediction Result",
        delayProbability: "Delay Probability",
        riskLevel: "Risk Level",
        high: "High",
        medium: "Medium",
        low: "Low",
        estimatedDelay: "Estimated Delay",
        minutes: "minutes",
        recommendation: "Recommendation",
        highRiskMsg: "High delay risk. Consider schedule adjustment.",
        mediumRiskMsg: "Moderate delay risk. Monitor conditions.",
        lowRiskMsg: "Low delay risk. Normal operation expected.",
        
        // Schedules
        trainSchedules: "Train Schedules",
        type: "Type",
        arrival: "Arrival",
        capacity: "Capacity",
        loadSchedules: "Load Schedules",
        selectDay: "Select a day and click Load",
        showing: "Showing",
        schedulesFor: "schedules for",
        
        // Status badges
        scheduled: "Scheduled",
        delayed: "Delayed",
        cancelled: "Cancelled"
    },
    fr: {
        // Navigation
        dashboard: "Tableau de bord",
        schedules: "Horaires",
        analytics: "Analytique",
        predict: "Prédire",
        
        // Index page
        appTitle: "MarocRail Optimizer",
        appSubtitle: "Optimiseur intelligent d'horaires de trains pour les chemins de fer marocains",
        systemRunning: "✓ Système en marche",
        mlDescription: "Système de prédiction des retards et d'optimisation des horaires alimenté par l'IA avec tableau de bord interactif",
        openDashboard: "Ouvrir le tableau de bord",
        
        // Dashboard
        systemOverview: "Vue d'ensemble du système",
        totalStations: "Stations totales",
        totalRoutes: "Itinéraires totaux",
        activeTrains: "Trains actifs",
        onTimeRate: "Taux de ponctualité",
        recentDelays: "Retards récents",
        todaySchedules: "Horaires d'aujourd'hui",
        train: "Train",
        route: "Itinéraire",
        delay: "Retard",
        reason: "Raison",
        weather: "Météo",
        departure: "Départ",
        platform: "Quai",
        status: "Statut",
        loading: "Chargement...",
        noDelaysFound: "Aucun retard trouvé",
        noSchedulesFound: "Aucun horaire trouvé",
        failedToLoad: "Échec du chargement",
        
        // Analytics
        delayAnalytics: "Analytique des retards",
        delaysByReason: "Retards par raison",
        delaysByHour: "Retards par heure de la journée",
        delaysByWeather: "Retards par condition météorologique",
        
        // Predict
        delayPrediction: "Prédiction de retard",
        trainParameters: "Paramètres du train",
        hourOfDay: "Heure de la journée",
        dayOfWeek: "Jour de la semaine",
        monday: "Lundi",
        tuesday: "Mardi",
        wednesday: "Mercredi",
        thursday: "Jeudi",
        friday: "Vendredi",
        saturday: "Samedi",
        sunday: "Dimanche",
        weatherCondition: "Condition météorologique",
        sunny: "Ensoleillé",
        cloudy: "Nuageux",
        rainy: "Pluvieux",
        foggy: "Brumeux",
        hot: "Chaud",
        trainType: "Type de train",
        highSpeed: "Al Boraq (Grande vitesse)",
        fast: "TNR (Rapide)",
        regular: "Régulier",
        distance: "Distance (km)",
        duration: "Durée (minutes)",
        trainCapacity: "Capacité du train",
        predictDelay: "Prédire le retard",
        predictionResult: "Résultat de la prédiction",
        delayProbability: "Probabilité de retard",
        riskLevel: "Niveau de risque",
        high: "Élevé",
        medium: "Moyen",
        low: "Faible",
        estimatedDelay: "Retard estimé",
        minutes: "minutes",
        recommendation: "Recommandation",
        highRiskMsg: "Risque de retard élevé. Envisager un ajustement de l'horaire.",
        mediumRiskMsg: "Risque de retard modéré. Surveiller les conditions.",
        lowRiskMsg: "Faible risque de retard. Fonctionnement normal prévu.",
        
        // Schedules
        trainSchedules: "Horaires des trains",
        type: "Type",
        arrival: "Arrivée",
        capacity: "Capacité",
        loadSchedules: "Charger les horaires",
        selectDay: "Sélectionnez un jour et cliquez sur Charger",
        showing: "Affichage de",
        schedulesFor: "horaires pour",
        
        // Status badges
        scheduled: "Prévu",
        delayed: "Retardé",
        cancelled: "Annulé"
    }
};

// Get current language from localStorage or default to English
let currentLanguage = localStorage.getItem('language') || 'en';

// Function to change language
function changeLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('language', lang);
    translatePage();
    
    // Update active button state
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-lang="${lang}"]`)?.classList.add('active');
}

// Function to translate the page
function translatePage() {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[currentLanguage] && translations[currentLanguage][key]) {
            element.textContent = translations[currentLanguage][key];
        }
    });
    
    // Translate placeholder attributes
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (translations[currentLanguage] && translations[currentLanguage][key]) {
            element.placeholder = translations[currentLanguage][key];
        }
    });
}

// Initialize translation on page load
document.addEventListener('DOMContentLoaded', () => {
    translatePage();
    
    // Set active button
    document.querySelector(`[data-lang="${currentLanguage}"]`)?.classList.add('active');
});
