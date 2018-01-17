# -*- coding: utf-8 -*-
import math
from math import sin, cos, sqrt, fabs, atan2
from math import pi as PI


# define ellipsoid
a = 6378245.0
f = 1 / 298.3
b = a * (1 - f)
ee = 1 - (b * b) / (a * a)

class Transform():

    def outOfChina(self, lng, lat):
        """check weather lng and lat out of china
        
        Arguments:
            lng {float} -- longitude
            lat {float} -- latitude
        
        Returns:
            Bollen -- True or False
        """
        return not (72.004 <= lng <= 137.8347 and 0.8293 <= lat <= 55.8271)


    def transformLat(self, x, y):
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * sqrt(fabs(x))
        ret = ret + (20.0 * sin(6.0 * x * PI) + 20.0 * sin(2.0 * x * PI)) * 2.0 / 3.0
        ret = ret + (20.0 * sin(y * PI) + 40.0 * sin(y / 3.0 * PI)) * 2.0 / 3.0
        ret = ret + (160.0 * sin(y / 12.0 * PI) + 320.0 * sin(y * PI / 30.0)) * 2.0 / 3.0
        return ret


    def transformLon(self, x, y):
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x +  0.1 * x * y + 0.1 * sqrt(fabs(x))
        ret = ret + (20.0 * sin(6.0 * x * PI) + 20.0 * sin(2.0 * x * PI)) * 2.0 / 3.0
        ret = ret + (20.0 * sin(x * PI) + 40.0 * sin(x / 3.0 * PI)) * 2.0 / 3.0
        ret = ret + (150.0 * sin(x / 12.0 * PI) + 300.0 * sin(x * PI / 30.0)) * 2.0 / 3.0
        return ret


    def wgs2gcj(self, wgsLon, wgsLat):
        """wgs coord to gcj
        
        Arguments:
            wgsLon {float} -- lon
            wgsLat {float} -- lat
        
        Returns:
            tuple -- gcj coords
        """

        if self.outOfChina(wgsLon, wgsLat):
            return wgsLon, wgsLat
        dLat = self.transformLat(wgsLon - 105.0, wgsLat - 35.0)
        dLon = self.transformLon(wgsLon - 105.0, wgsLat - 35.0)
        radLat = wgsLat / 180.0 * PI
        magic = math.sin(radLat)
        magic = 1 - ee * magic * magic
        sqrtMagic = sqrt(magic)
        dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * PI)
        dLon = (dLon * 180.0) / (a / sqrtMagic * cos(radLat) * PI)
        gcjLat = wgsLat + dLat
        gcjLon = wgsLon + dLon
        return (gcjLon, gcjLat)


    def gcj2wgs(self, gcjLon, gcjLat):
        g0 = (gcjLon, gcjLat)
        w0 = g0
        g1 = self.wgs2gcj(w0[0], w0[1])
        # w1 = w0 - (g1 - g0)
        w1 = tuple(map(lambda x: x[0]-(x[1]-x[2]), zip(w0,g1,g0)))
        # delta = w1 - w0
        delta = tuple(map(lambda x: x[0] - x[1], zip(w1, w0)))
        while (abs(delta[0]) >= 1e-6 or abs(delta[1]) >= 1e-6):
            w0 = w1
            g1 = self.wgs2gcj(w0[0], w0[1])
            # w1 = w0 - (g1 - g0)
            w1 = tuple(map(lambda x: x[0]-(x[1]-x[2]), zip(w0,g1,g0)))
            # delta = w1 - w0
            delta = tuple(map(lambda x: x[0] - x[1], zip(w1, w0)))
        return w1


    def gcj2bd(self, gcjLon, gcjLat):
        z = sqrt(gcjLon * gcjLon + gcjLat * gcjLat) + 0.00002 * sin(gcjLat * PI * 3000.0 / 180.0)
        theta = atan2(gcjLat, gcjLon) + 0.000003 * cos(gcjLon * PI * 3000.0 / 180.0)
        bdLon = z * cos(theta) + 0.0065
        bdLat = z * sin(theta) + 0.006
        return (bdLon, bdLat)


    def bd2gcj(self, bdLon, bdLat):
        x = bdLon - 0.0065
        y = bdLat - 0.006
        z = sqrt(x * x + y * y) - 0.00002 * sin(y * PI * 3000.0 / 180.0)
        theta = atan2(y, x) - 0.000003 * cos(x * PI * 3000.0 / 180.0)
        gcjLon = z * cos(theta)
        gcjLat = z * sin(theta)
        return (gcjLon, gcjLat)


    def wgs2bd(self, wgsLon, wgsLat):
        gcj = self.wgs2gcj(wgsLon, wgsLat)
        return self.gcj2bd(gcj[0], gcj[1])


    def bd2wgs(self, bdLon, bdLat):
        gcj = self.bd2gcj(bdLon, bdLat)
        return self.gcj2wgs(gcj[0], gcj[1])


if __name__ == '__main__':
    transform = Transform()
    aa = getattr(transform, 'bd2gcj')(120, 40)
    print(aa)