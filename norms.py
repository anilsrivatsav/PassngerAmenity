# norms.py
class RailwayAmenities:
    def __init__(self):
        self.minimum_essential_amenities = {
            'NSG1': {
                'drinking_water_taps': {'quantity': 20, 'note': 'One tap for disabled persons on alternate water booths'},
                'waiting_hall_sqm': 250,
                'seating_per_platform': 150,
                'platform_shelter_sqm': 500,
                'urinals': {'quantity': 12, 'auto_flush': True, 'note': '1/3rd for ladies'},
                'latrines': {'quantity': 12, 'auto_flush': True, 'note': '1/3rd for ladies'},
                'platform_level': 'High Level',
                'lighting': 'As per Board standards',
                'fans': {'note': 'One row for 6-9m width platform, two rows for >9m'},
                'foot_over_bridge': {'required': True, 'with_cover': True, 'width': '6m minimum'},
                'time_table': 'As per extant instructions',
                'clock': 'As per zonal railways',
                'water_cooler': '2 on each PF',
                'public_address_system': 'As per extant instructions',
                'parking_area': 'With lights',
                'train_indicator': 'As per extant instructions',
                'signage': {'required': True, 'note': 'Standardized per Board guidelines'},
                'dustbins': {'spacing': '50m', 'note': 'Uniformly designed'}
            }
        }
        
        # Copy NSG1 amenities to NSG2-6 with modifications
        for category in ['NSG2', 'NSG3', 'NSG4', 'NSG5', 'NSG6']:
            self.minimum_essential_amenities[category] = self.minimum_essential_amenities['NSG1'].copy()
            
            if category == 'NSG3':
                self.minimum_essential_amenities[category].update({
                    'waiting_hall_sqm': 125,
                    'seating_per_platform': 125,
                    'platform_shelter_sqm': 400,
                    'urinals': {'quantity': 10, 'auto_flush': True, 'note': '1/3rd for ladies'},
                    'latrines': {'quantity': 10, 'auto_flush': True, 'note': '1/3rd for ladies'}
                })
            elif category == 'NSG4':
                self.minimum_essential_amenities[category].update({
                    'waiting_hall_sqm': 75,
                    'seating_per_platform': 100,
                    'platform_shelter_sqm': 200,
                    'urinals': {'quantity': 4, 'auto_flush': False, 'note': '1/3rd for ladies'},
                    'latrines': {'quantity': 6, 'auto_flush': False, 'note': '1/3rd for ladies'},
                    'foot_over_bridge': {'required': True, 'with_cover': False}
                })
            elif category == 'NSG5':
                self.minimum_essential_amenities[category].update({
                    'drinking_water_taps': {'quantity': 8, 'note': 'One tap for disabled persons'},
                    'waiting_hall_sqm': 30,
                    'seating_per_platform': 50,
                    'platform_shelter_sqm': 50,
                    'urinals': {'quantity': 4, 'auto_flush': False, 'note': '1/3rd for ladies'},
                    'latrines': {'quantity': 4, 'auto_flush': False, 'note': '1/3rd for ladies'},
                    'water_cooler': '1 on main PF'
                })
            elif category == 'NSG6':
                self.minimum_essential_amenities[category].update({
                    'drinking_water_taps': {'quantity': 2, 'note': 'Alternative arrangement where piped water not feasible'},
                    'waiting_hall_sqm': 15,
                    'seating_per_platform': 10,
                    'platform_shelter_sqm': 50,
                    'urinals': {'quantity': 1, 'auto_flush': False, 'note': '1/3rd for ladies'},
                    'latrines': {'quantity': 1, 'auto_flush': False, 'note': '1/3rd for ladies'},
                    'water_cooler': '1 on main PF',
                    'dustbins': {'spacing': 'As required', 'note': 'Adequate numbers'},
                    'train_indicator': False
                })

        # Add Halt stations (HG) amenities
        self.minimum_essential_amenities.update({
            'HG1': {
                'drinking_water': 'Appropriate facility',
                'waiting_hall': '10 sqm booking office cum waiting hall',
                'platform_shelter': 'Bus type modular shelter',
                'platform_level': 'High Level',
                'lighting': 'As per Board standards',
                'foot_over_bridge': {'required': True, 'note': 'For double line section'},
                'time_table': 'As per instructions',
                'clock': True,
                'dustbins': 'As per instructions'
            },
            'HG2': {
                'drinking_water': 'Appropriate facility',
                'waiting_hall': '10 sqm booking office cum waiting hall',
                'platform_shelter': 'Shady trees',
                'platform_level': 'High Level',
                'lighting': 'For night trains',
                'foot_over_bridge': {'required': True, 'note': 'For double line section'},
                'dustbins': 'As per instructions'
            },
            'HG3': {
                'drinking_water': 'Appropriate facility',
                'platform_shelter': 'Shady trees',
                'platform_level': 'High Level',
                'lighting': 'For night trains',
                'foot_over_bridge': {'required': True, 'note': 'For double line section'},
                'dustbins': 'As per instructions'
            }
        })

    def get_minimum_amenities(self, station_category):
        # Remove hyphen from category code if present
        category = station_category.replace('-', '')
        return self.minimum_essential_amenities.get(category, {})

    def get_desirable_amenities(self, station_category):
        # Remove hyphen from category code if present
        category = station_category.replace('-', '')
        
        desirable_amenities = {
            'NSG1': {
                'retiring_room': True,
                'waiting_room_with_bath': True,
                'cloak_room': True,
                'enquiry_counter': True,
                'ntes': True,
                'ivrs': True,
                'public_address_system': True,
                'book_stalls': True,
                'refreshment_room': True,
                'parking_area': True,
                'train_indicator': True,
                'touch_screen': True,
                'water_vending': True,
                'escalators': True,
                'travellator': True,
                'signage': True,
                'modular_catering': True,
                'automatic_vending': True,
                'pay_use_toilets': True,
                'cyber_cafe': True,
                'atm': True,
                'executive_lounge': True,
                'food_plaza': True,
                'train_coach_indication': True,
                'cctv': True,
                'coin_operated_ticket': True,
                'pre_paid_taxi': True,
                'access_control': True,
                'bio_toilets': True,
                'bottle_crushers': True,
                'wifi': True,
                'second_entry': True,
                'senior_citizen_waiting': True,
                'wheelchair_facilities': True,
                'water_fountain': True
            }
        }
        
        # Copy NSG1 amenities to NSG2-3 with modifications
        for cat in ['NSG2', 'NSG3']:
            desirable_amenities[cat] = desirable_amenities['NSG1'].copy()
        
        # NSG4-6 have fewer desirable amenities
        desirable_amenities['NSG4'] = {
            'pay_use_toilets': True,
            'atm': True,
            'bio_toilets': True,
            'wifi': True,
            'second_entry': True
        }
        
        desirable_amenities['NSG5'] = {
            'pay_use_toilets': True,
            'atm': True,
            'bio_toilets': True
        }
        
        desirable_amenities['NSG6'] = {
            'pay_use_toilets': True,
            'atm': True,
            'bio_toilets': True
        }
        
        return desirable_amenities.get(category, {})