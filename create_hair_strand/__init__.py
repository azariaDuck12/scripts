import bpy
from bpy.props import IntProperty, FloatProperty

# Global variable to hold the instance of the CreateHairStrandOperator
operator_instance = None

class CreateHairStrandOperator(bpy.types.Operator):
    bl_idname = "object.create_hair_strand"
    bl_label = "Create Hair Strand"
    bl_description = "Create a hair strand with user-defined parameters"

    num_points: IntProperty(
        name="Number of Bezier Points",
        description="Number of control points for the hair strand",
        default=2,
        min=2,
        max=20
    ) # type: ignore
    
    extrude: FloatProperty(
        name="Extrude",
        description="Extrusion thickness of the hair strand",
        default=1,
        min=0,
        max=100,
        precision=2
    ) # type: ignore

    bevel_depth: FloatProperty(
        name="Bevel Depth",
        description="Bevel depth for the hair strand",
        default=0.5,
        min=0.0,
        max=100,
        precision=2
    ) # type: ignore

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "num_points")
        layout.prop(self, "extrude")
        layout.prop(self, "bevel_depth")
        layout.operator("object.reset_hair_strand_defaults", text="Reset to Defaults")

    def execute(self, context):
        # Clear existing curve objects
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_by_type(type='CURVE')
        bpy.ops.object.delete()

        # Create a new curve
        curve_data = bpy.data.curves.new(name='HairStrand', type='CURVE')
        curve_data.dimensions = '3D'

        # Create a new spline in the curve
        spline = curve_data.splines.new(type='BEZIER')
        spline.bezier_points.add(count=self.num_points - 1)

        # Define the points of the spline
        points = spline.bezier_points
        for i, point in enumerate(points):
            point.co = (0, 0, i)  # Arrange points along the Z-axis
            point.handle_left_type = 'AUTO'
            point.handle_right_type = 'AUTO'

        # Create a new object with the curve
        curve_obj = bpy.data.objects.new('HairStrandObject', curve_data)

        # Add the object to the scene
        scene = bpy.context.scene
        scene.collection.objects.link(curve_obj)

        # Set the active object
        bpy.context.view_layer.objects.active = curve_obj
        curve_obj.select_set(True)

        # Add taper and extrude to give volume to the hair strand
        curve_data.extrude = self.extrude/100  # Set thickness from user input
        curve_data.bevel_depth = self.bevel_depth/100  # Set taper from user input

        # Apply smooth shading
        curve_obj.data.bevel_resolution = 4
        
        return {'FINISHED'}

    def invoke(self, context, event):
        # Open the operator properties dialogue
        context.window_manager.modal_handler_add(self)
        return context.window_manager.invoke_props_dialog(self)

class ResetHairStrandDefaultsOperator(bpy.types.Operator):
    bl_idname = "object.reset_hair_strand_defaults"
    bl_label = "Reset Hair Strand Defaults"

    def execute(self, context):
        global operator_instance
        if operator_instance:
            operator_instance.num_points = 2
            operator_instance.extrude = 1
            operator_instance.bevel_depth = 0.5
        return {'FINISHED'}

# Function to add the operator to the Object menu
def menu_func(self, context):
    self.layout.operator(CreateHairStrandOperator.bl_idname, text="Create Hair Strand")

# Register and unregister the operator and menu
def register():
    bpy.utils.register_class(CreateHairStrandOperator)
    bpy.utils.register_class(ResetHairStrandDefaultsOperator)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)  # Add to the "Add Mesh" menu

def unregister():
    bpy.utils.unregister_class(CreateHairStrandOperator)
    bpy.utils.unregister_class(ResetHairStrandDefaultsOperator)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

# Ensure proper registration and unregistration
if __name__ == "__main__":
    # Only unregister if the class has already been registered
    try:
        unregister()
    except Exception as e:
        print("Unregister failed:", e)
    register()
