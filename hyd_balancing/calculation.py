from .models import HeatingSystem, Room, Radiator

def get_specific_heat_demand(room):
    """
    Returns estimated W/m² based on insulation quality or custom value.
    """
    if room.insulation_quality == 'custom' and room.custom_insulation_value:
        return room.custom_insulation_value

    mapping = {
        'poor': 150.0,    # Old building, uninsulated
        'average': 100.0, # Standard / Renovated
        'good': 50.0,     # Modern / Highly Insulated
    }
    return mapping.get(room.insulation_quality, 100.0)

def get_radiator_nominal_output(rad: Radiator):
    """
    Estimates nominal heat output (W) at 75/65/20 (DeltaT 50K).
    """
    if rad.radiator_type == 'underfloor':
        # UFH capacity is not calculated via 75/65/20 nominals.
        # We return 0 here and handle it specifically in the capacity function.
        return 0
    
    type_factors = {
        '10': 650,
        '11': 900,
        '21': 1250,
        '22': 1700,
        '33': 2400,
    }
    factor = type_factors.get(rad.radiator_type, 1700)
    width_m = (rad.width_mm or 0) / 1000.0
    height_m = (rad.height_mm or 0) / 1000.0
    return (width_m * height_m) * (factor / 0.6)

def get_ufh_capacity(rad: Radiator, system: HeatingSystem, room: Room):
    """
    Calculates UFH capacity based on surface heat emission laws.
    q = alpha * (T_water_avg - T_room)
    alpha is roughly 8.5 W/(m2K) for typical floor constructions.
    """
    t_avg_water = (system.supply_temperature + system.return_temperature) / 2.0
    delta_t = t_avg_water - room.target_temp
    
    if delta_t <= 0: return 10.0 # prevent 0
    
    # Area covered by this loop
    area = rad.area_sqm or room.area_sqm
    
    # Heat emission coefficient (approx 8.5 to 11 depending on floor cover)
    # We use 10.0 as a robust modern average.
    q_specific = delta_t * 10.0
    
    # Max comfort limit is usually around 100W/m2 (floor temp < 29C)
    if q_specific > 100: q_specific = 100.0
    
    return area * q_specific

def get_temperature_correction_factor(system: HeatingSystem, room: Room):
    """
    Calculates the correction factor for standard radiators vs 75/65/20.
    """
    t_supply = system.supply_temperature
    t_return = system.return_temperature
    t_room = room.target_temp
    
    delta_t_sys = (t_supply + t_return) / 2.0 - t_room
    delta_t_norm = 50.0 # (75+65)/2 - 20
    
    if delta_t_sys <= 0: return 0.1
    
    # Radiator exponent (typically 1.3 for panel radiators)
    # At very low temperatures (<35C), convection is less efficient.
    # We use 1.33 as a more conservative modern estimate for retrofits.
    n = 1.33
    return (delta_t_sys / delta_t_norm) ** n

def determine_valve_setting(flow_rate, is_underfloor=False):
    """
    Maps a flow rate (l/h) to a generic valve setting.
    """
    if is_underfloor:
        # Underfloor heating usually has flow meters (Topmeter) calibrated in l/min
        flow_l_min = flow_rate / 60.0
        if flow_l_min < 0.05: return "0.0 l/min"
        return f"{round(flow_l_min, 1)} l/min"

    # Standard radiator pre-setting (1-6)
    if flow_rate <= 10: return "1"
    if flow_rate <= 30: return "2"
    if flow_rate <= 60: return "3"
    if flow_rate <= 100: return "4"
    if flow_rate <= 150: return "5"
    if flow_rate <= 200: return "6"
    return "Max / Open"

