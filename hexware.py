import cadquery as cq
import math

ESPRESSO_OZ = [2.75, 3.5]
THICK_RATIO = 0.10
OZ_TO_ML = 29.5735


def espresso_cup(h):
    assert ESPRESSO_OZ[1] > ESPRESSO_OZ[0]
    target_oz = (ESPRESSO_OZ[1] - ESPRESSO_OZ[0])/2 + ESPRESSO_OZ[0]
    target_cu_mm = (target_oz * OZ_TO_ML)*1000
    target_dia = 2*math.sqrt((target_cu_mm/h)/math.pi)
    print("target_dia", target_dia)

    cutout = (
            cq.Workplane("XY").add(
                cq.Solid.makeCone(
                    target_dia/2 * (1-THICK_RATIO),
                    target_dia/2 * (1+THICK_RATIO),
                    h)
            ).faces("<Z").fillet(target_dia*THICK_RATIO)
    )

    bottom_seg_h = h * 2*THICK_RATIO
    outside_dia = target_dia * (1+2*THICK_RATIO)
    walls = (
        cq.Workplane("XY").polygon(6, outside_dia, circumscribed=True)
        .extrude(h)
    )
    body = (
        cq.Workplane("XY").polygon(6, outside_dia, circumscribed=True)
        .workplane(offset=-bottom_seg_h).polygon(6, outside_dia * (1-THICK_RATIO), circumscribed=True)
        .loft(combine=True)
        .union(walls)
    )

    roundover = (
        cq.Workplane("XY").circle(outside_dia/2 * (1+THICK_RATIO))
        .extrude(h+bottom_seg_h)
        .faces(">Z").fillet(2)
        .translate((0,0,-bottom_seg_h))
    )

    volume = body.intersect(cutout).val().Volume()/1000/OZ_TO_ML
    print("Final volume", volume, "oz")
    assert ESPRESSO_OZ[0] < volume < ESPRESSO_OZ[1]
    return body.cut(cutout).intersect(roundover)


VH = 40
result = espresso_cup(h=VH)
