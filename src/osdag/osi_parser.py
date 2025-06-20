import yaml
from osdag.design_type.tension_member.tension_welded import Tension_welded
from osdag.design_type.tension_member.tension_bolted import Tension_bolted
from .Common import KEY_DISP_TENSION_WELDED, KEY_DISP_TENSION_BOLTED

MODULE_CLASS_MAP = {
    KEY_DISP_TENSION_WELDED: Tension_welded,
    KEY_DISP_TENSION_BOLTED: Tension_bolted,
}

def parse_osi_to_ui_inputs(osi_source, from_string=False):
    """
    Parse an OSI file or YAML string and return a list of UI input tuples (key, label, type, ..., value),
    similar to what ui_template.py expects for UI population.
    """
    if from_string:
        data = yaml.safe_load(osi_source)
    else:
        with open(osi_source, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    if not data or 'Module' not in data:
        raise ValueError("Invalid or missing 'Module' in OSI data")
    module = data['Module']
    if module not in MODULE_CLASS_MAP:
        raise ValueError(f"Unsupported module: {module}")
    design_class = MODULE_CLASS_MAP[module]()
    ui_fields = design_class.input_values()
    ui_inputs = []
    for field in ui_fields:
        key = field[0]
        value = data.get(key) if key else None
        ui_inputs.append(field + (value,))
    return ui_inputs

if __name__ == "__main__":
    import pprint
    osi_file_path = ['osi_files/TensionBoltedTest1.osi',
                     'osi_files/TensionBoltedTest2.osi',
                     'osi_files/TensionBoltedTest3.osi',
                     'osi_files/TensionBoltedTest4.osi']
    for osi in osi_file_path:
        result = parse_osi_to_ui_inputs(osi)
        pprint.pprint(result)
