import cadquery as cq
import math

ESPRESSO_OZ = [2.75, 3.5]
assert ESPRESSO_OZ[1] > ESPRESSO_OZ[0]
THICK_RATIO = 0.10
OZ_TO_ML = 29.5735
FINGER_HOLE_DIA = 25.4
VH = 40

def hex_body(h, tile_factor=1):
    target_oz = (ESPRESSO_OZ[1] - ESPRESSO_OZ[0])/2 + ESPRESSO_OZ[0]
    target_cu_mm = (target_oz * OZ_TO_ML)*1000
    target_dia = 2*math.sqrt((target_cu_mm/VH)/math.pi) * tile_factor
    cutout = (
            cq.Workplane("XY").add(
                cq.Solid.makeCone(
                    target_dia/2 * (1-THICK_RATIO),
                    target_dia/2 * (1+THICK_RATIO),
                    h)
            ).faces("<Z").fillet(target_dia*THICK_RATIO)
    )

    bottom_seg_h = VH * 2*THICK_RATIO
    outside_dia = target_dia * (1+2*THICK_RATIO)
    walls = (
        cq.Workplane("XY").polygon(6, outside_dia, circumscribed=True)
        .extrude(h)
    )
    bounds = (
        cq.Workplane("XY").polygon(6, outside_dia, circumscribed=True)
        .workplane(offset=-bottom_seg_h).circle(outside_dia/2 * (1-THICK_RATIO))
        .loft(combine=True)
        .union(walls)
        .cut(cq.Workplane("XY").workplane(offset=-bottom_seg_h).circle(outside_dia/3).extrude(bottom_seg_h/2))
    )

    roundover = (
        cq.Workplane("XY").circle(outside_dia/2 * (1+THICK_RATIO))
        .extrude(h+bottom_seg_h)
        .faces(">Z").fillet(2)
        .translate((0,0,-bottom_seg_h))
    )

    # Ensure the body is stackable
    body = bounds.cut(bounds.translate((0,0,h + 2/3*bottom_seg_h)))

    return body.cut(cutout).intersect(roundover), bounds, cutout, outside_dia

def espresso_cup():
    body, bounds, cutout, outside_dia = hex_body(h=VH, tile_factor=1)
    volume = bounds.intersect(cutout).val().Volume()/1000/OZ_TO_ML
    print("Final volume", volume, "oz")
    assert ESPRESSO_OZ[0] < volume < ESPRESSO_OZ[1]

    handle_thick = FINGER_HOLE_DIA * 3*THICK_RATIO
    handle = (
        cq.Workplane("XZ")
        .circle(FINGER_HOLE_DIA/2)
        .circle(FINGER_HOLE_DIA/2 + handle_thick)
        .extrude(handle_thick/2, both=True)
        .translate((outside_dia/2 + FINGER_HOLE_DIA/2, 0, VH/2))
        .edges().fillet(handle_thick/4)
        .cut(bounds)
    )

    return body.union(handle)

def ramekin():
    body, _, _, outside_dia = hex_body(h=VH/2, tile_factor=1)
    return body.translate((-outside_dia,0,0))

def low_bowl():
    body, _, _, outside_dia = hex_body(h=VH/2, tile_factor=2)
    return body.translate((-outside_dia, 0, 0))

def body_mod(h, tile_factor, translate):
    body, _, _, outside_dia = hex_body(VH/3, tile_factor)
    return body.translate([outside_dia*dim for dim in translate])

ecup = espresso_cup()
ecup_saucer = body_mod(VH/3, 2, (0,0,0)).translate((0,0,-7)).cut(ecup)
mug = "TODO 2x tile factor, double height"
cappucino_cup = "TODO 2x tile factor, espresso height"
cappucino_saucer = "TODO 3x tile factor, holds cappucino cup"
bowl = "3x tile factor, cappucino height"
ramen_bowl = "4x tile factor, 2x height"
serving_tray = "TODO hex grid CNC bamboo platter that holds stuff"
placemat = "TODO CNC hex mat with location of various objects"
small_plate = body_mod(VH/3, 3, (1,1.3,0))
dinner_plate = body_mod(VH/3, 5, (1,0,0))
sauce_dish = "TODO ramekin but lower and wider"
ramekin = body_mod(VH/2, 1, (2,0,0))
sushi_dipping_tray = "TODO two ramekins fused together"
base_tile = "TODO solid hexagonal tiles just for messin"
cupholder = "triplet of 1x tile factor base tiles, combined"
table = "TODO hexagonal table with cutouts for the placemats, and covers for them that can be magnetically removed"
