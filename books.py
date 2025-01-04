class ParkingZone:
    def __init__(self, zone_id, entry_location):
        self.zone_id = zone_id
        self.entry_location = entry_location
        self.area = {
            'two_wheeler': 0,  # in sq meters
            'four_wheeler': 0  # in sq meters
        }
        self.capacity = {
            'two_wheeler': 0,
            'four_wheeler': 0
        }
        self.type = 'segregated'  # or 'combined'
        self.is_active = True

class ParkingFacility:
    def __init__(self):
        self.zones = {}
        
    def add_zone(self, zone_id, entry_location):
        self.zones[zone_id] = ParkingZone(zone_id, entry_location)
        
    def update_zone(self, zone_id, area_data, capacity_data, parking_type):
        if zone_id in self.zones:
            zone = self.zones[zone_id]
            zone.area.update(area_data)
            zone.capacity.update(capacity_data)
            zone.type = parking_type
            
    def get_total_capacity(self):
        return {
            'two_wheeler': sum(zone.capacity['two_wheeler'] for zone in self.zones.values()),
            'four_wheeler': sum(zone.capacity['four_wheeler'] for zone in self.zones.values())
        }
        
    def get_total_area(self):
        return {
            'two_wheeler': sum(zone.area['two_wheeler'] for zone in self.zones.values()),
            'four_wheeler': sum(zone.area['four_wheeler'] for zone in self.zones.values())
        }