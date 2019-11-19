'''
Lanim: This is the class that contains all of the information for the LaTeX animation.

Methods:
    * cam_move: This adds a camera movement.
    * cam_zoom: This adds a camera zoom.
    * make_me: This makes the animation.
'''

# Lanim = LaTeX Animation
class Lanim:
    # Initialization parameters:
    #   * lower_left = coordinates of the lower_left corner of the camera
    #   * upper_right = coordinates of the upper_right corner of the camera
    #   * length = number of frames in the animation
    #   * file_name = output file name
    #   * additional = additional TikZ code that is inserted at the top of the file.
    def __init__(self,
                 lower_left = [0, 0],
                 upper_right = [640, 480],
                 length = 1,
                 file_name = 'lanim.tex',
                 additional = ''):

        # Lanim.length = number of frames
        self.length = length
        # Animation.file_name = output file name, should include .tex extension
        self.file_name = file_name
        
        # Camera Information
        # Lanim.camera_center = Coordinates of the camera's center
        self.camera_center = [ (upper_right[i] + lower_left[i])/2 for i in range(2) ]
        # Lanim.camera_offset = Adjustment to camera position is the original
        #                           lower_left corner is not [0, 0]
        self.camera_offset = [ lower_left[i] for i in range(2)]

        # Lanim.camera_size = Corner-to-corner distance for camera, varies with zoom
        self.camera_size = [ upper_right[i] - lower_left[i] for i in range(2) ]
        # Lanim.camera_zoom = Zoom level of the camera
        self.camera_zoom = 1
        
        # Lanim.camera_keyframes = List that contains all the camera movements
        self.camera_keyframes = []

        # Lanim.draw_boundary = TikZ code that produces the actual camera frame
        self.draw_boundary = '\\newcommand{\\BoundingBox}' + \
                             '{{\\clip ({},{}) '.format(lower_left[0], lower_left[1]) + \
                             'rectangle ({},{});}} \n\n'.format(upper_right[0], upper_right[1])
    
        # Lanim.additional = Additional TikZ code to be inserted, such as macros
        self.additional = additional

        # Lanim.contents = List that contains the contents of the Animation
        self.contents = []

    # Camera movement method
    # Note: The x and y coordinates are set as separate Animate objects
    # Parameters:
    #   * frames = list containing the start and end frames of the animation
    #   * end_center = list containing the coordinates of the end location of the
    #                  camera's center
    def cam_move(self, frames, end_center):
        self.camera_keyframes.append(
            Animate(frames = frames,
                    ani_type = 'cam_x',
                    end_value = end_center[0]))
        self.camera_keyframes.append(
            Animate(frames = frames,
                    ani_type = 'cam_y',
                    end_value = end_center[1]))

    # Camera zoom method
    # Parameters:
    #   * frames = list containing the start and end frames of the animation
    #   * end_zoom = the end zoom level of the camera
    def cam_zoom(self, frames, end_zoom):
        self.camera_keyframes.append(
            Animate(frames = frames,
                    ani_type = 'cam_zoom',
                    end_value = end_zoom))

    # Method to create the actual file
    def make_me(self):
        # Open file
        f = open(self.file_name, 'w')
        
        # Write the Preamble
        f.write('\\documentclass[multi={img},preview]{standalone} \n')
        f.write('\\usepackage{amsmath,amssymb} \n')
        f.write('\\usepackage{tikz} \n\n')
        f.write('\\newenvironment{img}{}{} \n\n')
        f.write(self.draw_boundary)
        f.write(self.additional)
        f.write('\n\n\\begin{document} \n')

        # Loop for drawing each frame
        for frame in range(1,self.length + 1):
            print(frame)
            f.write('% Frame {}\n'.format(frame))
            f.write('\\begin{img} \n')
            # The x and y values here chosen so that the output through GIMP is
            # the right size. I'm not sure how this runs on other computers.
            f.write('\\begin{tikzpicture}[x=0.7229pt,y=0.7229pt] \n')
            f.write('\\BoundingBox \n')

            # Check for camera movements.
            for animate in self.camera_keyframes:
                # Set the start_value for camera movements that are just starting
                if animate.start_frame == frame:
                    if animate.ani_type == 'cam_x':
                        animate.start_value = self.camera_center[0]
                    if animate.ani_type == 'cam_y':
                        animate.start_value = self.camera_center[1]
                    if animate.ani_type == 'cam_zoom':
                        animate.start_value = self.camera_zoom

                # Is there an active camera movement?
                if animate.start_frame <= frame and animate.end_frame >= frame:
                    if animate.ani_type == 'cam_x':
                        self.camera_center[0] = animate.linear_interpolate(frame)
                    if animate.ani_type == 'cam_y':
                        self.camera_center[1] = animate.linear_interpolate(frame)
                    if animate.ani_type == 'cam_zoom':
                        self.camera_zoom = animate.linear_interpolate(frame)

            # Rather than moving the camera, we're actually moving the underlying canvas.
            # The desired camera shift is the location of the bottom_left corner, which is
            # based on the location of the center and the size of the camera.
            # The true shift of the canvas is the negative of this plus the offset if the
            # original bottom_left corner was not [0, 0]
            camera_shift = [ self.camera_center[i] - self.camera_size[i]/(2 * self.camera_zoom) for i in range(2) ]
            self.canvas_shift = [ -camera_shift[i] + self.camera_offset[i] for i in range(2) ]

            print('Camera:', self.camera_center, self.canvas_shift, self.camera_zoom)

            # The canvas shift is captured in a single scope around the entire frame contents
            f.write('\\begin{{scope}}[shift={{({},{})}}, '.format(self.canvas_shift[0], self.canvas_shift[1]) + \
                    'transform canvas={{scale={}}} ] \n'.format(self.camera_zoom))

            # Look for active objects in the Lanim
            # All of the code to generate the output is contained in the indivudal classes and
            # called using the draw_me() method.
            for obj in self.contents:
                if obj.start_frame <= frame and (obj.end_frame == 0 or obj.end_frame >= frame):
                    f.write(obj.draw_me(frame))
                    f.write('\n')

            # Close the original canvas shifting scope and finish the frame
            f.write('\\end{scope} \n')
            f.write('\\end{tikzpicture} \n')
            f.write('\\end{img} \n \n')

        f.write('\\end{document} \n')
        f.close()   
        
        return(True)

