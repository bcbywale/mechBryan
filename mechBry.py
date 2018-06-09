#!usr/bin/python3

import sys
import ezdxf
import cloudconvert


#Information required, vessel, penetration, water depth, deck height, crane radius or angle, hook height
#TODO ask user for input
#TODO Work in feet or mm

vessel = sys.argv[1]
vesselFile = vessel +".dxf"
penetration = float(sys.argv[2])*12
waterDepth = float(sys.argv[3])*12
deckHeight = float(sys.argv[4])*12
craneRadius = float(sys.argv[5])*12
craneAngle = float(sys.argv[6])*12
hookHeight = float(sys.argv[7])*12

#Program defined variables
enviromentWidth = 500*12
scale = .001302*12
textHeight = 5.0*12
textOffset = 0.25*12
dxfversion = "AC1015"

#enter Model Space
drawing = ezdxf.readfile(vesselFile, encoding='auto', legacy_mode=False)
modelspace = drawing.modelspace()

#Add required layers
drawing.layers.new('ENVIROMENT', dxfattribs={'color': 7})
drawing.layers.new('TEXT', dxfattribs={'color': 7})
drawing.layers.new('VESSEL', dxfattribs={'color': 7})

#Draw Mean Low Water at Origin
modelspace.add_text('MLW', dxfattribs={'layer': 'TEXT','height': textHeight}).set_pos((0, 0), align='RIGHT')
modelspace.add_line((0, 0), (enviromentWidth, 0), dxfattribs={'layer':'ENVIROMENT'})

modelspace.add_text('Penetration', dxfattribs={'layer': 'TEXT','height': textHeight}).set_pos((0, -(penetration+waterDepth)), align='RIGHT')
modelspace.add_line((0, -(penetration+waterDepth)), (enviromentWidth, -(penetration+waterDepth)), dxfattribs={'layer':'ENVIROMENT'})

modelspace.add_text('Mudline', dxfattribs={'layer': 'TEXT','height': textHeight}).set_pos((0, -waterDepth), align='RIGHT')
modelspace.add_line((0, -waterDepth), (enviromentWidth, -waterDepth), dxfattribs={'layer':'ENVIROMENT'})

point = [enviromentWidth-(200*12),deckHeight,0]
modelspace.add_blockref('LB_JILL_HULL', point, dxfattribs={
        'xscale': 1,
        'yscale': 1,
        'rotation': 0
    })

point = [(enviromentWidth-(200*12)-(3.5*12)),(deckHeight+(178.75)),0]

modelspace.add_blockref('LB_JILL_7000L-140_Boom', point, dxfattribs={
        'xscale': 1,
        'yscale': 1,
        'rotation': -craneAngle
})

point = [(enviromentWidth-((200+176)*12)),-(penetration+waterDepth),0]
modelspace.add_blockref('LB_JILL_LEGS', point, dxfattribs={
        'xscale': 1,
        'yscale': 1,
        'rotation': 0
})

layout = drawing.layout('Layout1')  # default layout name
height = 17
width = 11
layout.page_setup(size=(height, width), margins=(.5, .5, 0.5, .5), units='inch')
layout.add_viewport(center=(height/2-.5, width/2-.5), size=(height-1, width-1), view_center_point=(225*12, 0), view_height=5000)

drawing.saveas('out.dxf')

#Do drawing conversion
convert = 1
if (convert == 0):

    api = cloudconvert.Api('YzFRe3SooBOizrVpL0Oh6rmhtvp0foneAjsmLNgllQgqknWTdNoA0yJ4GYQ11zTC')
    process = api.createProcess({
        "inputformat": "dxf",
        "outputformat": "pdf"
    })

    process.start({
        "input": "upload",
        "file": open('out.dxf', 'rb'),
        "outputformat": "pdf",
        "converteroptions": {
        "all_layouts": True,
        "resize": "1224 x 792",
        "auto_zoom": False
        }
    })

    process.refresh() # fetch status from API
    process.wait() # wait until conversion completed
    print(process['message']) #  access process data
    process.download('test.pdf')

    from PyPDF2 import PdfFileWriter, PdfFileReader
    pages_to_keep = [2] #use regular page numbers, program will subtract below

    for i in range(len(pages_to_keep)):
        pages_to_keep[i] = pages_to_keep[i] - 1 #page numbering starts at zero

    infile = PdfFileReader('out.pdf', 'rb')
    output = PdfFileWriter()

    for i in range(infile.getNumPages()):
        if i in pages_to_keep:
            p = infile.getPage(i)
            output.addPage(p)

    with open('final.pdf', 'wb') as f:
        output.write(f)

print("MechBry complete!")
