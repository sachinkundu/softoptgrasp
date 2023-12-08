from robosuite.models.objects import MujocoXMLObject


class ClothObject(MujocoXMLObject):
    """
    Cloth object
    """

    def __init__(self, path, name):
        super().__init__(path, name=name, obj_type="collision", duplicate_collision_geoms=False)