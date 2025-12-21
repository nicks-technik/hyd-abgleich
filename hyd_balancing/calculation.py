from .models import HeatingSystem, Room, Radiator

def get_specific_heat_demand(insulation_quality):
    """
    Returns estimated W/m² based on insulation quality.
    """
    mapping = {
        'poor': 150.0,    # Old building, uninsulated
        'average': 100.0, # Standard / Renovated
        'good': 50.0,     # Modern / Highly Insulated
    }
    return mapping.get(insulation_quality, 100.0)

def determine_valve_setting(flow_rate):
    """
    Maps a flow rate (l/h) to a generic valve setting (1-6).
    This is a simplified generic lookup.
    """
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
        delta_t = 15 # Fallback to prevent division by zero or negative logic
    
    # Constant for water: 1.163 Wh/(kg*K) ~= 1.163 W / (l/h * K)
    # Flow (l/h) = Power (W) / (1.163 * DeltaT)
    c_water = 1.163

    for room in system.rooms.all():
        # 1. Calculate Room Heat Load
        specific_heat = get_specific_heat_demand(room.insulation_quality)
        room_load_watts = room.area_sqm * specific_heat
        
        # 2. Distribute load among radiators
        radiators = room.radiators.all()
        radiator_count = radiators.count()
        
        if radiator_count == 0:
            continue
            
        load_per_radiator = room_load_watts / radiator_count
        
        for rad in radiators:
            # 3. Calculate Flow Rate
            if rad.radiator_type == 'underfloor':
                # Underfloor heating typically has lower Delta T (e.g. 5-7K)
                # But here we use system delta T for simplicity unless overridden
                # Let's assume a fixed Delta T of 7K for underfloor logic override
                effective_delta_t = 7 
            else:
                effective_delta_t = delta_t
            
            req_flow = load_per_radiator / (c_water * effective_delta_t)
            
            # 4. Determine Setting
            setting = determine_valve_setting(req_flow)
            
            # 5. Update Model
            rad.required_flow_rate = round(req_flow, 2)
            rad.valve_setting = setting
            rad.save()