'''
Animate Class: This is the generic class for all animations, including
camera movements.

Camera Animate Types:
    * cam_x -- change the camera's x coordinate
    * cam_y -- change the camera's y coordinate
    * cam_zoom -- zoom level of the camera

Object Animate Types:
    * obj_x -- change the object's x coordinate
    * obj_y -- change the object's y coordinate
    * obj_rot -- change the object's rotation (in degrees)
    * obj_fade -- change the object's opacity (0 = solid, 1 = transparent)
    * obj_scale -- change the object's scale
    * obj_radius -- change the object's radius (only for Circle objects)

Graphing Animate Types:
    * domain_a -- left endpoint of the domain of a Graph
    * domain_b -- right endpoint of the domain of a Graph

'''

class Animate:
    # Initialization parameters:
    #   * frames = list containing the start and end frames of the animation
    #   * ani_type = string containing the type of the Animate object. This helps
    #                with assigning the updated value to the correct parameter
    #   * end_value = The final value of the animation parameter
    # Note: The start_value is assigned in the first frame of the animation. This
    # allows one animation to interrupt another without needing to calculate the
    # true final values for the first animation.
    def __init__(self,
                 frames = [1,2],
                 ani_type = None,
                 end_value = 0):
        self.start_frame = frames[0]
        self.end_frame = frames[1]
        self.ani_type = ani_type
        self.start_value = None
        self.end_value = end_value
    
    # Linear interpolation method
    # This linearly interpolates the parameter's value between the starting and
    # ending value.
    # Note: At some point, it will be good to include other types of movement,
    # such as something that accelerates and decelerates. This will require
    # another initialization parameter to describe the interpolation type.
    def linear_interpolate(self, frame):
        if self.start_frame == self.end_frame:
            t = 0
        else:
            t = (frame - self.start_frame)/(self.end_frame - self.start_frame)
        return (1-t)*self.start_value + t*self.end_value


