"""
/***************************************************************************
Name                 : Sample Areas Grid for Quality Review
Description          : Generates a grid of sample areas for quality review ( QGIS 2.14 or above )
Date                 : March, 2019.
copyright            : (C) 2019 by Alex Santos and Viviane Diniz
email                : alex.santos@ibge.gov.br / viviane.diniz@ibge.gov.br

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 
 Grid generation code adapted from https://gis.stackexchange.com/questions/79916/how-to-generate-a-grid-programmatically-in-python-without-gui
 
"""
##Controle de Qualidade=group
##2 - Inspecao por area = name
##Camada=vector
##Tamanho_da_celula_da_grade=number 0.0
##Nivel_de_Inspecao=selection I;II;III
##Areas_de_Inspecao=output vector

from PyQt4 import QtCore
from PyQt4.QtGui import QMessageBox
from qgis import core as QgsCore
from processing.tools.vector import VectorWriter
from qgis.utils import iface
from math import ceil
import random
from qgis.gui import QgsMessageBar
from processing.tools import dataobjects, vector
from qgis.gui import QgsMessageBar

lyrInput = processing.getObject( Camada )
Output = Areas_de_Inspecao

# Plano de amostragem
dicSampleLength={2:[2,2,3],9:[2,3,5],16:[3,5,8],26:[5,8,13],51:[5,13,20],91:[8,20,32],151:[13,32,50],281:[20,50,80],501:[32,80,125],1201:[50,125,200],3201:[80,200,315],10001:[125,315,500],35001:[200,500,800],150001:[315,800,1250],500001:[500,1250,2000]}

xmin,ymin,xmax,ymax = lyrInput.extent().toRectF().getCoords()
gridWidth = Tamanho_da_celula_da_grade
gridHeight = Tamanho_da_celula_da_grade
rows = ceil((ymax-ymin)/gridHeight)
cols = ceil((xmax-xmin)/gridWidth)
ringXleftOrigin = xmin
ringXrightOrigin = xmin + gridWidth
ringYtopOrigin = ymax
ringYbottomOrigin = ymax-gridHeight
fields = [ QgsCore.QgsField("id", QtCore.QVariant.Int ) ]

lyrOutput = VectorWriter( Areas_de_Inspecao, None, fields, QgsCore.QGis.WKBPolygon, lyrInput.crs() )
lyrIntermediate=QgsCore.QgsVectorLayer("Polygon","temporary_polygons","memory")
lyrIntermediate.setCrs(lyrInput.crs())

id=1
progress.setInfo("Gerando grade de cobertura da camada...")
progress.setInfo("Numero de linhas: " + str(rows))
progress.setInfo("Numero de colunas: " + str(cols))

for i in range(int(cols)):
    ringYtop = ringYtopOrigin
    ringYbottom =ringYbottomOrigin
    for j in range(int(rows)):
        points = [QgsCore.QgsPoint(ringXleftOrigin, ringYtop),QgsCore.QgsPoint(ringXrightOrigin, ringYtop),QgsCore.QgsPoint(ringXrightOrigin, ringYbottom),QgsCore.QgsPoint(ringXleftOrigin, ringYbottom),QgsCore.QgsPoint(ringXleftOrigin, ringYtop)] 
        request = QgsCore.QgsFeatureRequest(QgsCore.QgsRectangle(ringXleftOrigin,ringYtop,ringXrightOrigin,ringYbottom))
        for feature in  lyrInput.getFeatures(request):
            square = QgsCore.QgsFeature()
            square.setGeometry(QgsCore.QgsGeometry.fromPolygon([points]))
            square.setAttributes([id])
            perc = id / (cols * rows * 100)
            progress.setPercentage(perc)
            lyrIntermediate.dataProvider().addFeatures([square])
            lyrIntermediate.updateExtents()
            id = id + 1
            break
        ringYtop = ringYtop - gridHeight
        ringYbottom = ringYbottom - gridHeight
    ringXleftOrigin = ringXleftOrigin + gridWidth
    ringXrightOrigin = ringXrightOrigin + gridWidth
    
progress.setInfo( 'Total de elementos da grade: ' + str(lyrIntermediate.featureCount()))

# Tamanho da amostra 
layer = lyrIntermediate
features = vector.features(layer)
featureCount = len(features)

for i in sorted(dicSampleLength.keys(),reverse=True):
    if featureCount >= i:
        index1 = i
        break

randomNum=random.sample(range(featureCount),1)[0]
sample_size=dicSampleLength[index1][Nivel_de_Inspecao]
step= lyrIntermediate.featureCount() // dicSampleLength[index1][Nivel_de_Inspecao]
module = randomNum % step
progress.setInfo("Numero aleatorio: " + str(randomNum))
progress.setInfo( 'Amostra: ' + str(dicSampleLength[index1][Nivel_de_Inspecao]))
progress.setInfo( 'Passo: ' + str(step))
progress.setInfo( 'Sorteado: ' + str(randomNum))

# Selecionando celulas da amostra
progress.setInfo('Selecionando celulas da amostra...')
listIds=range(featureCount) 
isSelectedId = []
x = 1
for i in listIds:
    if x <= sample_size: 
        if (i) % step == module:
            isSelectedId.append(i)
            x += 1    
          

for i, feat in enumerate(features):
    if i in isSelectedId:
        lyrOutput.addFeature(feat)

del lyrOutput

progress.setInfo('Numero de amostras selecionadas:  ' + str(len(isSelectedId)))
progress.setInfo('Alex Santos and Viviane Diniz')

QMessageBox.about(None, "Amostragem aleatoria sistematica", "Unidades de amostragem criadas")
        