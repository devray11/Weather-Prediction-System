// AtmoSense Real-Time Data Integration Script
// Add this to your existing index.html file to enable live ThingSpeak data

// Global variables for data management
let dataUpdateInterval;
let lastUpdateTime = 0;
let connectionStatus = 'connecting';

// Function to fetch and update real-time data from ThingSpeak
async function updateDashboardData() {
    try {
        const response = await fetch('/api/current-data');
        const result = await response.json();
        
        if (result.success && result.data) {
            const data = result.data;
            
            // Update temperature display with color coding
            updateTemperatureDisplay(data.temperature);
            
            // Update humidity display
            updateHumidityDisplay(data.humidity);
            
            // Update air quality display (convert gas_level to AQI)
            updateAirQualityDisplay(data.gas_level);
            
            // Update connection status
            updateConnectionStatus(data.status);
            
            // Log successful update
            console.log('✅ Dashboard updated with live ThingSpeak data:', {
                temp: data.temperature + '°C',
                humidity: data.humidity + '%',
                gas: data.gas_level + ' PPM',
                status: data.status
            });
            
            lastUpdateTime = Date.now();
            
        } else {
            throw new Error('Invalid response from server');
        }
    } catch (error) {
        console.error('❌ Failed to update dashboard data:', error);
        updateConnectionStatus('error');
    }
}

// Update temperature display with dynamic color coding
function updateTemperatureDisplay(temperature) {
    const tempElement = document.getElementById('temp-value');
    if (tempElement) {
        tempElement.textContent = Math.round(temperature);
        
        // Apply color coding based on temperature ranges
        tempElement.classList.remove('temp-cold', 'temp-normal', 'temp-hot');
        
        if (temperature < 15) {
            tempElement.classList.add('temp-cold');
        } else if (temperature >= 15 && temperature <= 29) {
            tempElement.classList.add('temp-normal');
        } else {
            tempElement.classList.add('temp-hot');
        }
    }
}

// Update humidity display
function updateHumidityDisplay(humidity) {
    const humidityElement = document.getElementById('humidity-value');
    if (humidityElement) {
        humidityElement.textContent = Math.round(humidity);
    }
}

// Update air quality display (convert PPM to AQI approximation)
function updateAirQualityDisplay(gasLevel) {
    const airQualityElement = document.getElementById('air-quality-value');
    if (airQualityElement) {
        // Convert gas sensor PPM to AQI approximation
        // This is a simplified conversion - adjust based on your sensor calibration
        let aqi;
        if (gasLevel <= 150) {
            aqi = Math.round(gasLevel / 3); // Good air quality
        } else if (gasLevel <= 300) {
            aqi = Math.round(50 + (gasLevel - 150) / 3); // Moderate
        } else {
            aqi = Math.round(100 + (gasLevel - 300) / 5); // Poor
        }
        
        aqi = Math.min(aqi, 500); // Cap at 500 AQI
        airQualityElement.textContent = aqi;
        
        // Update color based on AQI level
        const parentCard = airQualityElement.closest('.neu-card');
        if (parentCard) {
            const icon = parentCard.querySelector('[data-lucide="wind"]');
            if (icon) {
                icon.classList.remove('text-emerald-500', 'text-yellow-500', 'text-red-500');
                if (aqi <= 50) {
                    icon.classList.add('text-emerald-500'); // Good
                } else if (aqi <= 100) {
                    icon.classList.add('text-yellow-500'); // Moderate
                } else {
                    icon.classList.add('text-red-500'); // Poor
                }
            }
        }
    }
}

