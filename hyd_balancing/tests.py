from django.test import TestCase
from django.contrib.auth.models import User
from .models import HeatingSystem, Room, Radiator
from .calculation import calculate_simplified_balancing

class SimplifiedBalancingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.system = HeatingSystem.objects.create(
            user=self.user, 
            name='Test System', 
            max_valve_setting=6
        )
        # Room 1: Smallest
        self.r1 = Room.objects.create(system=self.system, name='Small Room', area_sqm=10, target_temp=20)
        # Room 2: Medium
        self.r2 = Room.objects.create(system=self.system, name='Medium Room', area_sqm=20, target_temp=20)
        # Room 3: Large
        self.r3 = Room.objects.create(system=self.system, name='Large Room', area_sqm=30, target_temp=23) # High temp

        # Radiators
        Radiator.objects.create(room=self.r1, name='R1', load_percentage=100)
        Radiator.objects.create(room=self.r2, name='R2-1', load_percentage=50)
        Radiator.objects.create(room=self.r2, name='R2-2', load_percentage=50)
        Radiator.objects.create(room=self.r3, name='R3', load_percentage=100)

    def test_calculation_logic(self):
        results, min_area, max_rel_area = calculate_simplified_balancing(self.system)
        
        # 1. Check Min/Max Logic
        # Min area = 10
        self.assertEqual(min_area, 10)
        # Rel areas: R1=0, R2=10, R3=20
        # Max rel area = 20
        self.assertEqual(max_rel_area, 20)

        # 2. Check Room 1 (Smallest)
        row1 = next(r for r in results if r['room'] == self.r1)
        self.assertEqual(row1['rel_area'], 0)
        self.assertEqual(row1['flow_share'], 0)
        # Base Setting = 2 + (0 * 4) = 2
        self.assertEqual(row1['base_setting'], 2)
        # Rads = 1. ZwR A = 1 - 0.25 = 0.75
        self.assertEqual(row1['zwr_a'], 0.75)
        # ZwR B = (20-20)/3 = 0
        self.assertEqual(row1['zwr_b'], 0)
        # Final = (2 / 0.75) + 0 = 2.66... -> Round to 2.7
        # Wait, implementation rounds final setting to 1 decimal place.
        # 2 / 0.75 = 2.666...
        self.assertAlmostEqual(row1['final_setting'], 2.7, places=1)

        # 3. Check Room 3 (Largest + High Temp)
        row3 = next(r for r in results if r['room'] == self.r3)
        self.assertEqual(row3['rel_area'], 20)
        self.assertEqual(row3['flow_share'], 1.0)
        # Base Setting = 2 + (1.0 * 4) = 6
        self.assertEqual(row3['base_setting'], 6)
        # Rads = 1. ZwR A = 0.75
        self.assertEqual(row3['zwr_a'], 0.75)
        # ZwR B = (23-20)/3 = 1.0
        self.assertEqual(row3['zwr_b'], 1.0)
        # Final = (6 / 0.75) + 1.0 = 8.0 + 1.0 = 9.0
        # But clamped to Max TV (6)?
        # My implementation: final_setting = max(1.0, min(float(max_tv), raw_final))
        # So should be 6.
        self.assertEqual(row3['final_setting'], 6)

    def test_empty_system(self):
        empty_system = HeatingSystem.objects.create(
            user=self.user, 
            name='Empty System'
        )
        results, min_area, max_rel_area = calculate_simplified_balancing(empty_system)
        self.assertEqual(results, [])
        self.assertEqual(min_area, 0)
        self.assertEqual(max_rel_area, 0)

    def test_room_with_no_radiators(self):
        # Create a room with no radiators
        r_empty = Room.objects.create(system=self.system, name='Empty Room', area_sqm=15, target_temp=20)
        
        results, _, _ = calculate_simplified_balancing(self.system)
        
        row_empty = next(r for r in results if r['room'] == r_empty)
        self.assertEqual(row_empty['num_rads'], 0)
        self.assertEqual(row_empty['zwr_a'], 0)
        self.assertEqual(row_empty['zwr_b'], 0)
        self.assertEqual(row_empty['final_setting'], 0)

from .calculation import get_specific_heat_demand

class HeatDemandCorrectionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.system = HeatingSystem.objects.create(user=self.user, name='Test System')
        self.room = Room.objects.create(system=self.system, name='Test Room', area_sqm=20, insulation_quality='average') # Base 100 W/m2

    def test_external_wall_factors(self):
        # 0 Walls -> 0.8
        self.room.external_walls = 0
        self.assertEqual(get_specific_heat_demand(self.room), 100.0 * 0.8)
        
        # 1 Wall -> 1.0
        self.room.external_walls = 1
        self.assertEqual(get_specific_heat_demand(self.room), 100.0 * 1.0)
        
        # 2 Walls -> 1.1
        self.room.external_walls = 2
        self.assertEqual(get_specific_heat_demand(self.room), 100.0 * 1.1)
        
        # 4 Walls -> 1.3
        self.room.external_walls = 4
        self.assertEqual(get_specific_heat_demand(self.room), 100.0 * 1.3)

    def test_custom_value_ignores_factor(self):
        self.room.insulation_quality = 'custom'
        self.room.custom_insulation_value = 123.0
        self.room.external_walls = 4 # Should have no effect
        self.assertEqual(get_specific_heat_demand(self.room), 123.0)

