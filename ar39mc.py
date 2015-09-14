import os, sys
from ROOT import *
from array import array
import numpy as np

# visibility tool
from pyubphotonlib.photonvisibility import PhotonVisibility

pvs = PhotonVisibility( "photonlib.json" )
LY = 40000.0 # photons/MeV
CE = 0.40
QE = 0.20*0.8
RATE = 1.0 # decay/kg/sec
FASTFRAC = 0.5
FASTCONST = 0.006 # usec
SLOWCONST = 1.600 # usec
LARDENSITY = 1.39 # g/cm^3
TPB = 1.1
XBOUNDS = [-50,300] # cm
YBOUNDS = [-180,180] # cm
ZBOUNDS = [-80,1110] # cm

def genDecayPosition():
    pos = np.asarray( [ XBOUNDS[0] + np.random.random()*(XBOUNDS[1]-XBOUNDS[0]),
                        YBOUNDS[0] + np.random.random()*(YBOUNDS[1]-YBOUNDS[0]),
                        ZBOUNDS[0] + np.random.random()*(ZBOUNDS[1]-ZBOUNDS[0]) ] )
    return pos

def genEnergyGaus( mean=0.200, sig =None):
    if sig is None:
        return mean

def ar39mc( photonlibrary, nevents ):
    
    eventtree = TTree( "eventtree", "Ar 39 MC event info" )
    petree    = TTree( "petree", "Ar 39 PE tree" )
    
    eventid = array('i',[0])
    energy  = array('f',[0])
    nphotons = array('f',[0])
    npe = array('f',[0])
    nhits = array('i',[0])
    dt = array('f',[0])
    tevent = array('f',[0])
    posv = array( 'f', [0]*3 )
    
    pmt  = array( 'i', [0] )
    thit = array( 'f', [0] )
    dthit = array( 'f', [0] )
    fastcomp = array( 'i', [0] )

    eventtree.Branch( "event", eventid, "event/I" )
    eventtree.Branch( "energy", energy, "energy/F" )
    eventtree.Branch( "nphotons", nphotons, "nphotons/F" )
    eventtree.Branch( "npe", npe, "npe/F" )
    eventtree.Branch( "nhits", nhits, "nhits/I" )
    eventtree.Branch( "tevent", tevent, "tevent/F" )
    eventtree.Branch( "dt", dt, "dt/F" )
    eventtree.Branch( "posv", posv, "posv[3]/F" )

    petree.Branch( "pmt", pmt, "pmt/I" )
    petree.Branch( "thit", thit, "thit/F" )
    petree.Branch( "dthit", dthit, "dthit/F" )
    petree.Branch( "fastcomp", fastcomp, "fastcomp/I")
    petree.Branch( "posv", posv, "posv[3]/F" )
    
    # Determine mass
    mass = LARDENSITY*(XBOUNDS[1]-XBOUNDS[0])*(YBOUNDS[1]-YBOUNDS[0])*(ZBOUNDS[1]-ZBOUNDS[0])*0.001 # kg
    detector_rate = mass*RATE
               
    period = (1.0/detector_rate)*1.0e6 # usec
    print "MASS: ",mass*0.001," tonnes"
    print "RATE: ",detector_rate
    print "PERIOD: ",period," microseconds"
    print "Total PMT efficiency: ",QE*CE
    eventid[0] = 0
    tevent[0] = 0.0
    while eventid[0]<nevents:
        if eventid[0]%1000==0:
            print "Event: ",eventid[0]
        # gen dt
        dt[0] = np.random.exponential( period )
        # t
        tevent[0] += dt[0]
        # gen position (then add offset)
        pos = genDecayPosition()
        for i in range(0,3):
            posv[i] = pos[i]
        # gen energy
        energy[0] = 0.600 # MeV
        eventid[0] += 1
        opcounts = photonlibrary.photonlib.getOpChannelCounts( pos )
        nphotons[0] = 0
        npe[0] = 0
        nhits[0] = 0
        fastcomp[0] = -1
        for opch,counts in enumerate(opcounts):
            pmt[0] = opch
            nphotons[0] += counts*(LY*energy[0])
            npe[0] += counts*(LY*energy[0])*CE*QE*TPB
            ophits = np.random.poisson( counts*(LY*energy[0])*CE*QE*TPB )
            nhits[0] += ophits
            for ihit in xrange(0,ophits):
                if np.random.random()<FASTFRAC:
                    fastcomp[0] = 1
                    dthit[0] = np.random.exponential( FASTCONST )
                    thit[0] = tevent[0] + dthit[0]
                else:
                    fastcomp[0] = 0
                    dthit[0] = np.random.exponential( SLOWCONST )
                    thit[0] = tevent[0] + dthit[0]
                petree.Fill()
        eventtree.Fill()
        
    eventtree.Write()
    petree.Write()
        

