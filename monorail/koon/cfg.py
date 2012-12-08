
class ConfigFile:
    """Handles koonsolo config files

    Public Members:
    - root_node: the root ConfigNode of this file

    example of such a file:

    en = Language {
      new game = New Game!
      quit = Quit Game
    }

    game = Subsection {

      hero = Player {
        place_x = 13.3
        place_y = 14.2
      }

      car1sprite = Sprite {
        surface = image.png
        center_x = 30
        center_y = 35
      }
    }
    """

    def __init__( self, filename = None ):
        if filename is not None:
            self.load( filename )

    def load( self, filename ):
        f = open( filename, "r" )
        self.root_node = ConfigNode.from_file( f )
        f.close()

    def save( self, filename ):
        f = open( filename, "w" )
        values = self.root_node.attribs.values()
        values.sort(key=lambda a:a.name)
        for attrib in values:
            attrib.to_file( f )
        f.close()

class ParseException( Exception ):
    pass

class ConfigNode:
    """One node with name/value information and optional subnodes

    Public Members:
    - name: string
    - value: string
    - attribs: dictionary of subnodes
    """
    def __init__( self, name = "", value = "", attribs = None):
        # attribs as default {} generates strange error ????
        self.name = name
        self.value = value
        if attribs is not None:
            self.attribs = attribs
        else:
            self.attribs = {}

    @staticmethod
    def from_file( configfile ):
        """ Returns the root node
        """
        root = ConfigNode( "root", "root" )
        nodes = []
        nodes.append( root )

        for line in configfile.readlines():
            line = ConfigNode._strip_comments( line )

            assign = line.find("=")
            if assign >= 0:
                if line.strip()[-1] == '{':
                    node = ConfigNode( line[0:assign].strip(), line[assign+1:-2].strip() )
                    nodes[-1].attribs[node.name] = node
                    nodes.append( node )
                else:
                    node = ConfigNode( line[0:assign].strip(), line[assign+1:].strip() )
                    nodes[-1].attribs[node.name] = node
            elif line.strip() == '}':
                if len( nodes ) > 1:
                    nodes.pop()
                else:
                    raise ParseException("too many }'s")

        if len( nodes ) <> 1:
            raise ParseException("too few {'s")

        return root

    @staticmethod
    def _strip_comments( line ):
        comment_pos = line.find("#")
        if comment_pos >= 0:
            line = line[0:comment_pos]
        return line

    def to_file( self, configfile, indent = 0 ):
        """writes to configfile"""
        configfile.write( "\t" * indent)
        configfile.write( "%s = %s" % (str(self.name), str(self.value) ) )
        if len(self.attribs) > 0:
            configfile.write(" {\n");
            values = self.attribs.values()
            values.sort(key=lambda a:a.name)
            for attrib in values:
                attrib.to_file( configfile, indent+1 )

            configfile.write( "\t" * indent)
            configfile.write("}")
        configfile.write("\n")

    def append_attribute( self, node ):
        if node is None: return

        if self.attribs.has_key( node.name ):
            if node.value is not None and node.value != "":
                self.attribs[ node.name ].value = node.value
            for n in node.attribs.values():
                self.attribs[ node.name ].append_attribute( n )
        else:
            self.attribs[ node.name ] = node

    def get( self, name ):
        """Return ConfigNode "sub1.sub2.name"
        """
        names = name.split(".")

        node = self
        for name in names:
            node = node.attribs[ name ]

        return node

    def set( self, name, value ):
        """Set value of "sub1.sub2.name"
        """
        names = name.split(".")

        node = self
        for name in names:
            try:
                node = node.attribs[ name ]
            except KeyError:
                node.append_attribute( ConfigNode( name, "" ) )
                node = node.attribs[ name ]

        node.value = str( value )

