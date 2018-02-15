#!/usr/bin/env python
#
# ChampApertureFieldEdxFile.py
#
# P. Grimes, Feb 2018
#
# Class to read, write and manipulate .edx files output by TICRA CHAMP, tailored to ApertureFields
#
# Since the XML schema for this format is not available (www.edi-forum.org is dead), we
# have to handcode the XPaths

from lxml import etree
import numpy as np
import NumpyUtility as nu
from io import StringIO

from matplotlib import pyplot as pp

class ChampApertureFieldEdxFile:
    '''Class to parse and hold data from a CHAMP .edx output file.'''
    def __init__(self, fileLike=None):
        '''Create a ChampEdxFile object, reading and parsing from <file>.
        
        if file not give, create empty object to be filled with .read, etc.'''
        # Flag to prevent errors from calling methods on objects with no data
        self.__ready = False
        
        if fileLike !=None:
            self.read(fileLike)
            
    def read(self, f):
        '''Read and parse a .edx file
        
        f can be either a file name or a file object'''
        if isinstance(f, file):
            fileLike = f
        else:
            fileLike = open(f)
            
        # Start by parsing xml
        ## Prevent errors due to large text nodes.  There is some security risk to this,
        ## but it is unavoidable in this application
        p = etree.XMLParser(huge_tree=True)
        self._tree = etree.parse(fileLike, p)
        self._root = self._tree.getroot()
        
        # Now start filling attributes read from file
        
        ## Read the shape of the radiation pattern data
        apertureFieldShapeText = self._root.find('{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="PlaneCut_E_RadiationPattern"]/{http://www.edi-forum.org}Sizes').text
        apertureFieldShape = []
        
        ### Read and manipulate shape to allow for complex numbers
        for i in apertureFieldShapeText.strip().split():
            apertureFieldShape.append(int(i))
        apertureFieldShape.append(2)
        
        self._shape = apertureFieldShape
        
        ## Read the field component number and type 
        self.nComponents = int(self._root.find('{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="PlaneCut_E_ProjectionComponents"]/{http://www.edi-forum.org}Sizes').text)
        self.componentType = self._root.find('{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="PlaneCut_E_ProjectionComponents"]').attrib["Class"].split(':')[1]
        
        ## Read the phi cut values
        self.nPhi = int(self._root.find('{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="PlaneCut_Phi"]/{http://www.edi-forum.org}Sizes').text)
        phiElement = self._root.find('{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="PlaneCut_Phi"]/{http://www.edi-forum.org}Component/{http://www.edi-forum.org}Value')
        phiText = StringIO(unicode(phiElement.text))
        self.phi = np.loadtxt(phiText)
        
        ## Read the z values
        zElement = self._root.find('{http://www.edi-forum.org}Data/{http://www.edi-forum.org}Variable[@Name="PlaneCut_Z"]/{http://www.edi-forum.org}Component/')
        zText = StringIO(unicode(rhoElement.text))
        self.z = np.loadtxt(zText)
        
        ## Read the rho values
        rhoElement = self._root.find('{http://www.edi-forum.org}Data/{http://www.edi-forum.org}Variable[@Name="PlaneCut_Rho"]/{http://www.edi-forum.org}Component/')
        rhoText = StringIO(unicode(rhoElement.text))
        self.rho = np.loadtxt(rhoText)

        ## Read the frequency vector
        freqElement = self._root.find('{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="PlaneCut_Frequency"]/{http://www.edi-forum.org}Component/')
        freqText = StringIO(unicode(freqElement.text))
        self.frequency = np.loadtxt(freqText)
        
        # Now read the actual data
        apertureFieldElement = self._root.find('{http://www.edi-forum.org}Data/{http://www.edi-forum.org}Variable[@Name="PlaneCut_E_RadiationPattern"]/{http://www.edi-forum.org}Component/')
        apertureFieldText = StringIO(unicode(apertureFieldElement.text))
        rP = np.loadtxt(apertureFieldText)
        apertureFields = rP.reshape(apertureFieldShape)
        self._apertureField = apertureFields[:,:,:,:,0] + 1j*apertureFields[:,:,:,:,1]
        
        # Should now have all data from file
        
    def getPatternByFreq(self, freq):
        '''Return the radiation pattern at one frequency in frequency vector'''
        # Get the index of the nearest frequency in the frequency vector
        freqIdx = nu.findNearestIdx(self.frequency, freq)
        
        return self._apertureField[:,:,:,freqIdx]
        
    def getPattern(self, component, phi, z, freq):
        '''Return an individual radiation pattern for one component, cut angle and frequency'''
        freqIdx = nu.findNearestIdx(self.frequency, freq)
        phiIdx = nu.findNearestIdx(self.phi, phi)
        zIdx = nu.findNearestIdx(self.z, z)
        
        return self._apertureField[component, :, zIdx, phiIdx, freqIdx]
        
    def plotPatterndB(self, component, phi, z, freq, label=None):
        '''Convenience function to plot an individual radiation pattern for one component, cut angle and frequency'''
        apertureField = self.getPattern(component, phi, z, freq)
        
        phi = nu.findNearest(self.phi, phi)
        freq = nu.findNearest(self.frequency, freq)
        z = nu.findNearest(self.z, z)
        
        if label==None:
            label = r"Component {:d}, $\phi={:g}^\circ$, z={:g}mm, {:g} GHz".format(component, phi, z*1e3, freq/1.0e9) 
        pp.plot(self.rho, 20*np.log10(np.abs(apertureField)), label=label)
        
    def plotPatternPhase(self, component, phi, z, freq, label=None):
        '''Convenience function to plot an individual radiation pattern for one component, cut angle and frequency'''
        apertureField = self.getPattern(component, phi, z, freq)
        
        phi = nu.findNearest(self.phi, phi)
        freq = nu.findNearest(self.frequency, freq)
        z = nu.findNearest(self.z, z)
        
        if label==None:
            label = r"Component {:d}, $\phi={:g}^\circ$, z={:g}mm, {:g} GHz".format(component, phi, z*1e3, freq/1.0e9) 
        pp.plot(self.rho, np.rad2deg(np.angle(apertureField)-np.angle(apertureField[0])), label=label)
        