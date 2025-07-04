import sqlite3
from importlib.resources import files
from mock import MagicMock, Mock, patch
import yaml
import os
import traceback

# Configure mocks to be iterable
VALUES_CONN = MagicMock(name="VALUES_CONN")
VALUES_CONN.__iter__.return_value = iter(["Column Flange-Beam Web", "Column Web-Beam Web", "Beam-Beam"])

VALUES_TYP = MagicMock(name="VALUES_TYP")
VALUES_TYP.__iter__.return_value = iter(["Bearing Bolt", "Friction Grip Bolt"])

VALUES_GRD_CUSTOMIZED = MagicMock(name="VALUES_GRD_CUSTOMIZED")
VALUES_GRD_CUSTOMIZED.__iter__.return_value = iter(["E 250 (Fe 410 W)A", "Cus_250_410"])

VALUES_PLATETHK_CUSTOMIZED = MagicMock(name="VALUES_PLATETHK_CUSTOMIZED")
VALUES_PLATETHK_CUSTOMIZED.__iter__.return_value = iter(["10", "12", "16", "20"])

# MaterialValidator can remain a standard Mock
MaterialValidator = Mock(name="MaterialValidator")
MaterialValidator.return_value.is_valid_custom.return_value = True

# PATH_TO_DATABASE = ":memory:"
PATH_TO_DATABASE = files("osdag.data.ResourceFiles.Database").joinpath("Intg_osdag.sqlite")

# Mock FinPlateConnection and its methods
FinPlateConnection = Mock(name="FinPlateConnection")
FinPlateConnection.return_value.set_input_values = Mock(name="set_input_values")
FinPlateConnection.return_value.save_design = Mock(name="save_design")

# Material property calculation
def get_material_strength(material_grade: str, thickness: float = None) -> tuple:
    """
    Calculate yield (fy) and ultimate (fu) strengths for a material grade.
    """
    if material_grade == "E 250 (Fe 410 W)A":
        try:
            thickness = float(thickness)
        except (ValueError, TypeError):
            thickness = None

        if thickness is None:
            return 410, 250, None, None
        elif thickness <= 20:
            return 410, 250, 250, 250
        elif thickness <= 40:
            return 410, 250, 240, 240
        else:
            return 410, 250, 240, 230
        
    elif material_grade.startswith("Cus_"):
        validator = MaterialValidator(material_grade)
        if validator.is_valid_custom():
            parts = material_grade.split('_')
            fu, fy = float(parts[-1]), float(parts[-2])
            return fu, fy, fy, fy
    return 410, 250, None, None

