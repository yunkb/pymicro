import os
import sys
import vtk
import numpy as np
from vtk.util.colors import black, white, grey, blue, orange
from vtk.util import numpy_support

# see if some of the stuff needs to be moved to the Microstructure module
from pymicro.crystal.lattice import Lattice, HklPlane


def to_vtk_type(type):
    '''Function to get the VTK data type given a numpy data type.

    :param str type: The numpy data type like 'uint8', 'uint16'...
    :return: A VTK data type.
    '''
    if type == 'uint8':
        return vtk.VTK_UNSIGNED_CHAR
    elif type == 'uint16':
        return vtk.VTK_UNSIGNED_SHORT
    elif type == 'uint32':
        return vtk.VTK_UNSIGNED_INT
    elif type == 'float':
        return vtk.VTK_FLOAT
    elif type == 'float64':
        return vtk.VTK_DOUBLE


def rand_cmap(N=256, first_is_black=False, table_range=(0, 255)):
    '''Create a VTK lookup table with random colors.

    The first color can be enforced to black and usually figure out
    the image background. The random seed is fixed to 13 in order
    to consistently produce the same colormap.

    :param int N: The number of colors in the colormap.
    :param bool first_is_black: Force the first color to be black.
    :param typle table_range: The range of the VTK lookup table
    :return: A vtkLookupTable lookup table with N random colors.
    '''
    np.random.seed(13)
    rand_colors = np.random.rand(N, 3)
    if first_is_black:
        rand_colors[0] = [0., 0., 0.]  # enforce black background
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(N)
    lut.Build()
    for i in range(N):
        lut.SetTableValue(i, rand_colors[i][0], rand_colors[i][1], rand_colors[i][2], 1.0)
    lut.SetRange(table_range)
    return lut


def pv_rand_cmap(N=256, first_is_black=False):
    '''Write out the random color map in paraview xml format.

    This method print out the XML declaration of the random colormap.
    This may be saved to a text file and used in paraview.

    :param int N: The number of colors in the colormap.
    :param bool first_is_black: Force the first color to be black.
    '''
    np.random.seed(13)
    rand_colors = np.random.rand(N, 3)
    if first_is_black:
        rand_colors[0] = [0., 0., 0.]  # enforce black background
    print '<ColorMap name="random" space="RGB">'
    for i in range(N):
        print '<Point x="%d" o="1" r="%8.6f" g="%8.6f" b="%8.6f"/>' % (
            i, rand_colors[i][0], rand_colors[i][1], rand_colors[i][2])
    print '</ColorMap>'


def gray_cmap(table_range=(0, 255)):
    '''create a black and white colormap.

    *Parameters*

    **table_range**: 2 values tuple (default: (0,255))
    start and end values for the table range.

    *Returns*

    A vtkLookupTable from black to white.
    '''
    lut = vtk.vtkLookupTable()
    lut.SetSaturationRange(0, 0)
    lut.SetHueRange(0, 0)
    lut.SetTableRange(table_range)
    lut.SetValueRange(0, 1)
    lut.SetRampToLinear()
    lut.Build()
    return lut


def invert_cmap(ref_lut):
    '''invert a VTK lookup table.

    *Parameters*

    **ref_lut**: The lookup table to invert.

    *Returns*

    A reverse vtkLookupTable.
    '''
    N = ref_lut.GetNumberOfTableValues()
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(N)
    lut.Build()
    for i in range(N):
        lut.SetTableValue(i, ref_lut.GetTableValue(N - i))
    lut.SetRange(ref_lut.GetTableRange())
    return lut


def hsv_cmap(N=64, table_range=(0, 255)):
    '''Create a VTK look up table similar to matlab's hsv.

    *Parameters*

    **N**: int, number of colors in the table.

    **table_range**: 2 values tuple (default: (0,255))
    start and end values for the table range.

    *Returns*

    A vtkLookupTable.
    '''
    lut = vtk.vtkLookupTable()
    lut.SetHueRange(0.0, 1.0)
    lut.SetSaturationRange(1.0, 1.0)
    lut.SetValueRange(1.0, 1.0)
    lut.SetNumberOfColors(N)
    lut.Build()
    lut.SetRange(table_range)
    return lut


def jet_cmap(N=64, table_range=(0, 255)):
    '''Create a VTK look up table similar to matlab's jet.

    *Parameters*

    **N**: int, number of colors in the table.

    **table_range**: 2 values tuple (default: (0,255))
    start and end values for the table range.

    *Returns*

    A vtkLookupTable from blue to red.
    '''
    lut = vtk.vtkLookupTable()
    lut.SetHueRange(0.667, 0.0)
    lut.SetNumberOfColors(N)
    lut.Build()
    lut.SetRange(table_range)
    return lut