def plotSlice( photonlibrary, xslice=None, yslice=None, zslice=None, reducefactor=1 ):
    if xslice is None and yslice is None and zslice is None:
        raise ValueError('c\'mon, pick at least one slice!')
    if xslice is not None:
        slicemin = photonlibrary.xmin
        slicemax = photonlibrary.xmax
        nslices = photonlibrary.Nx/reducefactor
        slicename = "xslice"
        slice = xslice
        slicemin1 = photonlibrary.zmin
        slicemax1 = photonlibrary.zmax
        nslices1  = photonlibrary.Nz/reducefactor
        slicemin2 = photonlibrary.ymin
        slicemax2 = photonlibrary.ymax
        nslices2  = photonlibrary.Ny/reducefactor
    elif yslice is not None:
        slicemin = photonlibrary.ymin
        slicemax = photonlibrary.ymax
        nslices = photonlibrary.Ny/reducefactor
        slicename = "yslice"
        slice = yslice
        slicemin1 = photonlibrary.zmin
        slicemax1 = photonlibrary.zmax
        nslices1  = photonlibrary.Nz/reducefactor
        slicemin2 = photonlibrary.xmin
        slicemax2 = photonlibrary.xmax
        nslices2  = photonlibrary.Nx/reducefactor
    elif zslice is not None:
        slicemin = photonlibrary.zmin
        slicemax = photonlibrary.zmax
        nslices = photonlibrary.Nz/reducefactor
        slicename = "zslice"
        slice = zslice
        slicemin1 = photonlibrary.xmin
        slicemax1 = photonlibrary.xmax
        nslices1  = photonlibrary.Nx/reducefactor
        slicemin2 = photonlibrary.ymin
        slicemax2 = photonlibrary.ymax
        nslices2  = photonlibrary.Ny/reducefactor

    voxid = int( ( slice-slicemin )/nslices )
    hname = "%s_voxel%d"%(slicename,voxid)
    t2 = TH2D( hname, "", nslices1, slicemin1, slicemax1, nslices2, slicemin2, slicemax2 )
    binsprocessed = 0
    for ix in xrange(1,t2.GetNbinsX()+1):
        for iy in xrange(1,t2.GetNbinsY()+1):
            xval = t2.GetXaxis().GetBinCenter( ix )
            yval = t2.GetYaxis().GetBinCenter( iy )
            if xslice is not None:
                pos = np.asarray( [ xslice, yval, xval ] )
            elif yslice is not None:
                pos = np.asarray( [ yval, yslice, xval ] )
            elif zslice is not None:
                pos = np.asarray( [ xval, yval, zslice ] )
            else:
                pass
            opcounts = photonlibrary.photonlib.getOpChannelCounts( pos )
            for opch,counts in enumerate(opcounts):
                #print ix, iy, opch, counts
                t2.SetBinContent( ix, iy, t2.GetBinContent( ix, iy )+counts )
            binsprocessed += 1
            if binsprocessed%100==0:
                print "Bins processed: ",binsprocessed
    return t2
    

if __name__ == "__main__":
    out = TFile( "output.root", "RECREATE" )
    #c = TCanvas("c","c",800,400)
    #c.Draw()
    #t2 = plotSlice( pvs, yslice=0.0 )
    #t2.Draw("COLZ")
    #c.Update()
    #t2.Write()
    #raw_input()
    ar39mc( pvs, 10000 )