'''
Obj: This is a basic object class. It is the parent of all of the other classes.

Forward Dependencies:
    * Obj --> Line
    *     --> Node_on_Path
    *     --> Literal
    *     --> Anim_Obj
'''
class Obj:
    # Initialization parameters:
    #   * ref = This is the name of the object, which can be used for referencing
    #           with the at_point parameter that is in some of the other classes.
    #   * frames = list containing the start and end frames of the animation. Note
    #              that setting the end_frame to 0 means the object will persist
    #              until the end of the animation.
    def __init__(self,
                 ref = 'Obj',
                 frames = [1, 0]):
        
        self.ref = ref
        self.start_frame = frames[0]
        self.end_frame = frames[1]

'''
Line: This creates a multi-line. The point list can be a combination of
coordinates and existing points. The existing points can either be point names
or they can be Point_Obj-s.

Methods:
    * draw_me: Generates the TikZ code to draw the object

Backward Dependencies:
    * Line <-- Obj
'''

class Line(Obj):
    # Initialization parameters:
    #   * ref: This puts a name to the Line object, all points will be named
    #          relative to this by appending a number.
    #   * initial_points: Point_Obj-s or coordinates of the initial line
    #   * closed: If True, closes the line. If false, leaves the line open.
    #   * options: These set the node options (such as anchor, color, etc.)
    def __init__(self,
                 ref = 'Line',
                 frames = [1, 0],
                 initial_points = [ [0,0] ],
                 closed = False,
                 options = ''):

        Obj.__init__(self,
                     ref = ref,
                     frames = frames)
        
        self.closed = closed
        self.options = options

        # Line.points: list of Point_Objs that are created to form the line.
        #              This creates objects that can be referred to by other commands
        self.points = []

        for i in range(len(initial_points)):
            if type(initial_points[i]) == list:
                self.points.append( \
                    Point_Obj(ref = self.ref + str(i),
                              location = initial_points[i],
                              frames = [self.start_frame, self.end_frame]) )
            else:
                self.points.append(initial_points[i])

    def draw_me(self, frame):
        draw_commands = ''
        
        # Lays out the coordinates of Point_Obj-s
        for point in self.points:
            if type(point) == Point_Obj:
                draw_commands += point.draw_me(frame)
        
        # Draws the multi-line
        if type(self.points[0]) == Point_Obj:
            draw_commands += '\draw[{}] ({})'.format(self.options, self.points[0].ref)
        elif type(self.points_list[0]) == str:
            draw_commands += '\draw[{}] ({})'.format(self.options, self.points)
        else:
            draw_commands += '\draw[{}] ({})'.format(self.options, self.points[0])
        for point in self.points[1:]:
            if type(point) == Point_Obj:
                point_name = point.ref
            else:
                point_name = point
            draw_commands += '-- ({})'.format(point_name)

        if self.closed == True:
            draw_commands += '-- cycle'
        draw_commands += '; \n'
        
        return draw_commands

