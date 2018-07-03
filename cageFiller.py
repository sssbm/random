import pandas as pd
import unittest


class cage(object):

    def __init__(self, size, name):
        # Generates a new cage object.
        if "x" in size:
            # cage('100x200x200')
            self.heigth, self.width, self.length = [float(_) for _ in size.split('x')]
        else:
            # cage(100,200,200)
            self.heigth, self.width, self.length = size

        # Cage number
        self.name = name
        # Cage volume
        self.volume = self.heigth * self.width * self.length
        # Cage dimensions
        self.size = (self.heigth, self.width, self.length)
        # No of boxes 
        self.boxes = []
        # Volume occupied
        self.filledVolume = 0

    def addBoxToCage(self, productId, productVolume):
        self.boxes.append(productId)
        self.filledVolume += productVolume

    def getUtilisation(self):
        return ((self.filledVolume * 100) / self.volume)
    
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

    def getLength(self):
        return self.Length

    def __str__(self):
        return 'Cage(\t\n filledVolume: %d,\n boxes: %s\n\t)' % (self.filledVolume, str(self.boxes))


# Class to handle all boxes that does not fit a given cage
# due to dimension mismatch
class discarded(object):

    def __init__(self):
        # Boxes that are not in any cage due to dimension mismatch
        self.discarded = []

    def boxNotAdded(self, box):
        self.discarded.append(box)

    def __str__(self):
        return 'Boxes that does not fit in a cage: %s \n' % (str(self.discarded))

# To check if a given box will fit inside a given cage
def isCageable(box, cg):
    # Box dimensions cm to mm
    bHeight = box[1] / 10
    bWidth = box[2] / 10
    bLength = box[3] / 10

    # Box HxWxL <= Cage HxWxL
    if (bHeight <= cg.heigth and bWidth <= cg.width and bLength <= cg.length):
        return True
    # Box LxHxW <= Cage HxWxL
    elif (bLength <= cg.heigth and bHeight <= cg.width and bWidth <= cg.length):
        return True
    # Box WxLxH <= Cage HxWxL
    elif (bLength <= cg.heigth and bHeight <= cg.width and bWidth <= cg.length):
        return True

    return False


def pack(boxes):
    cgs = []
    cageNo = 0
    dbox = discarded()
    
    for box in boxes:
        # Try to fit a box in a cage
        for cg in cgs:
            # If the box exceeds cage dimension keep it separate
            if isCageable(box, cg):
                if cg.filledVolume + box[5] <= cg.volume:
                    # print ('Adding', box[5], 'to', cg)
                    cg.addBoxToCage(box[0],box[5]) # Product Id, Volume
                    break
            else:
                dbox.boxNotAdded(box)
        else:
            # Cage number
            cageNo += 1
            # Box didn't fit into any cage (or no cage), get a new cage
            cg = cage((newCageDim), cageNo)
            # print ('Getting a new cage with dimensions(HxWxL)(cm)', cg.size)
            if isCageable(box, cg):
                cg.addBoxToCage(box[0],box[5]) # Product Id, Volume
            else:
                dbox.boxNotAdded(box)
            cgs.append(cg)
    return cgs, dbox


if __name__ == '__main__':

    colnames = ['ProductId', 'H', 'W', 'L', 'Qty'] 
    df = pd.read_csv('data\CageProducts.csv', names=colnames, header=None, skiprows=[0])

    # H: 1.603m:160.3cm, W: 0.697m:69.7cm, L: 0.846m:84.6cm
    newCageDim = '160.3x69.7x84.6'

    # Unpack all boxes, based on Qty
    df = pd.DataFrame([df.ix[idx] for idx in df.index for _ in range(df.ix[idx]['Qty'])]).reset_index(drop=True)

    # mm to cm for consistency
    df = df.assign(vol=((df.H * df.W * df.L)) / 1000)
    df = df.sort_values('vol', ascending=False)

    # Total number of boxes to be caged
    print ('Total number of boxes to be caged:', df.shape[0])
    
    # Total volume of all boxes
    print ('Total volume of all boxes: %.3f ' % df['vol'].sum())
  
    dfLst = df.values.tolist()
    cgs, dbox = pack(dfLst)
  
    print ('Total Cages Used: ', len(cgs), '\r\n')
    for cg in cgs:
        print ('Cage number:', cg.name)
        print ('Cage dimension(HxWxL) in cm:', cg.size)
        print ('Cage volume: %.3f' % cg.volume)
        print ('Total filled in volume:', cg.filledVolume)
        print ('Cage utilisation volume:%.3f' % cg.getUtilisation(), '%')
        print (cg, '\r\n')
        print('\r\n')
  
    # Boxes that does not fit a given cage
    print (dbox)


# Tests
class cageTests(unittest.TestCase):

    def test_initPass(self):
        self.assertEqual(cage((100, 100, 200)).size, cage((100, 100, 200)).size)
        self.assertEqual(cage((100.0, 200.0, 200.0)).size, cage('100x200x200').size)

    def test_volumeEquals(self):
        self.assertEqual(4000000, cage((100, 200, 200)).volume)
        self.assertEqual(1368, cage(('5.7x8x30')).volume)

    def test_volumeNotEquals(self):
        self.assertNotEqual(16319, cage(('15.3x26.8x39.8')).volume)
