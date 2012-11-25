#!/usr/bin/env python

import monorail.koon.cfg as cfg

class TestConfigNode:

    def test_get( self ):
        root = cfg.ConfigNode("root", "root")
        sub1 = cfg.ConfigNode("sub1", "val1")
        sub2a = cfg.ConfigNode("sub2a", "val2a")
        sub2b = cfg.ConfigNode("sub2b", "val2b")
        sub3 = cfg.ConfigNode("sub3", "val3")

        root.attribs["sub1"] = sub1
        sub1.attribs["sub2a"] = sub2a
        sub1.attribs["sub2b"] = sub2b
        sub2b.attribs["sub3"] = sub3
        
        assert root.get("sub1").value == "val1"
        assert root.get("sub1.sub2a").value == "val2a"
        assert root.get("sub1.sub2b").value == "val2b"
        assert root.get("sub1.sub2b.sub3").value == "val3"

        try:
            root.get("sub1.sub2a.sub3")
            assert False
        except:
            assert True

    def test_set( self ):        
        root = cfg.ConfigNode("root", "root")
        sub1 = cfg.ConfigNode("sub1", "val1")
        sub2a = cfg.ConfigNode("sub2a", "val2a")
        sub2b = cfg.ConfigNode("sub2b", "val2b")
        sub3 = cfg.ConfigNode("sub3", "val3")

        root.attribs["sub1"] = sub1
        sub1.attribs["sub2a"] = sub2a
        sub1.attribs["sub2b"] = sub2b
        sub2b.attribs["sub3"] = sub3

        root.set("sub1.sub2a", "val2Set")
        assert root.get("sub1.sub2a").value == "val2Set"
        
        root.set("sub1.subNew", 18)
        assert int( root.get("sub1.subNew").value ) == 18
        

    def test_parse_single( self ):
        cf = open( "cfg.tmp", "w" )
        cf.write("""
            timeout = 30
            
            x = 25.5
            y = 7""")
        cf.close()

        cf = open( "cfg.tmp", "r" )
        root = cfg.ConfigNode.from_file( cf )
        cf.close()

        assert root.get("timeout").value == "30"
        assert root.get("x").value == "25.5"
        assert root.get("y").value == "7"
        assert len( root.attribs ) == 3

    def test_parse_subs( self ):
        cf = open( "cfg.tmp", "w" )
        cf.write("""
            hero = Sprite {
                x = 50
                y = 60
                image = Surface {
                    width = 100
                    height = 70
                }
            }

            lang = en""")
        cf.close()

        cf = open( "cfg.tmp", "r" )
        root = cfg.ConfigNode.from_file( cf )
        cf.close()

        assert root.get("lang").value == "en"
        assert root.get("hero").value == "Sprite"
        assert root.get("hero.x").value == "50"
        assert root.get("hero.image.height").value == "70"

    def test_brace_errors( self ):
        cf = open( "cfg.tmp", "w" )
        cf.write("""
            hero = Sprite {
            }
            }
            """)
        cf.close()

        cf = open( "cfg.tmp", "r" )
        try:
            root = cfg.ConfigNode.from_file( cf )
            assert False
        except cfg.ParseException:
            assert True
        cf.close()

        cf = open( "cfg.tmp", "w" )
        cf.write("""
            hero = Sprite {
            """)
        cf.close()

        cf = open( "cfg.tmp", "r" )
        try:
            root = cfg.ConfigNode.from_file( cf )
            assert False
        except cfg.ParseException:
            assert True
        cf.close()

    def test_negative( self ):
        cf = open( "cfg.tmp", "w" )
        cf.write("""
            x = -16
            y = 7""")
        cf.close()

        cf = open( "cfg.tmp", "r" )
        root = cfg.ConfigNode.from_file( cf )
        cf.close()

        assert int(root.get("x").value) == -16

    def test_comments( self ):
        cf = open( "cfg.tmp", "w" )
        cf.write("""
            # A line comment
            timeout = 30 # a trailing comment
            
            x = 25.5
            y = 7""")
        cf.close()

        cf = open( "cfg.tmp", "r" )
        root = cfg.ConfigNode.from_file( cf )
        cf.close()

        assert root.get("timeout").value == "30"
        assert len( root.attribs ) == 3

class TestConfigFile:

    def test_load( self ):
        cf = open( "cfg.tmp", "w" )
        cf.write("""
            hero = Sprite {
                x = 50
                y = 60
                image = Surface {
                    width = 100
                    height = 70
                }
            }

            lang = en""")
        cf.close()

        conf = cfg.ConfigFile("cfg.tmp")
        assert conf.root_node.get("hero.y").value == "60"
        
    def test_save( self ):
        root = cfg.ConfigNode("root", "root")
        sub1 = cfg.ConfigNode("sub1", "val1")
        sub2a = cfg.ConfigNode("sub2a", "val2a")
        sub2b = cfg.ConfigNode("sub2b", "val2b")
        sub3 = cfg.ConfigNode("sub3", "val3")

        root.attribs["sub1"] = sub1
        sub1.attribs["sub2a"] = sub2a
        sub1.attribs["sub2b"] = sub2b
        sub2b.attribs["sub3"] = sub3

        conf = cfg.ConfigFile()
        conf.root_node = root
        conf.save("cfg.tmp")

        conf.load("cfg.tmp")
        
        assert conf.root_node.get("sub1").value == "val1"
        assert conf.root_node.get("sub1.sub2a").value == "val2a"
        assert conf.root_node.get("sub1.sub2b").value == "val2b"
        assert conf.root_node.get("sub1.sub2b.sub3").value == "val3"

        try:
            conf.root_node.get("sub1.sub2a.sub3")
            assert False
        except:
            assert True

    def test_preserve_layout( self ):
        pass