'''
Node_On_Path: Creates a node along a path between two points. Points can be
coordinates (as a list) or names of TikZ existing coordinates or Point_Obj-s

Methods:
    * draw_me: Generates the TikZ code to draw the object

Backward Dependencies:
    * Node_On_Path <-- Obj
'''
class Node_On_Path(Obj):
    # Initialization parameters:
    #   * first_point: Point_Obj, name, or coordinates of the first point
    #   * second_point: Point_Obj, name, or coordinates of the first point
    #   * contents: Contents of the node
    #   * options: These set the node options (such as anchor, color, etc.)
    def __init__(self,
                 ref = 'Node_On_Path',
                 frames = [1, 1],
                 location = [0, 0],
                 rotate = 0,
                 fade = 0,
                 scale = 1,
                 first_point = 'my_first_point',
                 second_point = 'my_second_point',
                 contents = '',
                 options = '',
                 at_point = False):

        Obj.__init__(self,
                     ref = ref,
                     frames = frames)

        self.rotate = rotate
        self.fade = fade
        self.scale = scale

        self.first_point = first_point
        self.second_point = second_point
        self.contents = contents
        draw_options = 'scale={},rotate={},opacity={}'.format(self.scale, self.rotate, 1-self.fade)
        self.options = draw_options + ',' + options

    def draw_me(self, frame):
        if type(self.first_point) == str:
            first_point = self.first_point
        elif type(self.first_point) == Point_Obj:
            first_point = self.first_point.ref
        else:
            first_point = '{},{}'.format(self.first_point[0], self.first_point[1])

        if type(self.second_point) == str:
            second_point = self.second_point
        elif type(self.second_point) == Point_Obj:
            second_point = self.second_point.ref
        else:
            second_point = '{},{}'.format(self.second_point[0], self.second_point[1])

        return '\\path ({}) -- ({}) '.format(first_point, second_point) + \
               'node[{}]{{{}}}; \n'.format(self.options,self.contents)

'''
Literal: This is for those things that I need to manually program in.

Methods:
    * draw_me: Generates the TikZ code to draw the object

Backward Dependencies:
    * Literal <-- Obj
'''

class Literal(Obj):
    def __init__(self,
                 ref = 'Literal',
                 frames = [1, 0],
                 contents = ''):
        
        Obj.__init__(self,
                     ref = ref,
                     frames = frames)

        self.contents = contents

    def draw_me(self, frame):
        return self.contents