def perform_hydraulic_balancing(system: HeatingSystem):
    """
    Calculates required flow rates and valve settings for all radiators in the system.
    """
    delta_t = system.supply_temperature - system.return_temperature
    if delta_t <= 0:
        delta_t = 15 # Fallback
    
    c_water = 1.163

    for room in system.rooms.all():
        specific_heat = get_specific_heat_demand(room)
        room_load_watts = room.area_sqm * specific_heat
        f_corr = get_temperature_correction_factor(system, room)
        
        radiators = room.radiators.all()
        for rad in radiators:
            is_ufh = (rad.radiator_type == 'underfloor')
            
            # 2. Calculate Maximum Capacity
            if is_ufh:
                nominal_cap = get_ufh_capacity(rad, system, room) # UFH doesn't have 75/65 nominals in same way
                max_capacity = nominal_cap
            else:
                nominal_cap = get_radiator_nominal_output(rad)
                max_capacity = nominal_cap * f_corr
            
            rad.nominal_capacity_watts = round(nominal_cap, 1)
            rad.max_capacity_watts = round(max_capacity, 1)

            # 3. Calculate Target Load
            target_load = (room_load_watts * rad.load_percentage) / 100.0
            rad.calculated_load_watts = round(target_load, 1)
            
            # 4. Calculate Flow Rate
            effective_delta_t = 7.0 if is_ufh else delta_t
            req_flow = target_load / (c_water * effective_delta_t)
            
            # 5. Determine Setting
            rad.required_flow_rate = round(req_flow, 2)
            rad.valve_setting = determine_valve_setting(req_flow, is_underfloor=is_ufh)
            rad.save()

def calculate_simplified_balancing(system: HeatingSystem):
    """
    Returns a list of dictionaries containing calculated values for the "Hydraulikblanko" (simplified method) table.
    """
    rooms = list(system.rooms.all())
    if not rooms:
        return [], 0, 0

    # 1. Determine Min Area and Max Relative Area
    areas = [r.area_sqm for r in rooms if r.area_sqm > 0]
    min_area = min(areas) if areas else 0
    
    # Calculate rel_area for all to find max
    rel_areas = [max(0, r.area_sqm - min_area) for r in rooms]
    max_rel_area = max(rel_areas) if rel_areas else 0

    results = []
    
    # Sort rooms by name or ID (or custom order if we had it)
    for idx, room in enumerate(rooms, start=1):
        rel_area = max(0, room.area_sqm - min_area)
        
        # Volumenstromanteil (Flow Share)
        # Avoid division by zero if all rooms are same size (max_rel_area=0)
        if max_rel_area > 0:
            flow_share = rel_area / max_rel_area
        else:
            flow_share = 1.0 # Or 0? If all same size, share is equal. Let's say 1.

        # Max Value TV (Thermostat Valve) - System Parameter
        max_tv = system.max_valve_setting # Default 6
        corr_max_tv = max_tv - 2
        
        # Grundeinstellwert (Base Setting) - Empirical Formula Estimation
        # Hypothesis: 2 + (Share * Range)
        base_setting = 2 + (flow_share * corr_max_tv)
        
        num_rads = room.radiators.count()
        if num_rads == 0:
            zwr_a = 0
            zwr_b = 0
            final_setting = 0
        else:
            # ZwR A: Count - (Count/4) -> N * 0.75
            zwr_a = num_rads - (num_rads / 4.0)
            
            # ZwR B: (Target - 20) / 3
            zwr_b = (room.target_temp - 20.0) / 3.0
            
            # Final Calculation
            # We divide base setting by radiator factor (more rads = lower setting each)
            # We add temp correction (higher temp = higher flow needed = higher setting)
            if zwr_a > 0:
                raw_final = (base_setting / zwr_a) + zwr_b
            else:
                raw_final = 0
            
            # Clamp between 1 and Max? Or leave raw? 
            # Usually valve settings are 1-6.
            final_setting = max(1.0, min(float(max_tv), raw_final))

        results.append({
            'room_nr': idx,
            'room': room,
            'rel_area': round(rel_area, 2),
            'flow_share': round(flow_share, 2),
            'max_tv': max_tv,
            'corr_max_tv': corr_max_tv,
            'base_setting': round(base_setting, 2),
            'num_rads': num_rads,
            'zwr_a': round(zwr_a, 2),
            'zwr_b': round(zwr_b, 2),
            'final_setting': round(final_setting, 1)
        })

    return results, min_area, max_rel_area

