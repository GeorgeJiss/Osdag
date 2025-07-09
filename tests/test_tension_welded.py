import os
from osdag.Common import *
import pytest
import pandas as pd
import yaml
from osdag.design_type.tension_member.tension_welded import Tension_welded

EXCEL_FILE = os.path.join(os.path.dirname(__file__), "Osdag Data for Unit Tests.xlsx")
OSI_DIR = os.path.join(os.path.dirname(__file__), "osi_files")

def load_osi_file(file_path):
    """Load OSI file and return as dictionary"""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def get_expected_values(test_name):
    """Get expected values from Excel data for given test name"""
    df = pd.read_excel(EXCEL_FILE, sheet_name='Tension Member Welded')

    df.columns = df.columns.str.strip()

    # Find correct row (based on row index, assuming TensionWelded1 = row 0, etc.)
    index = int(test_name.replace("TensionWeldedTest", "")) - 1
    row = df.iloc[index]
    
    return {
        "Designation": row['Designation'],
        "Tension_Yielding_Capacity": row['Tension Yielding Capacity'],
        "Tension_Rupture_Capacity": row['Tension Rupture Capacity'], 
        "Tension_Capacity": row['Tension Capacity'],
        "Slenderness": row['Slenderness Ratio'],
        "Weld_Size": row['Size of Weld'],
        "Weld_Strength": row['Weld Strength'],
        "Plate_Thickness": row['Gusset Plate Thickness'],
        "Plate_Height": row['Gusset Plate Min Height'],
        "Plate_Length": row['Gusset Plate Length']
    }

def create_design_dict_from_osi(osi_data):
    """Convert OSI data to design dictionary format required by calculation"""
    return {
        "Module": osi_data.get("Module", "Tension Member"),  # Optional fallback
        "Section_Profile": osi_data.get("Member.Profile", "Angle"),
        "Location": osi_data.get("Conn_Location", "Web"),
        "Section_Size": osi_data["Member.Designation"][0],  # Primary key used in current test flow
        "Member.Designation": osi_data["Member.Designation"],  # Added for compatibility
        "Material": osi_data.get("Material"),
        "Member.Material": osi_data.get("Member.Material"),
        "Length": osi_data.get("Member.Length", 1000),
        "Member.Length": osi_data.get("Member.Length", 1000),
        "Axial": float(osi_data.get("Load.Axial", 0)),
        "Plate_Thickness": osi_data["Connector.Plate.Thickness_List"][0],
        "Connector.Plate.Thickness_List": osi_data["Connector.Plate.Thickness_List"],  # For completeness
        "Connector_Material": osi_data.get("Connector.Material"),
        "Weld_Fabrication": "Shop",
        "Weld_Material_G_O": "E41XX",
        "Design_Method": osi_data.get("Design.Design_Method"),
        "KEY_DP_WELD_MATERIAL_G_O": "E41XX",  # If needed as alternate fallback key
        "KEY_DP_WELD_FAB": "Shop",  # Consistent with test setup
        "KEY_CONNECTOR_MATERIAL": osi_data.get("Connector.Material"),
        "KEY_PLATETHK": osi_data["Connector.Plate.Thickness_List"][0],
        "KEY_SEC_MATERIAL": osi_data.get("Member.Material"),
        "KEY_LOCATION": osi_data.get("Conn_Location"),
        "KEY_SECSIZE": osi_data["Member.Designation"][0],
        "KEY_SEC_PROFILE": osi_data.get("Member.Profile", "Angle"),
        "KEY_MODULE": osi_data.get("Module", "Tension Member"),
        "KEY_MATERIAL": osi_data.get("Material"),
        "KEY_LENGTH": osi_data.get("Member.Length", 1000),
        "KEY_AXIAL": float(osi_data.get("Load.Axial", 0))
    }


def run_calculation_and_get_results(design_dict):
    """Run calculation by calling set_input_values and return results dictionary"""
    
    
    # Create instance and set input values from OSI keys
    tension_welded = Tension_welded()
    
    # Pass OSI keys to set_input_values function
    tension_welded.set_input_values(design_dict)
    
    # The calculation should run automatically or we can trigger it
    # Extract results from the tension_welded object after calculation
    results = {
        "Designation": getattr(tension_welded, 'designation', ''),
        "Tension_Yielding_Capacity": getattr(tension_welded, 'tension_yielding_capacity', 0),
        "Tension_Rupture_Capacity": getattr(tension_welded, 'tension_rupture_capacity', 0),
        "Tension_Capacity": getattr(tension_welded, 'tension_capacity', 0),
        "Slenderness": getattr(tension_welded, 'slenderness_ratio', 0),
        "Weld_Size": getattr(tension_welded, 'weld_size', 0),
        "Weld_Strength": getattr(tension_welded, 'weld_strength', 0),
        "Plate_Thickness": getattr(tension_welded, 'plate_thickness', 0),
        "Plate_Height": getattr(tension_welded, 'plate_height', 0),
        "Plate_Length": getattr(tension_welded, 'plate_length', 0)
    }
    
    return results

def run_test(test_name):
    """
    Arrange -> Act -> Assert:
    1. Load OSI input
    2. Run design calculation
    3. Compare results with expected output
    """
    # Arrange
    osi_file_path = os.path.join(OSI_DIR, f"{test_name}.osi")
    osi_data = load_osi_file(osi_file_path)
    design_dict = create_design_dict_from_osi(osi_data)
    expected = get_expected_values(test_name)
    
    # Act
    results = run_calculation_and_get_results(design_dict)
    
    # Assert
    assert results["Designation"] == expected["Designation"]
    assert results["Tension_Yielding_Capacity"] == pytest.approx(expected["Tension_Yielding_Capacity"], rel=0.01)
    assert results["Tension_Rupture_Capacity"] == pytest.approx(expected["Tension_Rupture_Capacity"], rel=0.01)
    assert results["Tension_Capacity"] == pytest.approx(expected["Tension_Capacity"], rel=0.01)
    assert results["Slenderness"] == pytest.approx(expected["Slenderness"], rel=0.01)
    assert results["Weld_Size"] == expected["Weld_Size"]
    assert results["Weld_Strength"] == pytest.approx(expected["Weld_Strength"], rel=0.01)
    assert results["Plate_Thickness"] == expected["Plate_Thickness"]
    assert results["Plate_Height"] == expected["Plate_Height"]
    assert results["Plate_Length"] == expected["Plate_Length"]


def test_tension_welded_1():
    """Test case 1: OSI -> Calculation -> Excel comparison"""
    run_test("TensionWeldedTest1")

def test_tension_welded_2():
    """Test case 2: OSI -> Calculation -> Excel comparison"""
    run_test("TensionWeldedTest2")

def test_tension_welded_3():
    """Test case 3: OSI -> Calculation -> Excel comparison"""
    run_test("TensionWeldedTest3")

def test_tension_welded_4():
    """Test case 4: OSI -> Calculation -> Excel comparison"""
    run_test("TensionWeldedTest4")