import yaml
import pytest

def convert_cli_to_gui(cli_data):
    """
    Convert CLI input to GUI data structure.
    
    Args:
        cli_data (dict): CLI input data
        
    Returns:
        dict: Data structure matching GUI input format
    """
    # Convert to GUI format
    gui_data = {
        'type': cli_data['type'],
        'inputs': {}
    }
    
    # Convert inputs
    for key, value in cli_data['inputs'].items():
        # Convert mm to m for measurements
        if key in ['plate_thickness', 'plate_length', 'plate_width', 'weld_size', 
                  'pitch', 'gauge', 'end_distance', 'edge_distance']:
            gui_data['inputs'][key] = float(value) / 1000.0
        else:
            gui_data['inputs'][key] = value
    
    return gui_data

# Test data fixture
@pytest.fixture
def test_cli_data():
    return {
        'type': 'fin_plate',
        'inputs': {
            'column_section': 'ISMB 300',
            'beam_section': 'ISMB 250',
            'plate_thickness': 10,  # mm
            'plate_length': 300,    # mm
            'plate_width': 200,     # mm
            'weld_size': 6,         # mm
            'bolt_diameter': 20,    # mm
            'bolt_grade': '8.8',
            'bolt_type': 'bearing',
            'bolt_hole_type': 'normal',
            'bolt_washer': True,
            'bolt_line': 2,
            'bolts_one_line': 3,
            'pitch': 60,            # mm
            'gauge': 60,            # mm
            'end_distance': 40,     # mm
            'edge_distance': 40,    # mm
            'connection_type': 'col_web_beam_web',
            'design_method': 'LSD',
            'safety_factor': 1.5,
            'shear_force': 100,     # kN
            'axial_force': 0,       # kN
            'moment': 0             # kNm
        }
    }

def test_type_preservation(test_cli_data):
    """Test that the connection type is preserved in the conversion."""
    gui_data = convert_cli_to_gui(test_cli_data)
    assert gui_data['type'] == test_cli_data['type']

def test_measurement_conversion(test_cli_data):
    """Test that measurements are correctly converted from mm to m."""
    gui_data = convert_cli_to_gui(test_cli_data)
    
    # Test specific measurements
    assert gui_data['inputs']['plate_thickness'] == 0.01  # 10 mm to m
    assert gui_data['inputs']['plate_length'] == 0.3      # 300 mm to m
    assert gui_data['inputs']['weld_size'] == 0.006       # 6 mm to m
    assert gui_data['inputs']['pitch'] == 0.06            # 60 mm to m
    assert gui_data['inputs']['gauge'] == 0.06            # 60 mm to m
    assert gui_data['inputs']['end_distance'] == 0.04     # 40 mm to m
    assert gui_data['inputs']['edge_distance'] == 0.04    # 40 mm to m

def test_non_measurement_preservation(test_cli_data):
    """Test that non-measurement values are preserved without conversion."""
    gui_data = convert_cli_to_gui(test_cli_data)
    
    # Test specific non-measurement values
    assert gui_data['inputs']['column_section'] == test_cli_data['inputs']['column_section']
    assert gui_data['inputs']['beam_section'] == test_cli_data['inputs']['beam_section']
    assert gui_data['inputs']['bolt_grade'] == test_cli_data['inputs']['bolt_grade']
    assert gui_data['inputs']['bolt_type'] == test_cli_data['inputs']['bolt_type']
    assert gui_data['inputs']['design_method'] == test_cli_data['inputs']['design_method']
    assert gui_data['inputs']['safety_factor'] == test_cli_data['inputs']['safety_factor']

def test_boolean_preservation(test_cli_data):
    """Test that boolean values are preserved correctly."""
    gui_data = convert_cli_to_gui(test_cli_data)
    assert gui_data['inputs']['bolt_washer'] == test_cli_data['inputs']['bolt_washer']

def test_numeric_preservation(test_cli_data):
    """Test that numeric values that are not measurements are preserved."""
    gui_data = convert_cli_to_gui(test_cli_data)
    assert gui_data['inputs']['bolt_line'] == test_cli_data['inputs']['bolt_line']
    assert gui_data['inputs']['bolts_one_line'] == test_cli_data['inputs']['bolts_one_line']
    assert gui_data['inputs']['shear_force'] == test_cli_data['inputs']['shear_force']
    assert gui_data['inputs']['axial_force'] == test_cli_data['inputs']['axial_force']
    assert gui_data['inputs']['moment'] == test_cli_data['inputs']['moment']

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 