'''
Anim_Obj: This is an animated object.

Methods:
    * update: Updates the features of the animated object.
    * obj_move: Move the object
    * obj_rot: Rotate the object
    * obj_fade: Change the transparency of the object (0 = solid, 1 = transparent)
    * obj_scale: Change the scale of the object
    * graph_domain: Change the domain of a graph

Backward Dependencies:
    * Anim_Obj <-- Obj

Forward Dependencies:
    * Anim_Obj --> Point_Obj
    *          --> Circle
    *          --> Graph

'''
class Anim_Obj(Obj):
    # Initialization parameters:
    #   * location = list containing the initial coordinates of the object
    #   * rotate = rotation angle
    #   * fade = transparency of the object
    #   * scale = scale of the object
    def __init__(self,
                 ref = 'Anim_Obj',
                 frames = [1, 0],
                 location = [0, 0],
                 rotate = 0,
                 fade = 0,
                 scale = 1,
                 domain = [0, 0]):
        
        Obj.__init__(self,
                     ref = ref,
                     frames = frames)
        # Anim_Obj.x and Anim_Obj.y: The x and y coordinates of the object
        self.x = location[0]
        self.y = location[1]

        # Anim_Obj.rotate, Anim_Obj.fade, Anim_Obj.scale: The rotation, the transparency
        # and the scale of the object
        self.rotate = rotate
        self.fade = fade
        self.scale = scale
        
        # Anim_Obj.domain_a and Anim_Obj.domain_b: The left and right endpoints of the domain.
        self.domain_a = domain[0]
        self.domain_b = domain[1]
        
        # Anim_Obj.keyframes: list that contains all of the object's movements
        self.keyframes = []

    # Method to update the features of the animated object
    # Parameters:
    #   * frame: the current frame number
    def update(self, frame):
        for animate in self.keyframes:
            # Sets the initial parameter values in the first frame of the animation
            if animate.start_frame == frame:
                if animate.ani_type == 'obj_x':
                    animate.start_value = self.x
                elif animate.ani_type == 'obj_y':
                    animate.start_value = self.y
                elif animate.ani_type == 'obj_rot':
                    animate.start_value = self.rotate
                elif animate.ani_type == 'obj_fade':
                    animate.start_value = self.fade
                elif animate.ani_type == 'obj_scale':
                    animate.start_value = self.scale
                elif animate.ani_type == 'obj_xrad':
                    animate.start_value = self.x_radius
                elif animate.ani_type == 'obj_yrad':
                    animate.start_value = self.y_radius
                elif animate.ani_type == 'domain_a':
                    animate.start_value = self.domain_a
                elif animate.ani_type == 'domain_b':
                    animate.start_value = self.domain_b

            # Determines whether the animation is active. If there are multiple active animations,
            # the LAST Animate object in the keyframe list will take precedence
            if animate.start_frame <= frame and animate.end_frame >= frame:
                print(animate.start_frame, animate.end_frame, animate.ani_type, animate.start_value, animate.end_value,
                      animate.linear_interpolate(frame))
                if animate.ani_type == 'obj_x':
                    self.x = animate.linear_interpolate(frame)
                elif animate.ani_type == 'obj_y':
                    self.y = animate.linear_interpolate(frame)
                elif animate.ani_type == 'obj_rot':
                    self.rotate = animate.linear_interpolate(frame)
                elif animate.ani_type == 'obj_fade':
                    self.fade = animate.linear_interpolate(frame)
                elif animate.ani_type == 'obj_scale':
                    self.scale = animate.linear_interpolate(frame)
                elif animate.ani_type == 'obj_xrad':
                    self.x_radius= animate.linear_interpolate(frame)
                elif animate.ani_type == 'obj_yrad':
                    self.y_radius= animate.linear_interpolate(frame)
                elif animate.ani_type == 'domain_a':
                    self.domain_a = animate.linear_interpolate(frame)
                elif animate.ani_type == 'domain_b':
                    self.domain_b = animate.linear_interpolate(frame)

    # Animation methods
    def obj_move(self, frames, end_location):
        self.keyframes.append(
            Animate(frames = frames,
                    ani_type = 'obj_x',
                    end_value = end_location[0]))
        self.keyframes.append(
            Animate(frames = frames,
                    ani_type = 'obj_y',
                    end_value = end_location[1]))

    def obj_rot(self, frames, end_rotate):
        self.keyframes.append(
            Animate(frames = frames,
                    ani_type = 'obj_rot',
                    end_value = end_rotate))

    def obj_fade(self, frames, end_fade):
        self.keyframes.append(
            Animate(frames = frames,
                    ani_type = 'obj_fade',
                    end_value = end_fade))

    def obj_scale(self, frames, end_scale):
        self.keyframes.append(
            Animate(frames = frames,
                    ani_type = 'obj_scale',
                    end_value = end_scale))

    def obj_radius(self, frames, end_radius):
        if type(end_radius) == int or type(end_radius) == float:
            end_radius = [end_radius, end_radius]
            
        self.keyframes.append(
            Animate(frames = frames,
                    ani_type = 'obj_xrad',
                    end_value = end_radius[0]))
        self.keyframes.append(
            Animate(frames = frames,
                    ani_type = 'obj_yrad',
                    end_value = end_radius[1]))

    def change_domain(self, frames, end_domain):
        self.keyframes.append(
            Animate(frames = frames,
                    ani_type = 'domain_a',
                    end_value = end_domain[0]))
        self.keyframes.append(
            Animate(frames = frames,
                    ani_type = 'domain_b',
                    end_value = end_domain[0]))

'''
Circle: Draws an animated circle or ellipse. 

Methods:
    * draw_me: Generates the TikZ code to draw the object

Backward Dependencies:
    * Circle <-- Anim_Obj

'''

class Circle(Anim_Obj):
    # Initialization parameters:
    #   * location: The center of the Circle
    #   * radius: As a single number, this is the radius of the circle.
    #             As a list [x_radius, y_radius], this creates an ellipse.
    def __init__(self,
                 ref = 'my_point_object',
                 frames = [1, 1],
                 location = [0, 0],
                 rotate = 0,
                 fade = 0,
                 scale = 1,
                 radius = 0,
                 options = '',
                 at_point = False):

        Anim_Obj.__init__(self,
                          ref = ref,
                          frames = frames,
                          location = location,
                          rotate = rotate,
                          fade = fade,
                          scale = scale)

        self.at_point = at_point

        if type(radius) == int or type(radius) == float:
            radius = [radius, radius]
        self.x_radius = radius[0]
        self.y_radius = radius[1]

        self.options = options

    def draw_me(self, frame):
        self.update(frame)
        draw_options = 'opacity={}'.format(1-self.fade)

        if self.at_point == False:
            return '\\draw[{}] ({},{}) circle [scale={}, rotate={}, x radius={}, y radius={}]; \n'.format(
                    draw_options + ',' + self.options, self.x, self.y, self.scale,
                    self.rotate, self.x_radius, self.y_radius)
        else:
            return '\\draw[{}] ({}) circle [scale={}, rotate={}, x radius={}, y radius={}]; \n'.format(
                    draw_options + ',' + self.options, self.ref, self.scale,
                    self.rotate, self.x_radius, self.y_radius)

