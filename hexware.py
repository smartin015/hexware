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

def espresso_cup(h):
    body, bounds, cutout, outside_dia = hex_body(h, tile_factor=1)
    volume = bounds.intersect(cutout).val().Volume()/1000/OZ_TO_ML
    print("Final volume", volume, "oz")
    assert ESPRESSO_OZ[0] < volume < ESPRESSO_OZ[1]

    handle_thick = FINGER_HOLE_DIA * 2*THICK_RATIO
    handle = (
        cq.Workplane("XZ")
        .circle(FINGER_HOLE_DIA/2)
        .circle(FINGER_HOLE_DIA/2 + handle_thick)
        .extrude(handle_thick/2, both=True)
        .translate((outside_dia/2 + FINGER_HOLE_DIA/2, 0, h/2))
        .edges().fillet(handle_thick/4)
        .cut(bounds)
    )

    return body.union(handle)

def ramekin(h):
    body, _, _, outside_dia = hex_body(h, tile_factor=1)
    return body.translate((-outside_dia,0,0))

ecup = espresso_cup(h=VH)
rammy = ramekin(h=VH/2)
