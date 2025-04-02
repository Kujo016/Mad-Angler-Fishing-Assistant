# Define quadrant coordinates for each condition
base_tags = {
    'a': {
        'label': 'Low Activity — Stable High/Blue Skies',
        'point': [-1, 1]
    },
    'e': {
        'label': 'Transitional  — Cooling Morning/Late-Day',
        'point': [-1, 0]
    },
    'b': {
        'label': 'Ideal Fishing Window — Mild/Stable',
        'point': [1, 1]
    },
    'f': {
        'label': 'Drop — Incoming Cold Front/Falling',
        'point': [0, 1]
    },
    'c': {
        'label': 'Challenging — Pre-Front Muggy/Stagnant',
        'point': [-1, -1]
    },
    'g': {
        'label': 'Lift — Post-Front Warm-Up/Rising',
        'point': [1, 0]
    },
    'd': {
        'label': 'Chaotic, Unpredictable — Heatwave/Cold Front',
        'point': [1, -1]
    },
    'h': {
        'label': 'High Press Return — Post-Front Spike/Clear/Dry',
        'point': [0, -1]
    },
    'x': {
        'label': 'Immpossible Neutral — Corrupt Weather Data',
        'point': [0, 0]
    }
}


def classify_conditions(temp, humidity, pressure, wind):
    # Handle missing data
    if None in (temp, humidity, pressure, wind):
        print("Incomplete data: One or more weather parameters are missing.")
        return 'x'  # Unknown due to incomplete data

    try:
        temp = float(temp)
        humidity = float(humidity)
        pressure = float(pressure)
        wind = float(wind)
    except ValueError:
        return 'x'

    # 1. Ideal fishing window — stable, warm, mid-pressure, moderate humidity
    if 60 <= temp <= 75 and 40 <= humidity <= 65 and 1012 <= pressure <= 1018 and 3 <= wind <= 12:
        return 'b'

    # 2. Drop in conditions — cold front, falling pressure, light wind
    elif pressure <= 1008 and wind <= 8 and temp <= 60:
        return 'f'

    # 3. Lift in conditions — rising temps & pressure post-front, improving bite
    elif pressure >= 1010 and 60 <= temp <= 70 and 8 <= wind <= 15:
        return 'g'

    # 4. Chaotic, unpredictable — extreme heat/cold, high winds, sharp pressure drops
    elif temp >= 85 or temp <= 40 or wind >= 20 or pressure <= 1000:
        return 'd'

    # 5. Challenging but possible — humid, stagnant, pre-front bite window
    elif humidity >= 70 and wind < 6 and pressure >= 1005 and pressure <= 1010:
        return 'c'

    # 6. Calm, low activity — stable high pressure, clear skies, glassy water
    elif wind <= 2 and pressure >= 1018 and humidity <= 40:
        return 'a'

    # 7. Subtle shift — cool breeze, mid-pressure, good during transitions
    elif 50 <= temp <= 65 and 30 <= humidity <= 60 and 5 <= wind <= 10 and 1008 <= pressure <= 1015:
        return 'e'

    # 8. High pressure returning — spike in pressure after a front, often tough bite
    elif pressure >= 1016 and humidity <= 50 and wind  <= 8:
        return 'h'

    # Default: average, neutral
    return 'x'