'''
Graph: Produces an animated parametric graph. The default parameter is \t
and uses the TikZ plot command.

Graph <- Obj
'''

class Graph(Anim_Obj):
    def __init__(self,
                 ref = 'Graph',
                 frames = [1, 1],
                 domain = [0,0],
                 x = '',
                 y = '',
                 parameter = 't',
                 samples = 50,
                 options = ''):

        Obj.__init__(self,
                     ref = ref,
                     frames = frames)
        self.options = options
        self.samples = samples
        self.x = x
        self.y = y
        self.parameter = parameter
        
        self.left_endpoint = domain[0]
        self.right_endpoint = domain[1]

        self.keyframes = []
        
    def change_domain(self, frames, end_domain):
        self.keyframes.append(
            Animate(frames = frames,
                    ani_type = 'domain_a',
                    end_value = end_domain[0]))
        self.keyframes.append(
            Animate(frames = frames,
                    ani_type = 'domain_b',
                    end_value = end_domain[1]))

    def update(self, frame):
        for animate in self.keyframes:
            if animate.start_frame == frame:
                if animate.ani_type == 'domain_a':
                    animate.start_value = self.left_endpoint
                elif animate.ani_type == 'domain_b':
                    animate.start_value = self.right_endpoint

            if animate.start_frame <= frame and animate.end_frame >= frame:
                print(animate.start_frame, animate.end_frame, animate.ani_type, animate.start_value, animate.end_value,
                      animate.linear_interpolate(frame))
                if animate.ani_type == 'domain_a':
                    self.left_endpoint = animate.linear_interpolate(frame)
                elif animate.ani_type == 'domain_b':
                    self.right_endpoint = animate.linear_interpolate(frame)

    def draw_me(self, frame):
        self.update(frame)
        return '\\draw[smooth, samples={},variable=\\{},'.format(self.samples, self.parameter) + \
            'domain={}:{},{}] '.format(self.left_endpoint, self.right_endpoint, self.options) + \
            'plot ( {{{}}}, {{{}}} ); \n'.format(self.x, self.y)


'''
Point_Obj: This creates a TikZ coordinate at a particular point. It is the basis
for all point-like objects.

Methods:
    * draw_me: Generates the TikZ code to draw the object
    * coords (unused): Returns the x and y coordinates of the Point_Obj. This
    *                  is something I may use in the future.

Backward Dependencies:
    * Point_Obj <-- Anim_Obj

Forward Dependencies:
    * Point_Obj --> Node
    *           --> Scope
'''

class Point_Obj(Anim_Obj):
    # Initialization parameters:
    #   * at_point: if True, higher level objects will use a point
    #               as a reference instead of a coordinate
    def __init__(self,
                 ref = 'my_point_object',
                 frames = [1, 0],
                 location = [0, 0],
                 rotate = 0,
                 fade = 0,
                 scale = 1,
                 at_point = False):

        Anim_Obj.__init__(self,
                          ref = ref,
                          frames = frames,
                          location = location,
                          rotate = rotate,
                          fade = fade,
                          scale = scale)
        
        self.at_point = at_point

    def draw_me(self, frame):
        self.update(frame)
        return '\\coordinate ({}) at ({},{}); \n'.format(self.ref, self.x, self.y)
    
    def coords(self, frame):
        self.update(frame)
        return [self.x, self.y]

