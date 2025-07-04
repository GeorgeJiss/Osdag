import yaml
import os

def convert_cli_to_gui(cli_data):
    """
    Convert CLI input to GUI data structure.

    Returns:
        dict: Data structure matching GUI input format
    """
    # Convert to GUI format
    gui_data = {
        'type': cli_data['type'],
        'inputs': {}
    }
    
    # Convert basic inputs
    for key, value in cli_data['inputs'].items():
        if key == 'design_preferences':
            # Handle design preferences separately
            continue
            
        # Convert mm to m for measurements
        if key in ['plate_thickness', 'plate_length', 'plate_width', 'weld_size', 
                  'pitch', 'gauge', 'end_distance', 'edge_distance']:
            gui_data['inputs'][key] = float(value) / 1000.0
        else:
            gui_data['inputs'][key] = value
    
    # Handle design preferences if present
    if 'design_preferences' in cli_data['inputs']:
        design_prefs = cli_data['inputs']['design_preferences']
        
        # Convert weld preferences
        if 'weld' in design_prefs:
            for key, value in design_prefs['weld'].items():
                if key == 'weld_size':
                    gui_data['inputs'][f'weld_{key}'] = float(value) / 1000.0
                else:
                    gui_data['inputs'][f'weld_{key}'] = value
        
        # Convert detailing preferences
        if 'detailing' in design_prefs:
            for key, value in design_prefs['detailing'].items():
                if key in ['edge_distance', 'pitch', 'gauge']:
                    gui_data['inputs'][f'detailing_{key}'] = float(value) / 1000.0
                else:
                    gui_data['inputs'][f'detailing_{key}'] = value
        
        # Convert design preferences
        if 'design' in design_prefs:
            for key, value in design_prefs['design'].items():
                gui_data['inputs'][f'design_{key}'] = value
    
    return gui_data

def save_to_osi(gui_data, output_path):
    """
    Save the GUI data to an OSI file.
    
    Args:
        gui_data (dict): The converted GUI data
        output_path (str): Path where to save the OSI file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to file
    with open(output_path, 'w') as f:
        yaml.dump(gui_data, f)

if __name__ == "__main__":
    # Example
    test_cli_data = {
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
            'moment': 0,            # kNm
            'design_preferences': {
                'weld': {
                    'weld_type': 'fillet',
                    'weld_size': 6  # mm
                },
                'detailing': {
                    'edge_distance': 40,  # mm
                    'pitch': 60,         # mm
                    'gauge': 60          # mm
                },
                'design': {
                    'safety_factor': 1.5,
                    'design_method': 'LSD'
                }
            }
        }
    }
    
    # Convert CLI data to GUI format
    gui_data = convert_cli_to_gui(test_cli_data)
    
    # Save to OSI file
    save_to_osi(gui_data, 'output.osi')
    
    print("Original CLI data:")
    print(yaml.dump(test_cli_data, default_flow_style=False))
    print("\nConverted GUI data:")
    print(yaml.dump(gui_data, default_flow_style=False)) 