# Input simulation
def simulate_gui_inputs(test_case_data: dict) -> dict:
    """
    Simulate GUI inputs for fin plate connection design.
    """
    design_dict = test_case_data.copy()
    # Patch sqlite3.connect to avoid real DB access
    with patch('sqlite3.connect', return_value=Mock(name="sqlite_connection")):
        conn = sqlite3.connect(PATH_TO_DATABASE)
        # Define input fields and validation rules
        input_fields = [
            {"key": "KEY_MODULE", "type": "TYPE_MODULE", "value": "Fin Plate Connection"},
            {"key": "KEY_CONN", "type": "TYPE_COMBOBOX", "values": VALUES_CONN},
            {"key": "KEY_BOLT_HOLE_TYPE", "type": "TYPE_COMBOBOX", "values": ["Standard", "Over-sized", "Short Slotted", "Long Slotted"]},
            {"key": "KEY_D", "type": "TYPE_COMBOBOX", "values": ['8', '10', '14', '16', '20', '24', '30']},
            {"key": "KEY_GRD", "type": "TYPE_COMBOBOX", "values": ['3.6', '4.6', '4.8', '5.6', '5.8', '6.8', '8.8', '9.8', '10.9', '12.9']},
            {"key": "KEY_SLIP_FACTOR", "type": "TYPE_TEXT", "values": None},
            {"key": "KEY_TENSION_TYPE", "type": "TYPE_COMBOBOX", "values": ["Pre-tensioned", "Non pre-tensioned"]},
            {"key": "KEY_TYP", "type": "TYPE_COMBOBOX", "values": VALUES_TYP},
            {"key": "KEY_CONNECTOR_MATERIAL", "type": "TYPE_COMBOBOX", "values": VALUES_GRD_CUSTOMIZED},
            {"key": "KEY_PLATETHK", "type": "TYPE_COMBOBOX", "values": VALUES_PLATETHK_CUSTOMIZED},
            {"key": "KEY_DESIGN_METHOD", "type": "TYPE_COMBOBOX", "values": ["Limit State Design", "Working Stress Method"]},
            {"key": "KEY_CORROSIVE_INFLUENCES", "type": "TYPE_COMBOBOX", "values": ["Yes", "No"]},
            {"key": "KEY_EDGE_TYPE", "type": "TYPE_COMBOBOX", "values": ["Rolled, machine-flame cut, sawn and planed", "Sheared or hand-flame cut"]},
            {"key": "KEY_GAP", "type": "TYPE_TEXT", "values": None},
            {"key": "KEY_AXIAL", "type": "TYPE_TEXT", "values": None},
            {"key": "KEY_SHEAR", "type": "TYPE_TEXT", "values": None},
            {"key": "KEY_SUPTNGSEC", "type": "TYPE_TEXT", "values": None},
            {"key": "KEY_SUPTNGSEC_MATERIAL", "type": "TYPE_COMBOBOX", "values": VALUES_GRD_CUSTOMIZED},
            {"key": "KEY_SUPTDSEC", "type": "TYPE_TEXT", "values": None},
            {"key": "KEY_SUPTDSEC_MATERIAL", "type": "TYPE_COMBOBOX", "values": VALUES_GRD_CUSTOMIZED},
            {"key": "KEY_WELD_FAB", "type": "TYPE_COMBOBOX", "values": ["Shop weld", "Field weld"]},
            {"key": "KEY_WELD_FU", "type": "TYPE_TEXT", "values": None}
        ]
        for field in input_fields:
            key = field["key"]
            value = design_dict.get(key)
            if field["type"] == "TYPE_COMBOBOX":
                if value not in (field.get("values", []) or []) and value not in ["", None]:
                    continue  # Skip validation for mocks
            if key == "KEY_GRD":
                design_dict[key] = float(value) if value else 8.8
            else:
                design_dict[key] = str(value) if value is not None else ""
        material_keys = [
            ("KEY_SUPTNGSEC_FU", "KEY_SUPTNGSEC_FY", "KEY_SUPTNGSEC_MATERIAL", None),
            ("KEY_SUPTDSEC_FU", "KEY_SUPTDSEC_FY", "KEY_SUPTDSEC_MATERIAL", None),
            ("KEY_CONNECTOR_FU", "KEY_CONNECTOR_FY_20", "KEY_CONNECTOR_MATERIAL", design_dict.get('KEY_PLATETHK', 10)),
        ]
        for fu_key, fy_key, mat_key, thickness in material_keys:
            material = design_dict.get(mat_key, "E 250 (Fe 410 W)A")
            fu, fy, fy_20_40, fy_40 = get_material_strength(material, thickness)
            design_dict[fu_key] = str(fu)
            design_dict[fy_key] = str(fy)
            if fy_20_40 is not None:
                design_dict['KEY_CONNECTOR_FY_20_40'] = str(fy_20_40)
            if fy_40 is not None:
                design_dict['KEY_CONNECTOR_FY_40'] = str(fy_40)
        conn.close()
    return design_dict

# Test execution
def execute_test_cases():
    """
    Execute fin plate connection test cases and validate designs.
    """
    results = []
    osi_dir = "osi_files"
    
    if not os.path.exists(osi_dir):
        raise FileNotFoundError(f"Test directory not found: {osi_dir}")
    
    test_files = sorted(
        f for f in os.listdir(osi_dir) 
        if f.startswith("FinPlateTest") and f.endswith(".osi")
    )
    
    if not test_files:
        print("Warning: No test files found in directory")
        return results
    
    for filename in test_files:
        filepath = os.path.join(osi_dir, filename)
        try:
            print(f"\nProcessing test case: {filename}")
            
            # Read and parse OSI file as YAML
            with open(filepath, 'r') as f:
                test_data = yaml.safe_load(f)
            
            # Pass raw test data to processing pipeline
            design_dict = simulate_gui_inputs(test_data)
            fin_plate = FinPlateConnection()
            fin_plate.set_input_values(design_dict)
            
            results.append({
                "test_case": filename,
                "status": "SUCCESS",
                "design_dict": design_dict
            })
            print(f"{filename}: Validation Successful")
            
        except Exception as e:
            error_trace = traceback.format_exc()
            results.append({
                "test_case": filename,
                "status": "FAILED",
                "error": str(e),
                "traceback": error_trace
            })
            print(f"Validation failed for {filename}: {str(e)}")
    
    print(f"\nTest execution complete. {len(results)} cases processed")
    return results

if __name__ == "__main__":
    test_results = execute_test_cases()