// Update connection status indicator
function updateConnectionStatus(status) {
    connectionStatus = status;
    
    let statusIndicator = document.getElementById('connection-status');
    if (!statusIndicator) {
        // Create status indicator if it doesn't exist
        statusIndicator = document.createElement('div');
        statusIndicator.id = 'connection-status';
        statusIndicator.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            padding: 8px 16px;
            border-radius: 25px;
            font-size: 12px;
            font-weight: 600;
            z-index: 1000;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        document.body.appendChild(statusIndicator);
    }
    
    // Update status display based on connection state
    switch(status) {
        case 'connected':
            statusIndicator.innerHTML = '🟢 Live Data';
            statusIndicator.style.background = 'rgba(16, 185, 129, 0.9)';
            statusIndicator.style.color = 'white';
            statusIndicator.style.border = '1px solid rgba(16, 185, 129, 0.3)';
            break;
        case 'no_data':
            statusIndicator.innerHTML = '🟡 No Sensor Data';
            statusIndicator.style.background = 'rgba(245, 158, 11, 0.9)';
            statusIndicator.style.color = 'white';
            statusIndicator.style.border = '1px solid rgba(245, 158, 11, 0.3)';
            break;
        case 'connecting':
            statusIndicator.innerHTML = '🔄 Connecting...';
            statusIndicator.style.background = 'rgba(59, 130, 246, 0.9)';
            statusIndicator.style.color = 'white';
            statusIndicator.style.border = '1px solid rgba(59, 130, 246, 0.3)';
            break;
        default:
            statusIndicator.innerHTML = '🔴 Connection Error';
            statusIndicator.style.background = 'rgba(239, 68, 68, 0.9)';
            statusIndicator.style.color = 'white';
            statusIndicator.style.border = '1px solid rgba(239, 68, 68, 0.3)';
            break;
    }
}

// Fetch system status and display additional info
async function updateSystemStatus() {
    try {
        const response = await fetch('/api/system-status');
        const result = await response.json();
        
        if (result.success) {
            console.log('📊 System Status:', result.status);
            
            // You can add more status indicators here if needed
            if (result.status.channel_id) {
                console.log(`🔗 ThingSpeak Channel ID: ${result.status.channel_id}`);
            }
        }
    } catch (error) {
        console.warn('⚠️ Could not fetch system status:', error);
    }
}

// Initialize real-time data integration
function initializeAtmoSenseData() {
    console.log('🚀 Initializing AtmoSense Real-Time Data Integration...');
    console.log('📡 ThingSpeak API Key: 84OP68EGX1WSO1IM');
    
    // Set initial status
    updateConnectionStatus('connecting');
    
    // Initial data load
    updateDashboardData();
    
    // Initial system status check
    updateSystemStatus();
    
    // Set up periodic updates every 30 seconds
    dataUpdateInterval = setInterval(() => {
        updateDashboardData();
    }, 30000);
    
    // Set up system status updates every 5 minutes
    setInterval(() => {
        updateSystemStatus();
    }, 300000);
    
    console.log('✅ Real-time data integration active');
    console.log('🔄 Data updates every 30 seconds');
}

// Enhanced error handling and retry logic
function handleConnectionError() {
    console.log('🔄 Attempting to reconnect to ThingSpeak...');
    
    // Clear existing interval
    if (dataUpdateInterval) {
        clearInterval(dataUpdateInterval);
    }
    
    // Retry connection after 10 seconds
    setTimeout(() => {
        initializeAtmoSenseData();
    }, 10000);
}

// Add visual feedback for data updates
function showDataUpdateAnimation() {
    const cards = document.querySelectorAll('.neu-card');
    cards.forEach(card => {
        card.style.transform = 'scale(1.02)';
        setTimeout(() => {
            card.style.transform = '';
        }, 200);
    });
}

// Start the integration when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add some delay to ensure the page is fully loaded
    setTimeout(initializeAtmoSenseData, 1000);
});

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (dataUpdateInterval) {
        clearInterval(dataUpdateInterval);
    }
    console.log('🛑 AtmoSense data integration stopped');
});

// Add keyboard shortcut to manually refresh data (Ctrl+R)
document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'r') {
        event.preventDefault();
        console.log('🔄 Manual data refresh triggered');
        updateDashboardData();
        showDataUpdateAnimation();
    }
});

// Expose functions globally for debugging
window.AtmoSense = {
    updateData: updateDashboardData,
    getStatus: () => connectionStatus,
    getLastUpdate: () => lastUpdateTime,
    manualRefresh: () => {
        updateDashboardData();
        showDataUpdateAnimation();
    }
};

console.log('📱 AtmoSense integration script loaded successfully');
console.log('🎮 Use AtmoSense.manualRefresh() to manually update data');
console.log('⌨️ Press Ctrl+R to refresh data manually');