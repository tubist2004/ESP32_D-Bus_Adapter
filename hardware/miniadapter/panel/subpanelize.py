from kikit import panelize_ui, panelize
from kikit import panelize_ui_impl as ki
from kikit.units import readLength, readAngle, readPercents
from pcbnewTransition.pcbnew import (
    FromMM,
    LoadBoard,
    ToMM,
    EDA_ANGLE,
    VECTOR2I,
    BOX2I,
    EDA_ANGLE,
)
import commentjson

path = "panel/all.json"


def subPanelize(path, parent=None, id=0):
    try:
        with open(path, "r", encoding="utf-8") as f:
            preset = commentjson.load(f)
        inPath = preset["layout"].get("input")
        outPath = preset["layout"].get("output")
        subpanels = preset["layout"].get("subpanels")
        hspace = preset["layout"].get("hspace")
        vspace = preset["layout"].get("vspace")
        if parent != None:
            outPath = parent.replace(".kicad_pcb", "_" + str(id) + ".kicad_pcb")
        if (inPath != None) & (outPath != None):
            preset = ki.obtainPreset([path])
            panelize_ui.doPanelization(inPath, outPath, preset)
        elif (subpanels != None) & (outPath != None):
            i = 0
            panel = panelize.Panel(
                outPath.replace(".kicad_pcb", "_joined" + ".kicad_pcb")
            )
            posx = FromMM(20)
            posy = FromMM(20)
            for sub in subpanels:
                subPanelize(sub, parent=outPath, id=i)
                subPath = outPath.replace(".kicad_pcb", "_" + str(i) + ".kicad_pcb")
                box = panel.appendBoard(
                    subPath,
                    VECTOR2I(posx, posy),
                    BOX2I(
                        VECTOR2I(FromMM(-1000), FromMM(-1000)),
                        VECTOR2I(FromMM(2000), FromMM(2000)),
                    ),
                    origin=panelize.Origin.TopLeft,
                    shrink=True,
                    tolerance=FromMM(10),
                    interpretAnnotations=False,
                )
                print(subPath)
                if hspace != None:
                    posx = box.GetRight() + readLength(hspace)
                if vspace != None:
                    posy = box.GetBottom() + readLength(vspace)
                i += 1
            try:
                panel.save()
            except RuntimeError as e:
                print("Didn't merge DRCs")
            preset = ki.obtainPreset([path])
            panelize_ui.doPanelization(
                outPath.replace(".kicad_pcb", "_joined" + ".kicad_pcb"), outPath, preset
            )

    except OSError as e:
        raise RuntimeError(f"Cannot open preset '{path}'")


subPanelize(path)
