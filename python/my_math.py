import os
import struct
import math
import ctypes

#Water Temp
def estimate_water_temp(air_temp, wind_speed, elevation_ft):
    base = air_temp - (wind_speed * 0.5 if wind_speed else 0)
    if elevation_ft and elevation_ft > 5000:
        base -= 5
    return round(base, 1)

def normalize_inputs(humidity, pressure, temp, wind):
    norm_humidity = max(min(humidity / 100.0, 1.0), 0.01)
    norm_pressure = pressure / 1013.25
    norm_temp = max(min((temp - 32) / 68.0, 1.5), 0.0)
    norm_wind = max(min(wind / 15.0, 2.0), 0.0)

    volatility = norm_temp * (1.0 - norm_pressure) * norm_humidity
    spiral_speed = norm_wind * norm_humidity

    return norm_humidity, norm_temp, norm_pressure, norm_wind, volatility, spiral_speed


def spiral_position_within_quadrant(temp, humidity, pressure, center, wind, t=1.0, scale=10.0):
    """
    Generates a spiral path that rotates around a chaos vector and migrates outward from the center
    based on weather instability and directional tension.
    
    center: (x, y) graph center
    scale: max migration distance from center
    t: spiral time step
    """
    # STEP 0: Normalize inputs and extract properties
    norm_humidity, norm_temp, norm_pressure, norm_wind, volatility, spiral_speed = normalize_inputs(
        humidity, pressure, temp, wind
    )

    # STEP 1: Chaos vector [x, y] — direction of instability
    chaos_strength = volatility * 2.0
    chaos_angle = math.pi * (norm_wind - 0.5) * 2  # -π to π
    chaos_vector = [
        chaos_strength * math.cos(chaos_angle),
        chaos_strength * math.sin(chaos_angle),
    ]

    # STEP 2: Compute directional center vector (migration vector)
    # Use angle to determine direction from center, and tension to determine how far
    tension = (norm_humidity + norm_temp + (1 - norm_pressure) + norm_wind) / 4
    offset_distance = (0.5 + volatility) * tension * scale  # max ~scale * 1.5

    # Use same angle as chaos for now, but you could modify this too
    center_vector = [
        offset_distance * math.cos(chaos_angle),
        offset_distance * math.sin(chaos_angle),
    ]

    # STEP 3: Spiral radius decay and angle
    decay = 0.25 + norm_humidity * 0.5
    base_radius = 1.2 + volatility
    r = base_radius * (1 - math.exp(-decay * t))


    theta = -2 * math.pi * spiral_speed * t

    # Final spiral position: migrate + chaos + spiral
    x = center[0] + center_vector[0] + chaos_vector[0] + r * math.cos(theta)
    y = center[1] + center_vector[1] + chaos_vector[1] + r * math.sin(theta)

    return x, y

