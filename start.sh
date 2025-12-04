#!/bin/bash
#
# Raspberry Pi Smart Monitoring Kit - Startup Script
# Client: Yoshinori Ueda
#
# Usage:
#   ./start.sh          - Start monitoring system
#   ./start.sh --test   - Run sensor tests
#   ./start.sh --status - Check system status
#

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🏠 Raspberry Pi Smart Monitoring Kit                     ║"
echo "║     Client: Yoshinori Ueda                                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running on Raspberry Pi
check_raspberry_pi() {
    if [ -f /proc/device-tree/model ]; then
        MODEL=$(cat /proc/device-tree/model)
        echo -e "${GREEN}✅ Running on: $MODEL${NC}"
    else
        echo -e "${YELLOW}⚠️  Not running on Raspberry Pi (simulation mode)${NC}"
    fi
}

# Check Python version
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}❌ Python 3 not found!${NC}"
        exit 1
    fi
}

# Check LINE credentials
check_line_credentials() {
    if [ -n "$LINE_CHANNEL_ACCESS_TOKEN" ] && [ -n "$LINE_USER_ID" ]; then
        echo -e "${GREEN}✅ LINE credentials configured${NC}"
    else
        echo -e "${YELLOW}⚠️  LINE credentials not set (notifications disabled)${NC}"
        echo "   Set LINE_CHANNEL_ACCESS_TOKEN and LINE_USER_ID environment variables"
    fi
}

# Run sensor tests
run_tests() {
    echo ""
    echo "Running sensor tests..."
    echo ""
    
    echo "1. Testing PIR Motion Sensor..."
    python3 -c "from src.sensors.motion import MotionSensor; print('   ✅ Motion sensor module OK')" 2>/dev/null || echo "   ❌ Motion sensor module failed"
    
    echo "2. Testing Sound Sensor..."
    python3 -c "from src.sensors.sound import SoundSensor; print('   ✅ Sound sensor module OK')" 2>/dev/null || echo "   ❌ Sound sensor module failed"
    
    echo "3. Testing Door Sensor..."
    python3 -c "from src.sensors.door import DoorSensor; print('   ✅ Door sensor module OK')" 2>/dev/null || echo "   ❌ Door sensor module failed"
    
    echo "4. Testing Vibration Sensor..."
    python3 -c "from src.sensors.vibration import VibrationSensor; print('   ✅ Vibration sensor module OK')" 2>/dev/null || echo "   ❌ Vibration sensor module failed"
    
    echo "5. Testing Temperature Sensor..."
    python3 -c "from src.sensors.temperature import TemperatureSensor; print('   ✅ Temperature sensor module OK')" 2>/dev/null || echo "   ❌ Temperature sensor module failed"
    
    echo ""
    echo "6. Testing Monitoring System..."
    python3 -c "from src.monitoring import SensorHub, PatternEngine, AlertManager; print('   ✅ Monitoring system OK')" 2>/dev/null || echo "   ❌ Monitoring system failed"
    
    echo ""
    echo "Tests complete!"
}

# Show status
show_status() {
    echo ""
    echo "System Status:"
    echo ""
    check_raspberry_pi
    check_python
    check_line_credentials
    echo ""
}

# Start monitoring
start_monitoring() {
    echo ""
    check_raspberry_pi
    check_python
    check_line_credentials
    echo ""
    echo "Starting monitoring system..."
    echo ""
    
    python3 -m src.monitoring.monitor
}

# Main
case "${1:-}" in
    --test)
        run_tests
        ;;
    --status)
        show_status
        ;;
    --help)
        echo "Usage: $0 [--test|--status|--help]"
        echo ""
        echo "Options:"
        echo "  --test    Run sensor module tests"
        echo "  --status  Show system status"
        echo "  --help    Show this help message"
        echo ""
        echo "Without options, starts the monitoring system."
        ;;
    *)
        start_monitoring
        ;;
esac