'''
Scope: A scope is a class that contains other types of Obj-s.

Methods:
    * draw_me: Generates the TikZ code to draw the object

Backward Dependencies:
    * Circle <-- Anim_Obj
'''

class Scope(Point_Obj):
    def __init__(self,
                 ref = 'Scope',
                 frames = [1, 1],
                 location = [0, 0],
                 rotate = 0,
                 fade = 0,
                 scale = 1,
                 at_point = False,
                 options = ''):
        
        Point_Obj.__init__(self,
                           ref = ref,
                           frames = frames,
                           location = location,
                           rotate = 0,
                           fade = 0,
                           scale = 1,
                           at_point = False)

        self.options = options
        
        self.contents = []

    def draw_me(self, frame):
        self.update(frame)
        options = self.options + ',shift={{({},{})}}'.format(self.x, self.y)
        if self.start_frame <= frame and (self.end_frame >= frame or self.end_frame == 0):
            draw_commands = '\\begin{{scope}}[{}] \n'.format(options)
            
            for obj in self.contents:
                if obj.start_frame <= frame and (obj.end_frame == 0 or obj.end_frame >= frame):
                    draw_commands += obj.draw_me(frame) + '\n'
            draw_commands += '\\end{scope} \n'
            return draw_commands
        else:
            return 


'''
Node: This creates a node at a point. The point can either be preexisting or
it will create a new point and put the node there.

Methods:
    * draw_me: Generates the TikZ code to draw the object (Note: This replaces
               the draw_me method from the Point_Obj class)

Backward Dependencies:
    * Node <-- Point_Obj

Forward Dependencies:
    * Node --> Text

'''
class Node(Point_Obj):
    # Initialization parameters:
    #   * ref: If this is a string, then it creates a coordinate with that name.
    #          Otherwise, this needs to be a Point_Obj.
    #   * contents: These are the contents of the node
    #   * options: These set the node options (such as anchor, color, etc.)
    def __init__(self,
                 ref = 'my_node',
                 frames = [1, 0],
                 location = [0, 0],
                 rotate = 0,
                 fade = 0,
                 scale = 1,
                 contents = '',
                 options = '',
                 at_point = False):

        Point_Obj.__init__(self,
                           ref = ref,
                           frames = frames,
                           location = location,
                           rotate = rotate,
                           fade = fade,
                           scale = scale,
                           at_point = at_point)
        self.contents = contents
        self.options = options
        
    def draw_me(self, frame):
        self.update(frame)
        draw_commands = ''
        
        # Creates a new coordinate if not using an existing one
        if self.at_point == False:
            draw_commands = '\\coordinate ({}) at ({},{}); \n'.format(self.ref, self.x, self.y)

        # If the reference type of a string, then use the string. Otherwise, get the name
        # of the reference object. I think there's a better way to do this. Maybe just don't use
        # Point_Objs as references?
        if type(self.ref) == str:
            ref = self.ref
        else:
            ref = self.ref.ref
        draw_options = 'scale={},rotate={},opacity={}'.format(self.scale, self.rotate, 1-self.fade)
        draw_commands += '\\draw ({}) node[{}] {{{}}}; \n'.format(ref, draw_options + ',' + self.options, self.contents)

        return draw_commands


'''
Text: Creates a text object. By default, the text is centered with a strut so
that all basic text is handled in the same way. Mathematical notation may spill
above or below the strut, in which case the alignment may vary. The default is
also to double the size of the text so that it is readable at 1920x1080
'''

class Text(Node):
    def __init__(self,
                 ref = 'my_node',
                 frames = [1, 1],
                 location = [0, 0],
                 rotate = 0,
                 fade = 0,
                 scale = 1,
                 contents = '',
                 options = '',
                 at_point = False):

        Node.__init__(self,
                      ref = ref,
                      frames = frames,
                      location = location,
                      rotate = rotate,
                      fade = fade,
                      scale = scale,
                      at_point = at_point,
                      contents = contents,
                      options = options)
        self.contents += '\\strut'
        self.options += ',anchor=center,scale=2'
        
