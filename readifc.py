import ifcopenshell
import ifcopenshell.geom
from ifcopenshell.util.shape import (
    get_volume,
    get_area,
    get_top_elevation,
    get_bottom_elevation,
)
from ifccsv import IfcCsv

# Paths
ifc_path = './data/20211108ARA_ASH_S3B_ARCHITECTURE_wall.ifc'
output_csv = "output.csv"  # Replace with your desired CSV output path

# Load the IFC model
model = ifcopenshell.open(ifc_path)

# Initialize geometry settings
settings = ifcopenshell.geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)

# Helper function to get materials
def get_material(element):
    try:
        materials = element.IsDefinedBy
        if materials:
            for rel in materials:
                if hasattr(rel, "RelatingMaterial"):
                    material = rel.RelatingMaterial
                    if hasattr(material, "Name"):
                        return material.Name
                    elif hasattr(material, "Materials"):  # Composite materials
                        return ", ".join([m.Name for m in material.Materials])
        return "No material assigned"
    except Exception as e:
        return f"Error retrieving material: {e}"

# Collect data for CSV export
data = []
headers = [
    "ObjectID", "GlobalId", "Name", "Description", "ObjectType",
    "Material", "Volume (m³)", "Surface Area (m²)",
    "Top Elevation (m)", "Bottom Elevation (m)"
]

for element in model.by_type("IfcElement"):
    if element.Representation:
        try:
            # Basic properties
            object_id = element.id()
            global_id = element.GlobalId
            name = element.Name or "N/A"
            description = element.Description or "N/A"
            object_type = element.ObjectType or "N/A"
            material = get_material(element)

            # Geometry calculations
            shape = ifcopenshell.geom.create_shape(settings, element)
            volume = get_volume(shape.geometry)
            surface_area = get_area(shape.geometry)
            top_elevation = get_top_elevation(shape.geometry)
            bottom_elevation = get_bottom_elevation(shape.geometry)

            # Append data row
            data.append([
                object_id, global_id, name, description, object_type,
                material, f"{volume:.2f}", f"{surface_area:.2f}",
                f"{top_elevation:.2f}", f"{bottom_elevation:.2f}"
            ])
        except Exception as e:
            print(f"Error processing element {element.id()} ({element.GlobalId}): {e}")

# Export to CSV using IfcCsv
ifc_csv = IfcCsv()
ifc_csv.headers = headers
ifc_csv.results = data
ifc_csv.export_csv(output_csv, delimiter=",")

print(f"Export complete! File saved to {output_csv}")
