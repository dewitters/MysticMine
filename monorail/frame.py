#!/usr/bin/env python

from world import *
from player import *
from pickups import *
from tiles import *
from control import *
from event import *

from worldview import *
from playerview import *
from pickupsview import *
from tilesview import *
from controlview import *
from eventview import *

class Frame:
    """Contains one picture frame of the game.

    Use this class to first build up the frame, and later display it."""

    def __init__( self, surface, time_sec, interpol ):
        self.surface = surface
        self.time_sec = time_sec
        self.interpol = interpol
        self.optimize_speed = True

        self.X_OFFSET = 0
        self.Y_OFFSET = 0

    def get_views( self, model ):
        if hasattr( model, 'views' ) and model.views is not None:
            return model.views
        else:            
            if isinstance( model, Level):
                views = [LevelView( model )]
            elif isinstance( model, Playfield ):
                views = [PlayfieldView( model )]
            elif isinstance( model, GoldCar ):                
                views = [GoldCarView( model )]
                
            elif isinstance( model, Torch ):
                views = [TorchView( model )]
            elif isinstance( model, Diamond ):
                views = [DiamondView( model )]
            elif isinstance( model, Key ):
                views = [KeyView( model )]
            elif isinstance( model, Mirror ):
                views = [MirrorView( model )]
            elif isinstance( model, Oiler ):
                views = [OilerView( model )]
            elif isinstance( model, Multiplier ):
                views = [MultiplierView( model )]
            elif isinstance( model, Balloon ):
                views = [BalloonView( model )]
            elif isinstance( model, Ghost ):
                views = [GhostView( model )]
            elif isinstance( model, CopperCoin ):
                views = [CopperCoinView( model )]
            elif isinstance( model, GoldBlock ):
                views = [GoldBlockView( model )]
            elif isinstance( model, RockBlock ):
                views = [RockBlockView( model )]
            elif isinstance( model, Dynamite ):
                views = [DynamiteView( model )]
            elif isinstance( model, Lamp ):
                views = [LampView( model )]
            elif isinstance( model, Axe ):
                views = [AxeView( model )]
            elif isinstance( model, Flag ):
                views = [FlagView( model )]
            elif isinstance( model, Leprechaun):
                views = [LeprechaunView( model )]
                
            elif isinstance( model, Enterance ):
                views = [EnteranceView( model ), EnteranceTopView( model )]              
            elif isinstance( model, RailGate ):
                views = [RailGateView( model )]
            elif isinstance( model, Tile ):
                views = [TileView( model )]           
            elif isinstance( model, GroundControl ):
                views = [GroundControlView( model )]
            elif isinstance( model, Event ):
                views = [EventView( model )]
            else:
                return None

            model.views = views

            return views


    def draw( self, model ):
        if model is None: return
        
        for view in self.get_views( model ):
            view.draw( self )

    def draw_z( self, models ):        
        views = []
        for model in models:
            for view in self.get_views( model ):
                views.append( view )
                
                if hasattr(view, "submodels"):
                    for submodel in view.submodels:
                        for subview in self.get_views( submodel ):
                            views.append( subview )

        views.sort( key = lambda v: v.z )
                    
        for view in views:
            view.draw( self )
            