def hot_cmap(table_range=(0, 255)):
    '''Create a VTK look up table similar to matlab's hot.

    *Parameters*

    **table_range**: 2 values tuple (default: (0,255))
    start and end values for the table range.

    *Returns*

    A vtkLookupTable from white to red.
    '''
    lut = vtk.vtkLookupTable()
    lutNum = 64
    lut.SetNumberOfTableValues(lutNum)
    lut.Build()
    lut.SetTableValue(0, 0.041667, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(1, 0.083333, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(2, 0.125000, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(3, 0.166667, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(4, 0.208333, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(5, 0.250000, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(6, 0.291667, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(7, 0.333333, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(8, 0.375000, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(9, 0.416667, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(10, 0.458333, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(11, 0.500000, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(12, 0.541667, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(13, 0.583333, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(14, 0.625000, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(15, 0.666667, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(16, 0.708333, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(17, 0.750000, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(18, 0.791667, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(19, 0.833333, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(20, 0.875000, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(21, 0.916667, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(22, 0.958333, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(23, 1.000000, 0.000000, 0.000000, 1.0)
    lut.SetTableValue(24, 1.000000, 0.041667, 0.000000, 1.0)
    lut.SetTableValue(25, 1.000000, 0.083333, 0.000000, 1.0)
    lut.SetTableValue(26, 1.000000, 0.125000, 0.000000, 1.0)
    lut.SetTableValue(27, 1.000000, 0.166667, 0.000000, 1.0)
    lut.SetTableValue(28, 1.000000, 0.208333, 0.000000, 1.0)
    lut.SetTableValue(29, 1.000000, 0.250000, 0.000000, 1.0)
    lut.SetTableValue(30, 1.000000, 0.291667, 0.000000, 1.0)
    lut.SetTableValue(31, 1.000000, 0.333333, 0.000000, 1.0)
    lut.SetTableValue(32, 1.000000, 0.375000, 0.000000, 1.0)
    lut.SetTableValue(33, 1.000000, 0.416667, 0.000000, 1.0)
    lut.SetTableValue(34, 1.000000, 0.458333, 0.000000, 1.0)
    lut.SetTableValue(35, 1.000000, 0.500000, 0.000000, 1.0)
    lut.SetTableValue(36, 1.000000, 0.541667, 0.000000, 1.0)
    lut.SetTableValue(37, 1.000000, 0.583333, 0.000000, 1.0)
    lut.SetTableValue(38, 1.000000, 0.625000, 0.000000, 1.0)
    lut.SetTableValue(39, 1.000000, 0.666667, 0.000000, 1.0)
    lut.SetTableValue(40, 1.000000, 0.708333, 0.000000, 1.0)
    lut.SetTableValue(41, 1.000000, 0.750000, 0.000000, 1.0)
    lut.SetTableValue(42, 1.000000, 0.791667, 0.000000, 1.0)
    lut.SetTableValue(43, 1.000000, 0.833333, 0.000000, 1.0)
    lut.SetTableValue(44, 1.000000, 0.875000, 0.000000, 1.0)
    lut.SetTableValue(45, 1.000000, 0.916667, 0.000000, 1.0)
    lut.SetTableValue(46, 1.000000, 0.958333, 0.000000, 1.0)
    lut.SetTableValue(47, 1.000000, 1.000000, 0.000000, 1.0)
    lut.SetTableValue(48, 1.000000, 1.000000, 0.062500, 1.0)
    lut.SetTableValue(49, 1.000000, 1.000000, 0.125000, 1.0)
    lut.SetTableValue(50, 1.000000, 1.000000, 0.187500, 1.0)
    lut.SetTableValue(51, 1.000000, 1.000000, 0.250000, 1.0)
    lut.SetTableValue(52, 1.000000, 1.000000, 0.312500, 1.0)
    lut.SetTableValue(53, 1.000000, 1.000000, 0.375000, 1.0)
    lut.SetTableValue(54, 1.000000, 1.000000, 0.437500, 1.0)
    lut.SetTableValue(55, 1.000000, 1.000000, 0.500000, 1.0)
    lut.SetTableValue(56, 1.000000, 1.000000, 0.562500, 1.0)
    lut.SetTableValue(57, 1.000000, 1.000000, 0.625000, 1.0)
    lut.SetTableValue(58, 1.000000, 1.000000, 0.687500, 1.0)
    lut.SetTableValue(59, 1.000000, 1.000000, 0.750000, 1.0)
    lut.SetTableValue(60, 1.000000, 1.000000, 0.812500, 1.0)
    lut.SetTableValue(61, 1.000000, 1.000000, 0.875000, 1.0)
    lut.SetTableValue(62, 1.000000, 1.000000, 0.937500, 1.0)
    lut.SetTableValue(63, 1.000000, 1.000000, 1.000000, 1.0)
    lut.SetRange(table_range)
    return lut


def add_hklplane_to_grain(hklplane, grid, orientation, origin=(0, 0, 0),
                          opacity=1.0, show_normal=False, normal_length=1.0):
    rot_plane = vtk.vtkPlane()
    rot_plane.SetOrigin(origin)
    # rotate the plane by setting the normal
    Bt = orientation.orientation_matrix().transpose()
    n_rot = np.dot(Bt, hklplane.normal() / np.linalg.norm(hklplane.normal()))
    rot_plane.SetNormal(n_rot)
    # print '[hkl] normal direction expressed in sample coordinate system is: ', n_rot
    if show_normal:
        return add_plane_to_grid(rot_plane, grid, origin, opacity=opacity)
    else:
        return add_plane_to_grid_with_normal(rot_plane, grid, origin, \
                                             opacity=opacity, normal_length=normal_length)


def add_plane_to_grid(plane, grid, origin, opacity=0.3):
    '''Add a 3d plane inside another object.

    This function adds a plane inside another object described by a mesh
    (vtkunstructuredgrid). The method is to use a vtkCutter with the mesh
    as input and the plane as the cut function. An actor is returned.
    This may be used directly to add hkl planes inside a lattice cell or
    a grain.

    *Parameters*

    **plane**: A VTK implicit function describing the plane to add.

    **grid**: A VTK unstructured grid in which the plane is to be added.

    **opacity**: Opacity value of the plane actor.

    *Returns*

    A VTK actor.
    '''
    # cut the unstructured grid with the plane
    planeCut = vtk.vtkCutter()
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        planeCut.SetInputData(grid)
    else:
        planeCut.SetInput(grid)
    planeCut.SetCutFunction(plane)

    cutMapper = vtk.vtkPolyDataMapper()
    cutMapper.SetInputConnection(planeCut.GetOutputPort())
    cutActor = vtk.vtkActor()
    cutActor.SetMapper(cutMapper)
    cutActor.GetProperty().SetOpacity(opacity)
    return cutActor


def add_plane_to_grid_with_normal(plane, grid, origin, opacity=0.3, normal_length=1.0):
    '''Add a 3d plane and display its normal inside another object.

    This function adds a plane inside another object described by a mesh
    (vtkunstructuredgrid). It basicall call `add_plane_to_grid` and also
    add a 3d arrow to display the plane normal.

    *Parameters*

    **plane**: A VTK implicit function describing the plane to add.

    **grid**: A VTK unstructured grid in which the plane is to be added.

    **opacity**: Opacity value of the plane actor.

    **normal_length**: The length of the plane normal vector.

    *Returns*

    A VTK assembly with the plane and the normal.
    '''
    assembly = vtk.vtkAssembly()
    planeActor = add_plane_to_grid(plane, grid, origin, opacity=opacity)
    assembly.AddPart(planeActor)
    # add an arrow to display the normal to the plane
    arrowActor = unit_arrow_3d(origin, normal_length * np.array(plane.GetNormal()), make_unit=False)
    assembly.AddPart(arrowActor)
    return assembly


def axes_actor(length=1.0, axisLabels=('x', 'y', 'z'), fontSize=20, color=None):
    '''Build an actor for the cartesian axes.

    :param length: The arrow length of the axes (1.0 by default).
    :type length: float or triple of float to specify the length of each axis individually.
    :param list axisLabels: Specify the axes labels (xyz by default), use axisLabels = None to hide the axis labels
    :param int fontSize: Font size for the axes labels (20 by default).
    :param tuple color: A single color defined by its rgb components (not set by default which keep the red, green, blue colors).
    :returns: A VTK assembly representing the cartesian axes.
    '''
    axes = vtk.vtkAxesActor()
    if isinstance(length, (float, int, np.int64, np.float64)):
        axes.SetTotalLength(length, length, length)
    else:
        assert(len(length) == 3)
        axes.SetTotalLength(length)
    axes.SetShaftTypeToCylinder()
    axes.SetCylinderRadius(0.02)
    if axisLabels:
        axes.SetXAxisLabelText(axisLabels[0])
        axes.SetYAxisLabelText(axisLabels[1])
        axes.SetZAxisLabelText(axisLabels[2])
        axprop = vtk.vtkTextProperty()
        axprop.SetColor(0, 0, 0)
        axprop.SetFontSize(fontSize)
        axprop.SetFontFamilyToArial()
        axes.GetXAxisCaptionActor2D().SetCaptionTextProperty(axprop)
        axes.GetYAxisCaptionActor2D().SetCaptionTextProperty(axprop)
        axes.GetZAxisCaptionActor2D().SetCaptionTextProperty(axprop)
    else:
        axes.SetAxisLabels(0)
    if color:
        # set the color of the whole triad
        collection = vtk.vtkPropCollection()
        axes.GetActors(collection)
        for i in range(collection.GetNumberOfItems()):
            collection.GetItemAsObject(i).GetProperty().SetColor(color)
    return axes


def grain_3d(grain, hklplanes=None, show_normal=False, \
             plane_opacity=1.0, show_orientation=False, N=2048):
    '''Creates a 3d representation of a crystallographic grain.

    This method creates a vtkActor object of the surface mesh
    representing a Grain object. An optional list of crystallographic
    planes can be given

    :params grain: the Grain object to be shown in 3d.
    :params list hklplanes: the list of HklPlanes object to add to the assembly.
    :params bool show_normal: show also the normal to the hkl planes if True.
    :params float plane_opacity: set the opacity of the grain actor.
    :params bool show_orientation: show also the grain orientation with a vtkAxesActor placed at the grain center if True.
    :params int N: the number of colors to use in the colormap.
    :returns: a vtkAssembly of the grain mesh and the optional hkl planes.
    '''
    assembly = vtk.vtkAssembly()
    # create mapper
    mapper = vtk.vtkDataSetMapper()
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        mapper.SetInputData(grain.vtkmesh)
    else:
        mapper.SetInput(grain.vtkmesh)
    mapper.ScalarVisibilityOff()  # we use the grain id for chosing the color
    lut = rand_cmap(N, first_is_black=True, table_range=(0, N - 1))
    grain_actor = vtk.vtkActor()
    print grain.id
    print(lut.GetTableValue(grain.id)[0:3])
    grain_actor.GetProperty().SetColor(lut.GetTableValue(grain.id)[0:3])
    grain_actor.SetMapper(mapper)
    assembly.AddPart(grain_actor)
    # add all hkl planes
    if hklplanes != None:
        for hklplane in hklplanes:
            # the grain has its center of mass at the origin
            origin = (0., 0., 0.)
            hklplaneActor = add_hklplane_to_grain(hklplane, grain.vtkmesh, \
                                                  grain.orientation, origin, opacity=plane_opacity, \
                                                  show_normal=show_normal, normal_length=50.)
            assembly.AddPart(hklplaneActor)
    if show_orientation:
        grain_actor.GetProperty().SetOpacity(0.3)
        local_orientation = add_local_orientation_axes(grain.orientation, axes_length=30)
        # add local orientation to the grain actor
        assembly.AddPart(local_orientation)
    return assembly


# deprecated, will be removed soon
def add_grain_to_3d_scene(grain, hklplanes, show_orientation=False):
    orientation = grain.orientation
    assembly = vtk.vtkAssembly()
    # create mapper
    print 'creating grain actor'
    mapper = vtk.vtkDataSetMapper()
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        mapper.SetInputData(grain.vtkmesh)
    else:
        mapper.SetInput(grain.vtkmesh)
    mapper.ScalarVisibilityOff()  # we use the grain id for chosing the color
    lut = rand_cmap(N=2048, first_is_black=True, table_range=(0, 2047))
    grain_actor = vtk.vtkActor()
    grain_actor.GetProperty().SetColor(lut.GetTableValue(grain.id)[0:3])
    grain_actor.SetMapper(mapper)
    assembly.AddPart(grain_actor)
    # add all hkl planes and local grain orientation actor
    if show_orientation:
        grain_actor.GetProperty().SetOpacity(0.3)
        local_orientation = add_HklPlanes_with_orientation_in_grain(grain, hklplanes)
        # add local orientation to the grain actor
        assembly.AddPart(local_orientation)
    return assembly


def add_local_orientation_axes(orientation, axes_length=30):
    # use a vtkAxesActor to display the crystal orientation
    local_orientation = vtk.vtkAssembly()
    axes = axes_actor(length=axes_length, axisLabels=False)
    apply_orientation_to_actor(axes, orientation)
    '''
    transform = vtk.vtkTransform()
    transform.Identity()
    transform.RotateZ(orientation.phi1())
    transform.RotateX(orientation.Phi())
    transform.RotateZ(orientation.phi2())
    axes.SetUserTransform(transform)
    '''
    local_orientation.AddPart(axes)
    return local_orientation


def add_HklPlanes_with_orientation_in_grain(grain, \
                                            hklplanes=[]):
    '''
    Add some plane actors corresponding to a list of (hkl) planes to
    a grain actor.
    '''
    # use a vtkAxesActor to display the crystal orientation
    local_orientation = vtk.vtkAssembly()
    grain_axes = axes_actor(length=30, axisLabels=False)
    apply_orientation_to_actor(grain_axes, grain.orientation)
    local_orientation.AddPart(grain_axes)
    # add all hkl planes to the grain
    for hklplane in hklplanes:
        hklplaneActor = add_hklplane_to_grain(hklplane, grain.vtkmesh, \
                                              grain.orientation)
        local_orientation.AddPart(hklplaneActor)
    return local_orientation


def unit_arrow_3d(start, vector, color=orange, radius=0.03, make_unit=True, label=False, text=None, text_scale=0.1,
                  vector_normal=None):
    n = np.linalg.norm(vector)
    arrowSource = vtk.vtkArrowSource()
    arrowSource.SetShaftRadius(radius)
    arrowSource.SetTipRadius(10 * radius / 3.)
    # We build a local direct base with X being the unit arrow vector
    X = vector / n
    arb = np.array([1, 0, 0])  # used numpy here, could used the vtkMath module as well...
    if np.dot(X, arb) == 1:
        arb = np.array([0, 1, 0])
    Z = np.cross(X, arb)
    Y = np.cross(Z, X)
    m = vtk.vtkMatrix4x4()
    m.Identity()
    m.DeepCopy((1, 0, 0, start[0],
                0, 1, 0, start[1],
                0, 0, 1, start[2],
                0, 0, 0, 1))
    # Create the direction cosine matrix
    if make_unit: n = 1
    for i in range(3):
        m.SetElement(i, 0, n * X[i]);
        m.SetElement(i, 1, n * Y[i]);
        m.SetElement(i, 2, n * Z[i]);
    t = vtk.vtkTransform()
    t.Identity()
    t.Concatenate(m)
    transArrow = vtk.vtkTransformFilter()
    transArrow.SetInputConnection(arrowSource.GetOutputPort())
    transArrow.SetTransform(t)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(transArrow.GetOutputPort())
    arrowActor = vtk.vtkActor()
    arrowActor.SetMapper(mapper)
    arrowActor.GetProperty().SetColor(color)
    if label:
        # add a text actor to display the vector coordinates
        assembly = vtk.vtkAssembly()
        assembly.AddPart(arrowActor)
        vectorText = vtk.vtkVectorText()
        if text == None:
            # display the vector coordinates as text
            vectorText.SetText(np.array_str(vector))
        else:
            vectorText.SetText(text)
        textMapper = vtk.vtkPolyDataMapper()
        textMapper.SetInputConnection(vectorText.GetOutputPort())
        textTransform = vtk.vtkTransform()
        start_text = start + vector
        mt = vtk.vtkMatrix4x4()
        mt.Identity()
        mt.DeepCopy((1, 0, 0, start_text[0],
                     0, 1, 0, start_text[1],
                     0, 0, 1, start_text[2],
                     0, 0, 0, 1))
        # Create the direction cosine matrix
        if vector_normal == None: vector_normal = Z
        for i in range(3):
            mt.SetElement(i, 0, vector[i]);
            mt.SetElement(i, 1, Y[i]);
            mt.SetElement(i, 2, vector_normal[i]);
        textTransform.Identity()
        textTransform.Concatenate(mt)
        textTransform.Scale(text_scale, text_scale, text_scale)
        textActor = vtk.vtkActor()
        textActor.SetMapper(textMapper)
        textActor.SetUserTransform(textTransform)
        textActor.GetProperty().SetColor(color)
        assembly.AddPart(textActor)
        return assembly
    else:
        return arrowActor


def lattice_points(lattice, origin=(0., 0., 0.), m=1, n=1, p=1):
    '''
    Create a vtk representation of a the lattice points.

    A vtkPoints instance is used to store the lattice points, including
    the points not on the lattice corners according to the system
    centering (may be P, I, F for instance).

    :param Lattice lattice: The Lattice instance from which to construct the points.
    :param tuple origin: cartesian coordinates of the origin.
    :param int m: the number of cells in the [100] direction (1 by default).
    :param int n: the number of cells in the [010] direction (1 by default).
    :param int p: the number of cells in the [001] direction (1 by default).
    :return: A vtkPoints with all the lattice points ordered such that the first 8*(m*n*p) points describe the lattice cells.
    '''
    [A, B, C] = lattice._matrix
    O = origin
    points = vtk.vtkPoints()
    # create all the points based on the lattice matrix
    for k in range(p + 1):
        for j in range(n + 1):
            for i in range(m + 1):
                points.InsertNextPoint(O + i * A + j * B + k * C)
    # now add extra points to represent the lattice centering
    for k in range(p):
        for j in range(n):
            for i in range(m):
                O = origin + i * A + j * B + k * C
                if lattice._centering == 'P':
                    pass  # nothing to do
                elif lattice._centering == 'I':
                    points.InsertNextPoint(O + 0.5 * A + 0.5 * B + 0.5 * C)
                elif lattice._centering == 'A':
                    points.InsertNextPoint(O + 0.5 * B + 0.5 * C)
                    points.InsertNextPoint(O + A + 0.5 * B + 0.5 * C)
                elif lattice._centering == 'B':
                    points.InsertNextPoint(O + 0.5 * A + 0.5 * C)
                    points.InsertNextPoint(O + 0.5 * A + B + 0.5 * C)
                elif lattice._centering == 'C':
                    points.InsertNextPoint(O + 0.5 * A + 0.5 * B)
                    points.InsertNextPoint(O + 0.5 * A + 0.5 * B + C)
                elif lattice._centering == 'F':
                    points.InsertNextPoint(O + 0.5 * A + 0.5 * B)
                    points.InsertNextPoint(O + 0.5 * A + 0.5 * B + C)
                    points.InsertNextPoint(O + 0.5 * B + 0.5 * C)
                    points.InsertNextPoint(O + 0.5 * B + 0.5 * C + A)
                    points.InsertNextPoint(O + 0.5 * C + 0.5 * A)
                    points.InsertNextPoint(O + 0.5 * C + 0.5 * A + B)
    return points


def lattice_grid(lattice, origin=(0., 0., 0.), m=1, n=1, p=1):
    '''
    Create a mesh representation of a crystal lattice.

    A vtkUnstructuredGrid instance is used with a hexaedron element
    corresponding to the lattice system. Any number of cells can be
    displayed (just one by default).

    :param Lattice lattice: The Lattice instance from which to construct the grid.
    :param tuple origin: cartesian coordinates of the origin.
    :param int m: the number of cells in the [100] direction (1 by default).
    :param int n: the number of cells in the [010] direction (1 by default).
    :param int p: the number of cells in the [001] direction (1 by default).
    :return: A vtkUnstructuredGrid with (m x n x p) hexaedron cell representing the crystal lattice.
    '''
    points = lattice_points(lattice, origin, m, n, p)
    # build the unstructured grid with m x n x p cells
    grid = vtk.vtkUnstructuredGrid()
    grid.SetPoints(points)
    grid.Allocate(p * n * m, 1)
    for k in range(p):
        for j in range(n):
            for i in range(m):
                # ids list
                Ids = vtk.vtkIdList()
                Ids.InsertNextId(i + j * (m + 1) + k * (m + 1) * (n + 1))
                Ids.InsertNextId(i + 1 + j * (m + 1) + k * (m + 1) * (n + 1))
                Ids.InsertNextId(i + 1 + (j + 1) * (m + 1) + k * (m + 1) * (n + 1))
                Ids.InsertNextId(i + (j + 1) * (m + 1) + k * (m + 1) * (n + 1))
                Ids.InsertNextId(i + j * (m + 1) + (k + 1) * (m + 1) * (n + 1))
                Ids.InsertNextId(i + 1 + j * (m + 1) + (k + 1) * (m + 1) * (n + 1))
                Ids.InsertNextId(i + 1 + (j + 1) * (m + 1) + (k + 1) * (m + 1) * (n + 1))
                Ids.InsertNextId(i + (j + 1) * (m + 1) + (k + 1) * (m + 1) * (n + 1))
                grid.InsertNextCell(vtk.VTK_HEXAHEDRON, Ids)
    return grid


def hexagonal_lattice_grid(lattice, origin=[0., 0., 0.]):
    [A, B, C] = lattice._matrix
    O = origin
    points = vtk.vtkPoints()
    points.InsertNextPoint(O)
    points.InsertNextPoint(O + A)
    points.InsertNextPoint(O + A - B)
    points.InsertNextPoint(O - 2 * B)
    points.InsertNextPoint(O - 2 * B - A)
    points.InsertNextPoint(O - B - A)
    points.InsertNextPoint(O + C)
    points.InsertNextPoint(O + A + C)
    points.InsertNextPoint(O + A - B + C)
    points.InsertNextPoint(O - 2 * B + C)
    points.InsertNextPoint(O - 2 * B - A + C)
    points.InsertNextPoint(O - B - A + C)

    ids = vtk.vtkIdList()
    ids.InsertNextId(0)
    ids.InsertNextId(1)
    ids.InsertNextId(2)
    ids.InsertNextId(3)
    ids.InsertNextId(4)
    ids.InsertNextId(5)
    ids.InsertNextId(6)
    ids.InsertNextId(7)
    ids.InsertNextId(8)
    ids.InsertNextId(9)
    ids.InsertNextId(10)
    ids.InsertNextId(11)
    # build the unstructured grid with one cell
    grid = vtk.vtkUnstructuredGrid()
    grid.Allocate(1, 1)
    grid.InsertNextCell(16, ids)  # 16 is hexagonal prism cell type
    grid.SetPoints(points)
    return grid


def lattice_edges(grid, tubeRadius=0.02, tubeColor=grey):
    '''
    Create the 3D representation of crystal lattice edges.

    *Parameters*

    **grid**: vtkUnstructuredGrid
    The vtkUnstructuredGrid instance representing the crystal lattice.

    **tubeRadius**: float
    Radius of the tubes representing the atomic bonds (default: 0.02).

    **tubeColor**: vtk color
    Color of the tubes representing the atomis bonds (default: grey).

    *Returns*

    The method return a vtk actor for lattice edges.
    '''
    Edges = vtk.vtkExtractEdges()
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        Edges.SetInputData(grid)
    else:
        Edges.SetInput(grid)
    Tubes = vtk.vtkTubeFilter()
    Tubes.SetInputConnection(Edges.GetOutputPort())
    Tubes.SetRadius(tubeRadius)
    Tubes.SetNumberOfSides(6)
    Tubes.UseDefaultNormalOn()
    Tubes.SetDefaultNormal(.577, .577, .577)
    # Create the mapper and actor to display the cell edges.
    TubeMapper = vtk.vtkPolyDataMapper()
    TubeMapper.SetInputConnection(Tubes.GetOutputPort())
    Edges = vtk.vtkActor()
    Edges.SetMapper(TubeMapper)
    Edges.GetProperty().SetDiffuseColor(tubeColor)
    return Edges


def lattice_vertices(grid, sphereRadius=0.1, sphereColor=blue):
    '''
    Create the 3D representation of crystal lattice atoms.

    *Parameters*

    **grid**: vtkUnstructuredGrid
    The vtkUnstructuredGrid instance representing the crystal lattice.

    **sphereRadius**: float
    Size of the spheres representing the atoms (default: 0.1).

    **sphereColor**: vtk color
    Color of the spheres representing the atoms (default: blue).

    *Returns*

    The method return a vtk actor for lattice vertices.
    '''
    # Create a sphere to use as a glyph source for vtkGlyph3D.
    Sphere = vtk.vtkSphereSource()
    Sphere.SetRadius(sphereRadius)
    Sphere.SetPhiResolution(40)
    Sphere.SetThetaResolution(40)
    Vertices = vtk.vtkGlyph3D()
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        Vertices.SetInputData(grid)
    else:
        Vertices.SetInput(grid)
    Vertices.SetSourceConnection(Sphere.GetOutputPort())
    # Create a mapper and actor to display the glyphs.
    SphereMapper = vtk.vtkPolyDataMapper()
    SphereMapper.SetInputConnection(Vertices.GetOutputPort())
    SphereMapper.ScalarVisibilityOff()
    Vertices = vtk.vtkActor()
    Vertices.SetMapper(SphereMapper)
    Vertices.GetProperty().SetDiffuseColor(sphereColor)
    return Vertices


def crystal_vertices(crystal, origin=(0., 0., 0.), m=1, n=1, p=1, hide_outside=True):
    '''
    Create the 3D representation of the atoms in a given crystal, taking
    into account the crystal lattice and the basis which can be composed
    of any motif.

    :param tuple origin: cartesian coordinates of the origin.
    :param int m: the number of cells in the [100] direction (1 by default).
    :param int n: the number of cells in the [010] direction (1 by default).
    :param int p: the number of cells in the [001] direction (1 by default).
    :param bool hide_outside: do not displays atoms outside the displayed unit cells if True.
    :return: The method return a vtk actor with all the crystal atoms.
    '''
    data = vtk.vtkPolyData()
    # sphere glyph for one atom
    Sphere = vtk.vtkSphereSource()
    Sphere.SetPhiResolution(20)
    Sphere.SetThetaResolution(20)
    points = lattice_points(crystal._lattice, origin, m, n, p)
    # setup a vtkGlyph3D instance
    Vertices = vtk.vtkGlyph3D()
    Vertices.SetScaleModeToScaleByScalar()
    Vertices.SetScaleFactor(1.0)
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        Vertices.SetInputData(data)
    else:
        Vertices.SetInput(data)
    Vertices.SetSourceConnection(Sphere.GetOutputPort())
    Vertices.SetColorModeToColorByScalar()
    # Create a mapper and actor to display the glyphs.
    SphereMapper = vtk.vtkPolyDataMapper()
    SphereMapper.SetInputConnection(Vertices.GetOutputPort())
    SphereMapper.ScalarVisibilityOn()

    atom_points = vtk.vtkPoints()
    color_scalars = vtk.vtkFloatArray()
    color_scalars.SetName('color')
    radius_scalars = vtk.vtkFloatArray()
    radius_scalars.SetName('radius')
    radius = 0.1 * min(crystal._lattice._lengths)  # default for atoms
    bounds = np.array([m, n, p]) * crystal._lattice._lengths
    for pid in range(points.GetNumberOfPoints()):
        point = points.GetPoint(pid)
        for l in range(len(crystal._basis)):
            basis_position = crystal._basis[l] * crystal._lattice._lengths
            print(point)
            position = np.array(point) + np.array(basis_position)
            # if needed skip things outside
            eps = 1e-6
            if hide_outside and (
                                    position[0] - origin[0] > bounds[0] + eps or position[1] - origin[1] > bounds[
                            1] + eps or
                                position[2] - origin[2] > bounds[2] + eps):
                continue
            atom_points.InsertNextPoint(position)
            color_scalars.InsertNextValue(float(l))
            radius_scalars.InsertNextValue(crystal._sizes[l] * min(crystal._lattice._lengths))
    data.SetPoints(atom_points)
    # perpare a scalar array with the two components: radius and color
    scalar_data = vtk.vtkFloatArray()
    scalar_data.SetNumberOfComponents(2)
    scalar_data.SetNumberOfTuples(color_scalars.GetNumberOfTuples())
    scalar_data.CopyComponent(0, radius_scalars, 0)
    scalar_data.CopyComponent(1, color_scalars, 0)
    scalar_data.SetName('scalar_data')
    data.GetPointData().AddArray(scalar_data)
    data.GetPointData().SetActiveScalars('scalar_data')

    # make the corresponding lut
    lut = vtk.vtkLookupTable()
    N = len(crystal._basis)
    lut.SetNumberOfTableValues(N)
    lut.Build()
    for i in range(N):
        color = crystal._colors[i]
        lut.SetTableValue(i, color[0], color[1], color[2])
    lut.SetRange(0, N - 1)
    SphereMapper.SetLookupTable(lut)
    SphereMapper.ColorByArrayComponent('scalar_data', 1)
    atoms = vtk.vtkActor()
    atoms.SetMapper(SphereMapper)
    return atoms


def crystal_3d(crystal, origin=(0., 0., 0.), m=1, n=1, p=1, \
               sphereRadius=0.1, tubeRadius=0.02, sphereColor=blue, tubeColor=grey, hide_outside=True):
    assembly = vtk.vtkAssembly()
    print crystal
    grid = lattice_grid(crystal._lattice, origin, m, n, p)
    (a, b, c) = crystal._lattice._lengths
    edges = lattice_edges(grid, tubeRadius=tubeRadius * a, tubeColor=tubeColor)
    vertices = crystal_vertices(crystal, origin, m, n, p, hide_outside)
    assembly.AddPart(edges)
    assembly.AddPart(vertices)
    assembly.SetOrigin(origin)  # m*a/2, n*b/2, p*c/2)
    assembly.AddPosition(-np.array(origin))  # -m*a/2, -n*b/2, -p*c/2)
    return assembly


def lattice_3d(lattice, origin=(0., 0., 0.), m=1, n=1, p=1, \
               sphereRadius=0.05, tubeRadius=0.02, sphereColor=black, tubeColor=grey, \
               crystal_orientation=None, show_atoms=True, show_edges=True, cell_clip=False):
    '''
    Create the 3D representation of a crystal lattice.

    The lattice edges are shown using a vtkTubeFilter and the atoms are
    displayed using spheres. Both tube and sphere radius can be controlled.
    Crystal orientation can also be provided which rotates the whole
    assembly appropriately.

    The origin of the actor can be t=either specified directly using a
    tuple or set using a string as follow:

     * mid the middle of the lattice cell(s)

    .. code-block:: python

      l = Lattice.cubic(1.0)
      cubic = lattice_3d(l)
      ren = vtk.vtkRenderer()
      ren.AddActor(cubic)
      render(ren, display=True)

    .. figure:: _static/lattice_3d.png
        :width: 300 px
        :height: 300 px
        :alt: lattice_3d
        :align: center

        A 3D view of a cubic lattice.

    :param Lattice lattice: The Lattice instance representing the crystal lattice.
    :param tuple or string origin: cartesian coordinates of the origin.
    :param int m: the number of cells in the [100] direction (1 by default).
    :param int n: the number of cells in the [010] direction (1 by default).
    :param int p: the number of cells in the [001] direction (1 by default).
    :param float sphereRadius: Size of the spheres representing the atoms (default: 0.05).
    :param float tubeRadius: Radius of the tubes representing the atomic bonds (default: 0.02).
    :param tuple sphereColor: Color of the spheres representing the atoms (default: black).
    :param tuple tubeColor: Color of the tubes representing the atomis bonds (default: grey).
    :param crystal_orientation: The crystal :py:class:`~pymicro.crystal.microstructure.Orientation` with respect to the sample coordinate system (default: None).
    :param bool show_atoms: Control if the atoms are shown (default: True).
    :param bool show_edges: Control if the eges of the lattice are shown (default: True).
    :param bool cell_clip: Clip the lattice points glyphs by the cell (default: False).
    :return: The method return a vtk assembly combining lattice edges and vertices.
    '''
    (a, b, c) = lattice._lengths
    if origin == 'mid':
        origin = (m * a / 2, n * b / 2, p * c / 2)
    grid = lattice_grid(lattice, (0., 0., 0.), m, n, p)  # we use the actor origin
    edges = lattice_edges(grid, tubeRadius=tubeRadius * min(lattice._lengths), tubeColor=tubeColor)
    vertices = lattice_vertices(grid, sphereRadius=sphereRadius * min(lattice._lengths), sphereColor=sphereColor)
    assembly = vtk.vtkAssembly()
    if show_edges: assembly.AddPart(edges)
    if show_atoms:
        if cell_clip:
            # use boolean operation
            epsilon = 1.e-6
            cube = vtk.vtkCubeSource()
            cube.SetCenter(a / 2, b / 2, c / 2)
            cube.SetXLength(a + epsilon)
            cube.SetYLength(b + epsilon)
            cube.SetZLength(c + epsilon)
            strips = vtk.vtkStripper()
            strips.SetInputConnection(cube.GetOutputPort())
            strips.Update()
            triangles = vtk.vtkTriangleFilter()
            triangles.SetInputData(cube.GetOutput())
            bool_filter = vtk.vtkBooleanOperationPolyDataFilter()
            bool_filter.SetOperation(bool_filter.VTK_INTERSECTION)
            bool_filter.SetInputConnection(0, triangles.GetOutputPort())
            bool_filter.SetInputConnection(1, vertices.GetMapper().GetInputAlgorithm().GetOutputPort())
            clip_mapper = vtk.vtkPolyDataMapper()
            clip_mapper.SetInputConnection(bool_filter.GetOutputPort(0))
            clip_mapper.SetScalarVisibility(0)
            clip_actor = vtk.vtkActor()
            clip_actor.SetMapper(clip_mapper)
            clip_actor.GetProperty().SetColor(sphereColor)
            assembly.AddPart(clip_actor)
        else:
            assembly.AddPart(vertices)
    # finally, apply crystal orientation to the lattice
    apply_translation_to_actor(assembly, -np.array(origin))
    # assembly.SetOrigin(origin)#m*a/2, n*b/2, p*c/2)
    if crystal_orientation != None:
        apply_orientation_to_actor(assembly, crystal_orientation)
    return assembly


def lattice_3d_with_planes(lattice, hklplanes, plane_origins=None, show_normal=True,
                           plane_opacity=1.0, **kwargs):
    '''
    Create the 3D representation of a crystal lattice.

    HklPlanes can be displayed within the lattice cell with their normals.
    A single vtk actor in form of an assembly is returned.
    Additional parameters are passed to the `lattice_3d` method to control how the lattice is pictured.

    .. code-block:: python

      l = Lattice.cubic(1.0)
      o = Orientation.from_euler([344.0, 125.0, 217.0])
      hklplanes = Hklplane.get_family('111')
      cubic = lattice_3d_with_planes(l, hklplanes, show_normal=True, \\
        plane_opacity=0.5, crystal_orientation=o)
      s3d = Scene3D()
      s3d.add(cubic)
      s3d.render()

    .. figure:: _static/cubic_crystal_3d.png
       :width: 300 px
       :alt: lattice_3d_with_planes
       :align: center

       A 3D view of a cubic lattice with all four 111 planes displayed.

    :param lattice: An instance of :py:class:`~pymicro.crystal.lattice.Lattice` corresponding to the crystal lattice to be displayed.
    :param hklplanes: A list of :py:class:`~pymicro.crystal.lattice.HklPlane` instances to add to the lattice.
    :param plane_origins: A list of tuples describing the plane origins (must be the same length as `hklplanes`), if None, the planes are created to pass through the middle of the lattice (default).
    :param bool show_normal: Control if the slip plane normals are shown (default: True).
    :param float plane_opacity: A float number in the [0.,1.0] range controlling the slip plane opacity.
    :param **kwargs: additional parameters are passed to the `lattice_3d` method.
    :returns: The method return a vtkAssembly that can be directly added to a renderer.
    '''
    grid = lattice_grid(lattice)
    (a, b, c) = lattice._lengths
    if plane_origins:
        assert len(plane_origins) == len(hklplanes)
    elif kwargs['origin'] == 'mid':
        origin = (a / 2, b / 2, c / 2)
    else:
        origin = (0., 0., 0.)
    # get the atoms+edges assembly corresponding to the crystal lattice
    assembly = lattice_3d(lattice, **kwargs)
    # display all the hkl planes within the lattice
    for i, hklplane in enumerate(hklplanes):
        mid = np.array([a / 2, b / 2, c / 2])
        plane = vtk.vtkPlane()
        plane.SetOrigin(mid)
        plane.SetNormal(hklplane.normal())
        hklplaneActor = add_plane_to_grid(plane, grid, mid, opacity=plane_opacity)
        if plane_origins:
            origin = plane_origins[i] * np.array([a, b, c]) - mid
            print('using origin', origin)
            hklplaneActor.AddPosition(origin)
            hklplaneActor.SetOrigin(-origin)
        assembly.AddPart(hklplaneActor)
        if show_normal:
            # add an arrow to display the normal to the plane
            arrowActor = unit_arrow_3d(origin, a * hklplane.normal(), make_unit=False)
            assembly.AddPart(arrowActor)
    return assembly


def lattice_3d_with_plane_series(lattice, hkl, nps=1, **kwargs):
    '''
    Create the 3D representation of a crystal lattice with a series of hkl planes.

    HklPlanes can be displayed within the lattice cell with their normals.
    A single vtk actor in form of an assembly is returned.
    Additional parameters are passed to the `lattice_3d` method to control how the lattice is pictured.

    .. code-block:: python

        l = Lattice.cubic(1.0)
        orientation = Orientation.from_euler([0, 54.74, 135])  # correspond to 111 fiber texture
        copper = (1.000000, 0.780392, 0.494117)  # nice copper color
        copper_lattice = lattice_3d_with_plane_series(l, (1, -1, 1), nps=4, crystal_orientation=orientation, \\
            origin='mid', show_atoms=True, sphereColor=copper, sphereRadius=0.1)
        s3d = Scene3D()
        s3d.add(cubic)
        s3d.render()

    .. figure:: _static/Cu111_with_planes.png
       :width: 400 px
       :alt: Cu111_with_planes
       :align: center

       A 3D view of a copper lattice with a series of successive (111) planes displayed.

    :param lattice: An instance of :py:class:`~pymicro.crystal.lattice.Lattice` corresponding to the crystal lattice to be displayed.
    :param hkl: A tuple of the 3 miller indices.
    :param int nps: The number of planes to display in the series (1 by default).
    :param **kwargs: additional parameters are passed to the `lattice_3d_with_planes` method.
    :returns: The method return a vtkAssembly that can be directly added to a renderer.
    '''
    p = HklPlane(hkl[0], hkl[1], hkl[2], lattice)
    d_hkl = p.interplanar_spacing()
    (a, b, c) = lattice._lengths
    mid = np.array([0.5 * a, 0.5 * b, 0.5 * c])
    hkl_planes = []
    plane_origins = []
    for i in range(nps):
        hkl_planes.append(p)
        plane_origins.append(mid - (nps / 2. - 0.5 - i) * d_hkl * p.normal())
    return lattice_3d_with_planes(lattice, hkl_planes, plane_origins=plane_origins, **kwargs)


def apply_translation_to_actor(actor, trans):
    '''
    Transform the actor (or whole assembly) using the specified translation.

    :param vtkActor actor: the vtk actor.
    :param trans: a 3 component numpy vector or sequence describing the translation to apply in scene units.
    '''
    transform = actor.GetUserTransform()
    if transform == None:
        transform = vtk.vtkTransform()
        transform.Identity()
    transform.PostMultiply()
    transform.Translate(trans[0], trans[1], trans[2])
    actor.SetUserTransform(transform)


def apply_orientation_to_actor(actor, orientation):
    '''
    Transform the actor (or whole assembly) using the specified orientation.
    Here we could use the three euler angles associated with the
    orientation with the RotateZ and RotateX methods of the actor but
    the components of the orientation matrix are used directly since
    they are known without any ambiguity.

    :param vtkActor actor: the vtk actor.
    :param orientation: an instance of the :py:class:`pymicro.crystal.microstructure.Orientation` class
    '''
    transform = actor.GetUserTransform()
    if transform == None:
        transform = vtk.vtkTransform()
        transform.Identity()
    Bt = orientation.orientation_matrix().transpose()
    m = vtk.vtkMatrix4x4()
    m.Identity()
    m.DeepCopy((Bt[0, 0], Bt[0, 1], Bt[0, 2], 0,
                Bt[1, 0], Bt[1, 1], Bt[1, 2], 0,
                Bt[2, 0], Bt[2, 1], Bt[2, 2], 0,
                0, 0, 0, 1))
    transform.Concatenate(m)
    actor.SetUserTransform(transform)


def load_STL_actor(name, ext='STL', verbose=False, color=grey, feature_edges=False):
    '''Read a STL file and return the corresponding vtk actor.

    :param str name: the base name of the file to read.
    :param str ext: extension of the file to read.
    :param bool verbose: verbose mode.
    :param tuple color: the color to use for the actor.
    :param bool feature_edges: show boundary edges (default False).
    :return: the 3d solid in the form of a vtk actor.
    '''
    if verbose: print 'adding part: %s' % name
    part = vtk.vtkSTLReader()
    part.SetFileName(name + '.' + ext)
    part.Update()
    partMapper = vtk.vtkPolyDataMapper()
    partMapper.SetInputConnection(part.GetOutputPort())
    partActor = vtk.vtkActor()
    partActor.SetMapper(partMapper)
    partActor.GetProperty().SetColor(color)
    if feature_edges:
        extract = vtk.vtkFeatureEdges()
        extract.SetInputConnection(part.GetOutputPort())
        edge_mapper = vtk.vtkPolyDataMapper()
        edge_mapper.SetInputConnection(extract.GetOutputPort())
        edge_mapper.SetScalarVisibility(0)
        edge_actor = vtk.vtkActor()
        edge_actor.SetMapper(edge_mapper)
        edge_actor.GetProperty().SetColor(0, 0, 0)
        edge_actor.GetProperty().SetLineWidth(3.0)
        stl_part = vtk.vtkAssembly()
        stl_part.AddPart(partActor)
        stl_part.AddPart(edge_actor)
        return stl_part
    else:
        return partActor


def read_image_data(file_name, size, header_size=0, data_type='uint8', verbose=False):
    '''
    vtk helper function to read a 3d data file.
    The size is needed in the form (x, y, z) as well a string describing
    the data type in numpy format (uint8 is assumed by default).
    Lower file left and little endian are assumed.

    *Parameters*

    **file_name**: the name of the file to read.

    **size**: a sequence of three numbers describing the size of the 3d data set

    **header_size**: size of the header to skip in bytes (0 by default)

    **data_type**: a string describing the data type in numpy format ('uint8' by default)

    **verbose**: verbose mode (False by default)

    *Returns*

    A VTK data array
    '''
    vtk_type = to_vtk_type(data_type)
    if verbose:
        print 'reading scan %s with size %dx%dx%d using vtk type %d' % \
              (file_name, size[0], size[1], size[2], vtk_type)
    reader = vtk.vtkImageReader2()  # 2 is faster
    reader.SetDataScalarType(vtk_type)
    reader.SetFileDimensionality(3)
    reader.SetHeaderSize(header_size)
    reader.SetDataByteOrderToLittleEndian()
    reader.FileLowerLeftOn()
    reader.SetDataExtent(0, size[0] - 1, 0, size[1] - 1, 0, size[2] - 1)
    reader.SetNumberOfScalarComponents(1)
    reader.SetDataOrigin(0, 0, 0)
    reader.SetFileName(file_name)
    reader.Update()
    data = reader.GetOutput()
    return data


def data_outline(data, corner=False, color=black):
    '''
    vtk helper function to draw a bounding box around a volume.
    '''
    if corner:
        outlineFilter = vtk.vtkOutlineCornerFilter()
    else:
        outlineFilter = vtk.vtkOutlineFilter()
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        outlineFilter.SetInputData(data)
    else:
        outlineFilter.SetInput(data)
    outlineMapper = vtk.vtkPolyDataMapper()
    outlineMapper.SetInputConnection(outlineFilter.GetOutputPort())
    outline = vtk.vtkActor()
    outline.SetMapper(outlineMapper)
    outline.GetProperty().SetColor(color)
    return outline


def box_3d(size=(100, 100, 100), line_color=black):
    '''
    vtk helper function to draw a box of a given size.
    '''
    l = Lattice.orthorombic(size[0], size[1], size[2])
    grid = lattice_grid(l, origin=[0., 0., 0.])
    edges = vtk.vtkExtractEdges()
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        edges.SetInputData(grid)
    else:
        edges.SetInput(grid)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(edges.GetOutputPort())
    box = vtk.vtkActor()
    box.SetMapper(mapper)
    box.GetProperty().SetColor(line_color)
    return box


def build_line_mesh(points):
    '''Function to construct a vtkUnstructuredGrid representing a line mesh.
    
    :param list points: the list of points.
    :returns line_mesh: the vtkUnstructuredGrid.
    '''
    line_mesh = vtk.vtkUnstructuredGrid()
    nodes = vtk.vtkPoints()
    nodes.SetNumberOfPoints(len(points));
    for i in range(len(points)):
        (x, y, z) = points[i]
        nodes.InsertPoint(i, x, y, z)
    line_mesh.SetPoints(nodes)
    for i in range(len(points) - 1):
        Ids = vtk.vtkIdList()
        Ids.InsertNextId(i)
        Ids.InsertNextId(i + 1)
        line_mesh.InsertNextCell(4, Ids)
    return line_mesh

def line_3d(start_point, end_point):
    '''
    vtk helper function to draw a line in a 3d scene.
    '''
    linePoints = vtk.vtkPoints()
    linePoints.SetNumberOfPoints(2)
    linePoints.InsertPoint(0, start_point[0], start_point[1], start_point[2])
    linePoints.InsertPoint(1, end_point[0], end_point[1], end_point[2])
    aLine = vtk.vtkLine()
    aLine.GetPointIds().SetId(0, 0)
    aLine.GetPointIds().SetId(1, 1)
    aLineGrid = vtk.vtkUnstructuredGrid()
    aLineGrid.Allocate(1, 1)
    aLineGrid.InsertNextCell(aLine.GetCellType(), aLine.GetPointIds())
    aLineGrid.SetPoints(linePoints)
    aLineMapper = vtk.vtkDataSetMapper()
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        aLineMapper.SetInputData(aLineGrid)
    else:
        aLineMapper.SetInput(aLineGrid)
    aLineActor = vtk.vtkActor()
    aLineActor.SetMapper(aLineMapper)
    return aLineActor


def circle_line_3d(center=(0, 0, 0), radius=1, normal=(0, 0, 1), resolution=1):
    '''Function to draw a circle in a 3d scene.

    :params tuple center: the center of the cricle.
    :params float radius: the radius of the circle.
    :params tuple normal: the normal to the plane of the circle.
    :params float resolution: the resolution in degree.
    :return vtkActor: The method return a vtkActor that can be directly \
    added to a 3d scene.
    '''
    n = int(360 / resolution)
    linePoints = vtk.vtkPoints()
    linePoints.SetNumberOfPoints(n + 1)
    aLineGrid = vtk.vtkUnstructuredGrid()
    aLineGrid.Allocate(1, n)
    aLineGrid.SetPoints(linePoints)
    linePoints.InsertPoint(0, center[0] + radius, center[1], center[2])  # starting point
    for i in range(n):
        linePoints.InsertPoint(i + 1, \
                               center[0] + radius * np.cos(resolution * (i + 1) * np.pi / 180), \
                               center[1] + radius * np.sin(resolution * (i + 1) * np.pi / 180), \
                               center[2])
        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, i)
        line.GetPointIds().SetId(1, i + 1)
        aLineGrid.InsertNextCell(line.GetCellType(), line.GetPointIds())
    aLineMapper = vtk.vtkDataSetMapper()
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        aLineMapper.SetInputData(aLineGrid)
    else:
        aLineMapper.SetInput(aLineGrid)
    aLineActor = vtk.vtkActor()
    aLineActor.SetMapper(aLineMapper)
    return aLineActor


def contourFilter(data, value, color=grey, diffuseColor=grey, opacity=1.0, discrete=False):
    '''This method create an actor running a contour filter through the
    given data set.

    The data set can be equally given in numpy or VTK format (it will be
    converted to VTK if needed). The method may require a fair amount of
    memory so downsample your data if you can.

    :params data: the dataset to map, in numpy or VTK format.
    :params float value: numeric value to use for contouring.
    :params color: the solid color to use for the contour actor.
    :params diffuseColor: the diffusive color to use for the contour actor.
    :params float opacity: the opacity value to use for the actor (1.0 by default).
    :params bool discrete: use vtkDiscreteMarchingCubes if True (False by default).
    :returns: The method return a vtkActor that can be directly added to a renderer.
    '''
    if type(data) == np.ndarray:
        data = numpy_array_to_vtk_grid(data, False)
    if discrete:
        contour = vtk.vtkDiscreteMarchingCubes()
    else:
        contour = vtk.vtkContourFilter()
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        contour.SetInputData(data)
    else:
        contour.SetInput(data)
    contour.SetValue(0, value)
    contour.Update()
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(contour.GetOutputPort())
    normals.SetFeatureAngle(60.0)
    mapper = vtk.vtkPolyDataMapper()
    mapper.ScalarVisibilityOff()
    mapper.SetInputConnection(normals.GetOutputPort())
    mapper.Update()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetDiffuseColor(diffuseColor)
    actor.GetProperty().SetSpecular(.4)
    actor.GetProperty().SetSpecularPower(10)
    actor.GetProperty().SetOpacity(opacity)
    return actor


def volren(data, alpha_channel=None, color_function=None):
    '''Volume rendering for a 3d array using standard ray casting.

      :param data: the dataset to render, in numpy or VTK format.
      :param alpha_channel: a vtkPiecewiseFunction instance, default to linear between 0 and 255 if not given.
      :returns: The method return a vtkVolume that can be added to a renderer.
    '''
    if type(data) == np.ndarray:
        data = numpy_array_to_vtk_grid(data, False)
    if alpha_channel == None:
        alpha_channel = vtk.vtkPiecewiseFunction()
        alpha_channel.AddPoint(0, 0.0)
        alpha_channel.AddPoint(255, 0.5)
    volumeProperty = vtk.vtkVolumeProperty()
    if color_function != None:
        volumeProperty.SetColor(color_function)
    volumeProperty.SetScalarOpacity(alpha_channel)
    compositeFunction = vtk.vtkVolumeRayCastCompositeFunction()
    volumeMapper = vtk.vtkVolumeRayCastMapper()
    volumeMapper.SetVolumeRayCastFunction(compositeFunction)
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        volumeMapper.SetInputData(data)
    else:
        volumeMapper.SetInput(data)
    volume = vtk.vtkVolume()
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)
    return volume


def elevationFilter(data, value, (low, high), low_point=None, high_point=None):
    '''Create an isosurface and map it with an elevation filter.

    :param data: the dataset to map, in VTK format.
    :param float value: the value to use to create the isosurface.
    :param tuple (low, high): range to use in the elevation filter. \
    :param tuple low_point: lower point defining the axis from which to \
    compute the elevation. If not specified, (0, 0, low) is assumed.
    :param tuple high_point: lower point defining the axis from which to \
    compute the elevation. If not specified, (0, 0, high) is assumed.
    :returns vtkActor: The method return an actor that can be directly \
    added to a renderer.
    '''
    lut = vtk.vtkLookupTable()
    lut.SetHueRange(0.6, 0)
    lut.SetSaturationRange(1.0, 0)
    lut.SetValueRange(0.5, 1.0)
    contour = vtk.vtkDiscreteMarchingCubes()
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        contour.SetInputData(data)
    else:
        contour.SetInput(data)
    contour.SetValue(0, value)
    contour.Update()
    elevation = vtk.vtkElevationFilter()
    elevation.SetInputConnection(contour.GetOutputPort())
    if low_point == None:
        low_point = (0, 0, low)
    if high_point == None:
        high_point = (0, 0, high)
    elevation.SetLowPoint(low_point)
    elevation.SetHighPoint(high_point)
    elevation.SetScalarRange(low, high)
    elevation.ReleaseDataFlagOn()
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(elevation.GetOutputPort())
    normals.SetFeatureAngle(60.0)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetScalarRange(low, high)
    mapper.SetLookupTable(lut)
    mapper.ImmediateModeRenderingOn()
    mapper.SetInputConnection(normals.GetOutputPort())
    mapper.Update()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor


def numpy_array_to_vtk_grid(data, cell_data=True):
    '''Transform a 3d numpy data array into a vtk uniform grid with scalar data.

    :param data: the 3d numpy data array, possibly with 3 components using a 4th dimension.
    :param bool cell_data: boolean to assign cell data or point data ito the grid (True by default).
    :return vtkUniformGrid: The method return a vtkUniformGrid with scalar data initialized from
    the provided numpy array.
    '''
    if not data.ndim in [3, 4]:
        print('warning, data array dimension must be 3 or 4 (for multi-component)')
        return None
    if data.ndim == 3:
        size = np.shape(data)
        vtk_data_array = numpy_support.numpy_to_vtk(np.ravel(data, order='F'), deep=1)
    elif data.ndim == 4:
        print('treating the 4th dimension as 3 different components')
        assert data.shape[3] == 3
        size = np.shape(data)[:3]
        vtk_data_array = vtk.vtkUnsignedCharArray()
        vtk_data_array.SetNumberOfComponents(data.shape[3])
        n = np.prod(size)
        vtk_data_array.SetNumberOfTuples(n)
        for i in range(3):
            vtk_data_array.CopyComponent(i, numpy_support.numpy_to_vtk(np.ravel(data[:, :, :, i], order='F'), deep=1), 0)
    grid = vtk.vtkUniformGrid()
    if cell_data:
        grid.SetExtent(0, size[0], 0, size[1], 0, size[2])
        grid.GetCellData().SetScalars(vtk_data_array)
    else:
        grid.SetExtent(0, size[0] - 1, 0, size[1] - 1, 0, size[2] - 1)
        grid.GetPointData().SetScalars(vtk_data_array)
    grid.SetSpacing(1, 1, 1)
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        grid.SetScalarType(vtk.VTK_UNSIGNED_CHAR, vtk.vtkInformation())
    else:
        grid.SetScalarType(vtk.VTK_UNSIGNED_CHAR)
    return grid


def map_data_with_clip(data, lut=gray_cmap(), cell_data=True):
    '''This method construct an actor to map a 3d dataset.

    1/8 of the data is clipped out to have a better view of the interior.
    It requires a fair amount of memory so downsample your data if you can
    (it may not be visible at all on the resulting image).

    .. code-block:: python

      data = read_image_data(im_file, size)
      ren = vtk.vtkRenderer()
      actor = map_data_with_clip(data)
      ren.AddActor(actor)
      render(ren, display=True)

    .. figure:: _static/pa66gf30_clip_3d.png
       :width: 300 px
       :alt: pa66gf30_clip_3d
       :align: center

       A 3D view of a polyamid sample with reinforcing glass fibers.

    *Parameters*

    **data**: the dataset to map, in numpy or VTK format.

    **lut**: VTK look up table (default: `gray_cmap`).

    **cell_data**: boolean to map cell data or point data if False (True by default)

    *Returns*

    The method return a vtkActor that can be directly added to a renderer.
    '''
    # implicit function
    bbox = vtk.vtkBox()
    if type(data) == np.ndarray:
        size = data.shape
        bbox.SetXMin(size[0] / 2., -1, size[2] / 2.)
        bbox.SetXMax(size[0] + 1, size[1] / 2., size[2] + 1)
    else:
        e = 0.001
        bb = data.GetBounds()
        bbox.SetXMin((bb[1] - bb[0]) / 2., bb[2] - e, (bb[5] - bb[4]) / 2.)
        bbox.SetXMax(bb[1] + e, (bb[3] - bb[2]) / 2., bb[5] + e)
    return map_data(data, bbox, lut=lut, cell_data=cell_data)


def map_data(data, function, lut=gray_cmap(), cell_data=True):
    '''This method construct an actor to map a 3d dataset.

    It requires a fair amount of memory so downsample your data if you can
    (it may not be visible at all on the resulting image).

    *Parameters*

    **data**: the dataset to map, in numpy or VTK format.

    **function**: VTK implicit function where to map the data.

    **lut**: VTK look up table (default: `gray_cmap`).

    **cell_data**: boolean to map cell data or point data if False (True by default)

    *Returns*

    The method return a vtkActor that can be directly added to a renderer.
    '''
    if type(data) == np.ndarray:
        data = numpy_array_to_vtk_grid(data, cell_data)
    # use extract geometry filter to access the data
    extract = vtk.vtkExtractGeometry()
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        extract.SetInputData(data)
    else:
        extract.SetInput(data)
    extract.ExtractInsideOff()
    extract.ExtractBoundaryCellsOn()
    extract.SetImplicitFunction(function)

    mapper = vtk.vtkDataSetMapper()
    mapper.ScalarVisibilityOn()
    mapper.SetLookupTable(lut)
    mapper.UseLookupTableScalarRangeOn()
    if cell_data:
        mapper.SetScalarModeToUseCellData()
    else:
        mapper.SetScalarModeToUsePointData()
    mapper.SetColorModeToMapScalars()
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        mapper.SetInputConnection(extract.GetOutputPort())
        # with VTK 6, since SetInputData does not create a pipeline, we can also use:
        # extract.Update()
        # mapper.SetInputData(extract.GetOutput())
    else:
        mapper.SetInput(extract.GetOutput())
    mapper.Update()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor


def set_opacity(assembly, opacity):
    collection = vtk.vtkPropCollection()
    assembly.GetActors(collection)
    for i in range(collection.GetNumberOfItems()):
        collection.GetItemAsObject(i).GetProperty().SetOpacity(opacity)


def color_bar(title, lut=None, fmt='%.1e', width=0.5, height=0.075, num_labels=7, font_size=26):
    bar = vtk.vtkScalarBarActor()
    if not lut:
        lut = jet_cmap()
    bar.SetLookupTable(lut)
    bar.SetTitle(title)
    bar.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    bar.GetPositionCoordinate().SetValue(0.5 * (1 - width), 0.025)
    bar.SetOrientationToHorizontal()
    bar.SetLabelFormat(fmt)
    bar.GetLabelTextProperty().SetColor(0, 0, 0)
    bar.GetTitleTextProperty().SetColor(0, 0, 0)
    bar.GetLabelTextProperty().SetFontSize(font_size)
    bar.GetTitleTextProperty().SetFontSize(font_size)
    bar.SetWidth(width)
    bar.SetHeight(height)
    bar.SetNumberOfLabels(num_labels)
    return bar


def text(text, font_size=20, color=(0, 0, 0), hor_align='center', coords=(0.5, 0.5)):
    '''Create a 2D text actor to add to a 3d scene.

    :params int font_size: the font size (20 by default).
    :params tuple color: the face color (black by default).
    :params str hor_align: horizontal alignment, should be 'left', 'center' or 'right' (center by default).
    :params tuple coords: a sequence of two values between 0 and 1.
    :returns an actor for the text to add to a renderer.
    '''
    textMapper = vtk.vtkTextMapper()
    textMapper.SetInput(text)
    tprop = textMapper.GetTextProperty()
    tprop.SetFontSize(font_size)
    tprop.SetFontFamilyToArial()
    tprop.BoldOff()
    if hor_align == 'left':
        tprop.SetJustificationToLeft()
    elif hor_align == 'center':
        tprop.SetJustificationToCentered()
    elif hor_align == 'right':
        tprop.SetJustificationToRight()
    tprop.SetColor(color)
    textActor = vtk.vtkActor2D()
    textActor.SetMapper(textMapper)
    textActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    textActor.GetPositionCoordinate().SetValue(coords[0], coords[1])
    return textActor


def setup_camera(size=(100, 100, 100)):
    '''Setup the camera with usual viewing parameters.

    The camera is looking at the center of the data with the Z-axis vertical.

    *Parameters*

    **size**: the size of the 3d data set (100x100x100 by default).

    '''
    cam = vtk.vtkCamera()
    cam.SetViewUp(0, 0, 1)
    cam.SetPosition(2 * size[0], -2 * size[1], 2 * size[2])
    cam.SetFocalPoint(0.5 * size[0], 0.5 * size[1], 0.5 * size[2])
    cam.SetClippingRange(1, 10 * max(size))
    return cam


def render(ren, ren_size=(600, 600), display=True, save=False, name='render_3d.png', key_pressed_callback=None):
    '''Render the VTK scene in 3D.

    Given a `vtkRenderer`, this function does the actual 3D rendering. It
    can be used to display the scene interactlively and/or save a still
    image in png format.

    *Parameters*

    **ren**: the VTK renderer with containing all the actors.

    **ren_size**: a tuple with two value to set the size of the image in
    pixels (defalut 600x600).

    **display**: a boolean to control if the scene has to be displayed
    interactively to the user (default True).

    **save**: a boolean to to control if the scene has to be saved as a
    png image (default False).

    **name**: a string to used when saving the scene as an image (default
    is 'render_3d.png').

    **key_pressed_callback** a function (functions are first class variables)
    called in interactive mode when a key is pressed.
    '''
    # Create a window for the renderer
    if save:
        renWin = vtk.vtkRenderWindow()
        renWin.AddRenderer(ren)
        renWin.SetSize(ren_size)
        # capture the display and write a png image
        w2i = vtk.vtkWindowToImageFilter()
        writer = vtk.vtkPNGWriter()
        w2i.SetInput(renWin)
        w2i.Update()
        writer.SetInputConnection(w2i.GetOutputPort())
        writer.SetFileName(name)
        renWin.Render()
        writer.Write()
    if display:
        renWin = vtk.vtkRenderWindow()
        renWin.AddRenderer(ren)
        renWin.SetSize(ren_size)
        # Start the initialization and rendering
        iren = vtk.vtkRenderWindowInteractor()
        iren.SetRenderWindow(renWin)
        if key_pressed_callback:
            iren.AddObserver("KeyPressEvent", key_pressed_callback)
        renWin.Render()
        iren.Initialize()
        iren.Start()


def show_array(data, map_scalars=False, lut=None, hide_zero_values=True):
    '''Create a 3d actor representing a numpy array.

    Given a 3d array, this function compute the skin of the volume.
    The scalars can be mapped to the created surface and the colormap
    adjusted. If the data is in numpy format it is converted to VTK first.

    :param data: the dataset, in numpy or VTK format.
    :param bool map_scalars: map the scalar in the data array to the created surface (False by default).
    :param lut: a vtk lookup table (colormap) used to map the scalars.
    :return: a vtk actor that can be added to a rendered to show the 3d array.
    '''
    if type(data) == np.ndarray:
        grid = numpy_array_to_vtk_grid(data, cell_data=True)
        if hide_zero_values:
            visible = numpy_support.numpy_to_vtk(np.ravel(data > 0, order='F').astype(np.uint8), deep=1)
            grid.SetCellVisibilityArray(visible)
            # grid.SetPointVisibilityArray(visible)
        size = data.shape
        bounds = (0, size[0], 0, size[1], 0, size[2])
    else:
        grid = data
        bounds = grid.GetBounds()
        size = (bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])

    # use extract geometry filter to access the data
    extract = vtk.vtkExtractGeometry()
    # extract = vtk.vtkExtractVOI() # much faster but seems not to work with blanking
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        extract.SetInputData(grid)
    else:
        extract.SetInput(grid)
    extract.ExtractInsideOn()
    extract.ExtractBoundaryCellsOn()
    bbox = vtk.vtkBox()
    bbox.SetXMin(bounds[0::2])
    bbox.SetXMax(bounds[1::2])
    extract.SetImplicitFunction(bbox)
    extract.Update()
    return show_mesh(extract.GetOutput(), map_scalars, lut)


def show_mesh(grid, map_scalars=False, lut=None, show_edges=False, edge_color=(0., 0., 0.), edge_line_width=1.0):
    '''Create a 3d actor representing a mesh.

    :param grid: the vtkUnstructuredGrid object.
    :param bool map_scalars: map the scalar in the data array to the created surface (False by default).
    :param lut: a vtk lookup table (colormap) used to map the scalars.
    :param bool show_edes: display the mesh edges (False by default).
    :param tuple edge_color: color to use for the mesh edges (black by default).
    :param float edge_line_width: width of the edge lines (1.0 by default).
    :return: a vtk actor that can be added to a rendered to show the 3d array.
    '''
    mapper = vtk.vtkDataSetMapper()
    mapper.ScalarVisibilityOff()
    if map_scalars:
        mapper.ScalarVisibilityOn()
        mapper.UseLookupTableScalarRangeOn()
        mapper.SetScalarModeToUseCellData()
        mapper.SetColorModeToMapScalars()
        if not lut:
            # default to the usual gray colormap
            lut = gray_cmap()
        mapper.SetLookupTable(lut)
    '''
    # we should be able to use the normals ?
    extract = vtk.vtkGeometryFilter() # from unstructured grid to poly data
    extract.SetInputData(grid)
    extract.Update()
    print('number of points in poly data = %d' % extract.GetOutput().GetNumberOfPoints())
    mapper = vtk.vtkPolyDataMapper()
    #normals = vtk.vtkPolyDataNormals()
    #normals.SetInputConnection(extract.GetOutputPort())
    #normals.SetFeatureAngle(60.0)
    mapper.SetInputConnection(extract.GetOutputPort())
    '''
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        mapper.SetInputData(grid)
    else:
        mapper.SetInput(grid)
    mapper.Update()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    if show_edges:
        actor.GetProperty().EdgeVisibilityOn()
        actor.GetProperty().SetEdgeColor(edge_color)
        actor.GetProperty().SetLineWidth(edge_line_width)
    actor.GetProperty().SetSpecular(.4)
    actor.GetProperty().SetSpecularPower(10)
    actor.GetProperty().SetOpacity(1.0)
    return actor


def show_grains(data, num_colors=2048):
    '''Create a 3d actor of all the grains in a labeled numpy array.

    Given a 3d numpy array, this function compute the skin of all the
    grains (labels > 0). the background is assumed to be zero and is
    removed. The actor produced is colored by the grain ids using the
    random color map, see `rand_cmap`.

    *Parameters*

    **data**: a labeled numpy array.

    **num_colors**: number of colors in the lookup table (2048 by default)

    Returns a vtk actor that can be added to a rendered to show all the
    grains colored by their id.
    '''
    grain_lut = rand_cmap(N=num_colors, first_is_black=True, table_range=(0, num_colors - 1))
    grains = show_array(data, map_scalars=True, lut=grain_lut)
    return grains


def show_boundaries(grid, array_id=0, array_name=None, write=False):
    '''Create an actor representing the boundaries separating different
    values of a given array. The values have to be one of the integer type.

    :param vtkUnstructuredGrid grid: the unstructured grid referencing the data array.
    :param int array_id: the index of the array to process (default 0).
    :param str array_name: the name of the array to process.
    :param bool write: flag to write the boundary polydata to the disk.
    :return: a VTK actor containing the boundaries.
    '''
    # if array_name is specified, find the corresponding array
    if array_name:
        array_id = -1
        for i in range(grid.GetCellData().GetNumberOfArrays()):
            if grid.GetCellData().GetArray(i).GetName() == array_name:
                array_id = i
                break
    if array_id < 0:
        print('warning, array %s not found in CellData arrays' % array_name)
        return
    array = grid.GetCellData().GetArray(array_id)
    assert array.GetName() == array_name
    assert array.GetDataType() == vtk.VTK_UNSIGNED_SHORT or array.GetDataType() == vtk.VTK_UNSIGNED_CHAR or array.GetDataType() == vtk.VTK_INT
    grid.GetCellData().SetActiveScalars(array_name)
    # we use a vtkAppendPolyData to gather all the boundaries
    append = vtk.vtkAppendPolyData()
    gids_range = array.GetRange()
    print('field range used to find the boudnaries:', gids_range)
    for gid in range(int(gids_range[0]), 1 + int(gids_range[1])):
        print('trying gid=%d' % gid)
        thresh = vtk.vtkThreshold()
        thresh.SetInputData(grid)
        thresh.ThresholdBetween(gid - 0.5, gid + 0.5)
        thresh.SetInputArrayToProcess(1, 0, 0, 0, array_name)
        geometryFilter = vtk.vtkGeometryFilter()
        geometryFilter.SetInputConnection(thresh.GetOutputPort())
        boundariesExtractor = vtk.vtkFeatureEdges()
        boundariesExtractor.SetInputConnection(geometryFilter.GetOutputPort())
        boundariesExtractor.BoundaryEdgesOn()
        append.AddInputConnection(boundariesExtractor.GetOutputPort())
    # remove any duplicate points
    clean = vtk.vtkCleanPolyData()
    clean.SetInputConnection(append.GetOutputPort())
    clean.Update()
    if write:
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName('gb.vtp')
        writer.SetInputConnection(clean.GetOutputPort())
        writer.Write()
        print('writting gb.vtp')
    boundariesActor = edges_actor(clean.GetOutput(), linewidth=4.0, linecolor=black)
    return boundariesActor


def edges_actor(polydata, linewidth=1.0, linecolor=black):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    mapper.ScalarVisibilityOff()
    mapper.Update()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().EdgeVisibilityOn()
    actor.GetProperty().SetColor(linecolor)
    actor.GetProperty().SetLineWidth(linewidth)
    return actor


def xray_arrow():
    xrays_arrow = vtk.vtkArrowSource()
    xrays_mapper = vtk.vtkPolyDataMapper()
    xrays_mapper.SetInputConnection(xrays_arrow.GetOutputPort())
    xrays = vtk.vtkActor()
    xrays.SetMapper(xrays_mapper)
    return xrays


def slits(size, x_slits=0):
    '''Create a 3d schematic represenation of X-ray slits.

    The 3d represenation is made of 4 corners of the given size along
    the Y and Z axes.

    **Parameters**:

    *size*: a (X,Y,Z) tuple giving the size of the illuminated volume.
    The first value of the tuple is not used.

    *x_slits*: position of the slits along the X axis (0 be default).

    **Returns**:

    A vtk assembly of the 4 corners representing the slits.
    '''
    slits = vtk.vtkAssembly()
    corner_points = np.empty((3, 3, 4), dtype=np.float)
    corner_points[:, 0, 0] = [x_slits, -0.6 * size[1] / 2, -size[2] / 2]
    corner_points[:, 1, 0] = [x_slits, -size[1] / 2, -size[2] / 2]
    corner_points[:, 2, 0] = [x_slits, -size[1] / 2, -0.6 * size[2] / 2]
    corner_points[:, 0, 1] = [x_slits, -0.6 * size[1] / 2, size[2] / 2]
    corner_points[:, 1, 1] = [x_slits, -size[1] / 2, size[2] / 2]
    corner_points[:, 2, 1] = [x_slits, -size[1] / 2, 0.6 * size[2] / 2]
    corner_points[:, 0, 2] = [x_slits, 0.6 * size[1] / 2, -size[2] / 2]
    corner_points[:, 1, 2] = [x_slits, size[1] / 2, -size[2] / 2]
    corner_points[:, 2, 2] = [x_slits, size[1] / 2, -0.6 * size[2] / 2]
    corner_points[:, 0, 3] = [x_slits, 0.6 * size[1] / 2, size[2] / 2]
    corner_points[:, 1, 3] = [x_slits, size[1] / 2, size[2] / 2]
    corner_points[:, 2, 3] = [x_slits, size[1] / 2, 0.6 * size[2] / 2]
    for c in range(4):
        linePoints = vtk.vtkPoints()
        linePoints.SetNumberOfPoints(3)
        linePoints.InsertPoint(0, corner_points[:, 0, c])
        linePoints.InsertPoint(1, corner_points[:, 1, c])
        linePoints.InsertPoint(2, corner_points[:, 2, c])
        line1 = vtk.vtkLine()
        line1.GetPointIds().SetId(0, 0)
        line1.GetPointIds().SetId(1, 1)
        line2 = vtk.vtkLine()
        line2.GetPointIds().SetId(0, 1)
        line2.GetPointIds().SetId(1, 2)
        slitCorner1Grid = vtk.vtkUnstructuredGrid()
        slitCorner1Grid.Allocate(2, 1)
        slitCorner1Grid.InsertNextCell(line1.GetCellType(), line1.GetPointIds())
        slitCorner1Grid.InsertNextCell(line2.GetCellType(), line2.GetPointIds())
        slitCorner1Grid.SetPoints(linePoints)
        slitCorner1Mapper = vtk.vtkDataSetMapper()
        if vtk.vtkVersion().GetVTKMajorVersion() > 5:
            slitCorner1Mapper.SetInputData(slitCorner1Grid)
        else:
            slitCorner1Mapper.SetInput(slitCorner1Grid)
        slitCorner1Actor = vtk.vtkActor()
        slitCorner1Actor.SetMapper(slitCorner1Mapper)
        slitCorner1Actor.GetProperty().SetLineWidth(3.0)
        slitCorner1Actor.GetProperty().SetDiffuseColor(black)
        slits.AddPart(slitCorner1Actor)
    return slits


def pin_hole(inner_radius=100, outer_radius=200):
    pin_hole = vtk.vtkAssembly()
    disc = vtk.vtkDiskSource()
    disc.SetCircumferentialResolution(50)
    disc.SetInnerRadius(inner_radius)
    disc.SetOuterRadius(outer_radius)
    disc_mapper = vtk.vtkPolyDataMapper()
    disc_mapper.SetInputConnection(disc.GetOutputPort())
    discActor = vtk.vtkActor()
    discActor.SetMapper(disc_mapper)
    discActor.GetProperty().SetColor(black)
    pin_hole.AddPart(discActor)
    pin_hole.RotateY(90)
    return pin_hole


def zone_plate(thk=50, sep=25, n_rings=5):
    '''Create a 3d schematic represenation of a Fresnel zone plate.

    The 3d represenation is made of a number or concentric rings separated
    by a specific distance which control the X-ray focalisation.

    **Parameters**:

    *thk*: ring thickness (50 by default).

    *sep*: ring spacing (25 by default).

    **Returns**:

    A vtk assembly of the rings composing the Fresnel zone plate.
    '''
    zone_plate = vtk.vtkAssembly()
    for i in range(n_rings):
        disc = vtk.vtkDiskSource()
        disc.SetCircumferentialResolution(50)
        disc.SetInnerRadius(i * (thk + sep))
        disc.SetOuterRadius((i + 1) * thk + i * sep)
        disc_mapper = vtk.vtkPolyDataMapper()
        disc_mapper.SetInputConnection(disc.GetOutputPort())
        discActor = vtk.vtkActor()
        discActor.SetMapper(disc_mapper)
        zone_plate.AddPart(discActor)
    zone_plate.RotateY(90)
    return zone_plate


def grid_vol_view(scan):
    s_size = scan[:-4].split('_')[-2].split('x')
    s_type = scan[:-4].split('_')[-1]
    size = [int(s_size[0]), int(s_size[1]), int(s_size[2])]
    # prepare a uniform grid to receive the image data
    uGrid = vtk.vtkUniformGrid()
    uGrid.SetExtent(0, size[0], 0, size[1], 0, size[2])
    uGrid.SetOrigin(0, 0, 0)
    uGrid.SetSpacing(1, 1, 1)
    uGrid.SetScalarType(to_vtk_type(s_type))
    # read the actual image data
    print 'reading scan %s with size %dx%dx%d using type %d' % \
          (scan, size[0], size[1], size[2], to_vtk_type(s_type))
    reader = vtk.vtkImageReader2()  # 2 is faster
    reader.SetDataScalarType(to_vtk_type(s_type))
    reader.SetFileDimensionality(3)
    reader.SetHeaderSize(0)
    reader.SetDataByteOrderToLittleEndian()
    reader.FileLowerLeftOn()
    reader.SetDataExtent(0, size[0] - 1, 0, size[1] - 1, 0, size[2] - 1)
    reader.SetNumberOfScalarComponents(1)
    reader.SetDataOrigin(0, 0, 0)
    reader.SetFileName(scan)
    reader.Update()
    data = reader.GetOutput()
    # expose the image data array
    array = data.GetPointData().GetScalars()
    uGrid.GetCellData().SetScalars(array)
    uGrid.SetCellVisibilityArray(array)
    # create random lut
    lut = rand_cmap(N=2048, first_is_black=True, table_range=(0, 2047))
    # prepare the implicit function
    bbox = vtk.vtkBox()
    bbox.SetXMin(0, 0, 0)
    bbox.SetXMax(size[0], size[1], size[2])
    # use extract geometry filter to clip data
    extract = vtk.vtkExtractGeometry()
    extract.SetInput(uGrid)
    # extract.ExtractInsideOn()
    extract.SetImplicitFunction(bbox)
    extract.ExtractBoundaryCellsOn()
    # create mapper
    print 'creating actors'
    mapper = vtk.vtkDataSetMapper()
    mapper.SetLookupTable(lut)
    mapper.SetInput(extract.GetOutput())
    mapper.UseLookupTableScalarRangeOn()
    mapper.SetScalarModeToUseCellData();
    mapper.SetColorModeToMapScalars();
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    # set up camera
    cam = vtk.vtkCamera()
    cam.SetViewUp(0, 0, 1)
    cam.SetPosition(size[0], -size[1], 200)
    cam.SetFocalPoint(size[0] / 2, size[1] / 2, size[2] / 2)
    cam.Dolly(0.6)
    cam.SetClippingRange(0, 1000)
    # add axes actor
    l = 0.5 * np.mean(size)
    axes = axes_actor(length=l, axisLabels=True)
    # Create renderer
    ren = vtk.vtkRenderer()
    ren.SetBackground(1.0, 1.0, 1.0)
    ren.AddActor(actor)
    # ren.AddActor(outline)
    ren.AddViewProp(axes);
    ren.SetActiveCamera(cam)

    # Create a window for the renderer
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetSize(600, 600)
    # Start the initialization and rendering
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    renWin.Render()
    iren.Initialize()
    iren.Start()
    print 'done'


def vol_view(scan):
    # TODO change from scan name to numpy array
    s_size = scan[:-4].split('_')[-2].split('x')
    s_type = scan[:-4].split('_')[-1]
    size = [int(s_size[0]), int(s_size[1]), int(s_size[2])]
    print 'reading scan %s with size %dx%dx%d using type %d' % \
          (scan, size[0], size[1], size[2], to_vtk_type(s_type))
    reader = vtk.vtkImageReader2()  # 2 is faster
    reader.SetDataScalarType(to_vtk_type(s_type))
    reader.SetFileDimensionality(3)
    reader.SetHeaderSize(0)
    reader.SetDataByteOrderToLittleEndian()
    reader.FileLowerLeftOn()
    reader.SetDataExtent(0, size[0] - 1, 0, size[1] - 1, 0, 100)  # size[2]-1)
    reader.SetNumberOfScalarComponents(1)
    reader.SetDataOrigin(0, 0, 0)
    reader.SetFileName(scan)
    data = reader.GetOutput()
    # threshold to remove background
    print 'thresholding to remove background'
    thresh = vtk.vtkThreshold()
    if vtk.vtkVersion().GetVTKMajorVersion() > 5:
        thresh.SetInputData(data)
    else:
        thresh.SetInput(data)
    # thresh.SetInputConnection(data)
    thresh.Update()
    thresh.ThresholdByUpper(1.0)
    thresh.SetInputArrayToProcess(1, 0, 0, 0, "ImageFile")
    # create random lut
    lut = rand_cmap(N=2048, first_is_black=True, table_range=(0, 2047))
    # create mapper
    print 'creating actors'
    mapper = vtk.vtkDataSetMapper()
    mapper.SetLookupTable(lut)
    mapper.SetInputConnection(thresh.GetOutputPort())
    # mapper.SetInput(data)
    mapper.UseLookupTableScalarRangeOn()
    mapper.SetScalarModeToUsePointData();
    mapper.SetColorModeToMapScalars();
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    # set up camera
    cam = vtk.vtkCamera()
    cam.SetViewUp(0, 0, 1)
    cam.SetPosition(400, -400, 300)
    cam.SetFocalPoint(size[0], size[1], size[2])
    cam.SetClippingRange(20, 1000)
    # add axes actor
    l = min(size)
    axes = axes_actor(length=l, axisLabels=True)
    # Create renderer
    ren = vtk.vtkRenderer()
    ren.SetBackground(1.0, 1.0, 1.0)
    ren.AddActor(actor)
    # ren.AddActor(outline)
    ren.AddViewProp(axes);
    ren.SetActiveCamera(cam)

    # Create a window for the renderer
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetSize(600, 600)
    # Start the initialization and rendering
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    renWin.Render()
    iren.Initialize()
    iren.Start()
    print 'done'


def ask_for_map_file(dir, scan_name):
    list = {};
    i = 0
    print 'no map file was specified, please chose from the following file available'
    for file in os.listdir(dir):
        if file.startswith(scan_name + '.'):
            i += 1
            list[i] = file
            print ' * ', file, '[', i, ']'
    if i == 0:
        sys.exit('no matching map file could be located, exiting...')
    r = raw_input('chose file by entering the coresponding number [1]: ')

    if r == '':
        return list[1]
    else:
        try:
            ir = int(r)
        except:
            sys.exit('not a number, exiting...')
        else:
            if int(r) < i + 1:
                return list[int(r)]
            else:
                sys.exit('wrong entry, exiting...')
