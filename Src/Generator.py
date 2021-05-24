import cv2
import numpy as np
import math
import json
import pickle


def _reportMousePoint(event,x,y,flags,param):
    if event==cv2.EVENT_LBUTTONDOWN:
        print(x, "##", y, "##", flags, "##")

class Point:
    x = 0
    y = 0

class Point3d:
    x = 0
    y = 0
    z = 0

class CurveBezier:

    def __init__(self):
        self.point0 = Point()
        self.point1 = Point()
        self.point2 = Point()
        self.point3 = Point()
        self.nextCurve = None
    
    def getPoint(self, t):
        result = Point()
        result.x = self.point0.x*((1-t)**3) + 3*self.point1.x*t*((1-t)**2) + 3*self.point2.x*(t**2)*(1-t) + self.point3.x*(t**3)
        result.y = self.point0.y*((1-t)**3) + 3*self.point1.y*t*((1-t)**2) + 3*self.point2.y*(t**2)*(1-t) + self.point3.y*(t**3)
        return result

    def drawPoint(self, picture, color, index):
        point = self.point0
        if index is 0:
            point = self.point0
        elif index is 1:
            point = self.point1
        elif index is 2:
            point = self.point2
        elif index is 3:
            point = self.point3
        cv2.rectangle(picture, (point.x-3,point.y-3), (point.x+3,point.y+3),color,2)

    def setPoint(self, index, x, y):
        point = self.point0
        if index is 0:
            point = self.point0
        elif index is 1:
            point = self.point1
        elif index is 2:
            point = self.point2
        elif index is 3:
            point = self.point3
        point.x = x
        point.y = y

    def drawCurve(self, picture, color):
        time = np.arange(start=0, stop=1, step=0.001, dtype=np.float32)
        points_x = self.point0.x * ((1 - time) ** 3) + 3 * self.point1.x * time * ((1 - time) ** 2) + 3 * self.point2.x * (time ** 2) * (1 - time) + self.point3.x * (time ** 3)
        points_y = self.point0.y * ((1 - time) ** 3) + 3 * self.point1.y * time * ((1 - time) ** 2) + 3 * self.point2.y * (time ** 2) * (1 - time) + self.point3.y * (time ** 3)
        points_x = np.floor(points_x)
        points_y= np.floor(points_y)

        for index in range(len(time)):
            picture[int(points_y[index])][int(points_x[index])] = color

    def exportCurveTrack(self, time, step):
        time_list = np.arange(start=0, stop=time, step=step, dtype=np.float32)
        time_uniformization = time_list/time
        curve_t_uniformization = -10* time_uniformization ** 6 + 36* time_uniformization ** 5 - 45* time_uniformization** 4 + 20 * time_uniformization** 3
        # uniform time and caculate bezier para
        points_x = self.point0.x * ((1 - curve_t_uniformization) ** 3) + 3 * self.point1.x * curve_t_uniformization * ((1 - curve_t_uniformization) ** 2) + 3 * self.point2.x * (curve_t_uniformization ** 2) * (1 - curve_t_uniformization) + self.point3.x * (curve_t_uniformization ** 3)
        points_y = self.point0.y * ((1 - curve_t_uniformization) ** 3) + 3 * self.point1.y * curve_t_uniformization * ((1 - curve_t_uniformization) ** 2) + 3 * self.point2.y * (curve_t_uniformization ** 2) * (1 - curve_t_uniformization) + self.point3.y * (curve_t_uniformization ** 3)
        points_z = np.zeros((int(time/step)))
        return points_x,points_y,points_z
        

class Canva:
    windowName = ""
    fileName = ""
    curveList = list()
    nowCurve = 0
    nowPoint = 0
    curvePicture = 255*np.ones((700, 700, 3), np.uint8)
    textPicture = np.ones((700, 700, 3), np.uint8)


    def loadPicture(self, path):
        self.textPicture = cv2.imread(path)
        allPic = cv2.addWeighted(self.curvePicture, 0.7, self.textPicture, 0.3, 0)
        cv2.namedWindow(self.windowName)
        cv2.imshow(self.windowName, allPic)

    def createNewCurve(self):
        self.curveList.append(CurveBezier())

    def createLinkedNewCurve(self):

        newCurve.point0 = self.curveList[self.nowCurve].point3

    def saveCurves(self, path):
        file = open(path, 'wb')
        pickle.dump(self.curveList, file)

    def readCurves(self, path):
        file = open(path, 'rb')
        self.curveList = pickle.load(file)
        self.drawAllCurve()

    def deleteNowCurve(self):
        try:
            self.curveList.pop(self.nowCurve)
        except:
            print("没有找到曲线")

    def drawAllCurve(self):
        self.curvePicture = 255 * np.ones((700, 700, 3), np.uint8)
        for each_curve in self.curveList:
            each_curve.drawCurve(self.curvePicture, (200, 0, 0))
            each_curve.drawPoint(self.curvePicture, (200, 0, 0), 0)
            each_curve.drawPoint(self.curvePicture, (200, 0, 0), 1)
            each_curve.drawPoint(self.curvePicture, (200, 0, 0), 2)
            each_curve.drawPoint(self.curvePicture, (200, 0, 0), 3)
        try:
            self.curveList[self.nowCurve].drawCurve(self.curvePicture, (0, 0, 200))
            self.curveList[self.nowCurve].drawPoint(self.curvePicture, (0, 0, 200), self.nowPoint)
            cv2.imshow(self.windowName, cv2.addWeighted(self.curvePicture, 0.7, self.textPicture, 0.3, 0))
        except:
            print("没有找到曲线")

    def keyProcess(self, key_value):
        key = chr(key_value)
        if key is 'a':
            if self.nowCurve > 0:
                self.nowCurve -= 1
                self.nowPoint=0
                self.drawAllCurve()
        elif key is 'd':
            if self.nowCurve < len(self.curveList)-1:
                self.nowCurve += 1
                self.nowPoint=0
                self.drawAllCurve()
        elif key is 's':
            if self.nowPoint > 0:
                self.nowPoint -= 1
                self.drawAllCurve()
        elif key is 'w':
            if self.nowPoint < 3:
                self.nowPoint += 1
                self.drawAllCurve()
        elif key is 'f':
            self.createNewCurve()
            self.drawAllCurve()
        elif key is 'q':
            self.saveCurves("curve1")
        elif key is 'z':
            self.exportRobotTrack("result")

    def mouseProcess(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.curveList[self.nowCurve].setPoint(self.nowPoint, x, y)
            self.drawAllCurve()

    def linkNameWithCallBack(self):
        cv2.setMouseCallback(self.windowName, self.mouseProcess)

    def coordinateTrans(self, x_list, y_list, z_list):
        paper_center = Point3d()
        paper_center.x = 915
        paper_center.y = 0
        paper_center.z = 436.9

        paper_wide = 400
        paper_height = 300

        # 注意！！！ 狗opencv xy轴是反的
        x_list, y_list = y_list, x_list

        x_list = (x_list/7*3)  # Scale matrix
        y_list = (y_list/7*3)

        x_list += paper_center.x - (paper_height/2)
        y_list += paper_center.y - (paper_wide/2)
        z_list += paper_center.z


        return x_list, y_list, z_list

    def exportRobotTrack(self, path):
        result_x = np.array(())
        result_y = np.array(())
        result_z = np.array(())
        length = len(self.curveList)
        for curve_index in range(length):
            curve_x,curve_y,curve_z = self.curveList[curve_index].exportCurveTrack(0.5,0.01)

            result_x = np.append(result_x, curve_x)
            result_y = np.append(result_y, curve_y)
            result_z = np.append(result_z, curve_z)

            if curve_index != length-1:
                # 因为还要复习C语言所以全用直线连接了
                point_down1 = Point3d()
                point_down2 = Point3d()
                point_up1 = Point3d()
                point_up2 = Point3d()
                point_up1.x = self.curveList[curve_index].point3.x
                point_up1.y = self.curveList[curve_index].point3.y
                point_up1.z = 20
                
                point_down1.x = self.curveList[curve_index].point3.x
                point_down1.y = self.curveList[curve_index].point3.y
                point_down1.z = 0
                
                point_up2.x = self.curveList[curve_index+1].point0.x
                point_up2.y = self.curveList[curve_index+1].point0.y
                point_up2.z = 20
                
                point_down2.x = self.curveList[curve_index+1].point0.x
                point_down2.y = self.curveList[curve_index+1].point0.y
                point_down2.z = 0
                # 抬刀
                line_x, line_y, line_z = self.exportGenerateLineTrack(0.3, 0.01, point_down1, point_up1)
                result_x = np.append(result_x, line_x)
                result_y = np.append(result_y, line_y)
                result_z = np.append(result_z, line_z)
                line_x, line_y, line_z = self.exportGenerateLineTrack(0.3, 0.01, point_up1, point_up2)
                result_x = np.append(result_x, line_x)
                result_y = np.append(result_y, line_y)
                result_z = np.append(result_z, line_z)
                line_x, line_y, line_z = self.exportGenerateLineTrack(0.3, 0.01, point_up2, point_down2)
                result_x = np.append(result_x, line_x)
                result_y = np.append(result_y, line_y)
                result_z = np.append(result_z, line_z)

        # 变换坐标系并写入result文件
        result_x,result_y,result_z = self.coordinateTrans(result_x, result_y, result_z)
        file = open(path, 'w')

        file.write(str(result_x[0])+" "+str(result_y[0])+" "+str(result_z[0])+" ")
        for each_x in range(len(result_x)-3):
            file.write("0 ")  # 凑数用的
        file.write("\n")

        file.write(str(result_x[len(result_x)-1])+" "+str(result_y[len(result_y)-1])+" "+str(result_z[len(result_z)-1])+" ")
        for each_x in range(len(result_x)-3):
            file.write("0 ")  # 凑数用的
        file.write("\n")

        # motion track
        for each_x in result_x:
            file.write(str(each_x)+" ")
        file.write("\n")
        for each_y in result_y:
            file.write(str(each_y)+" ")
        file.write("\n")
        for each_z in result_z:
            file.write(str(each_z)+" ")
        file.close()

    def exportGenerateLineTrack(self, time, step, start_point, end_point):
        time_list = np.arange(start=0, stop=time, step=step, dtype=np.float32)
        time_uniformization = time_list / time
        curve_t_uniformization = -10 * time_uniformization ** 6 + 36 * time_uniformization ** 5 - 45* time_uniformization** 4 + 20 * time_uniformization** 3
        result_x = (1 - curve_t_uniformization) * start_point.x + curve_t_uniformization * end_point.x
        result_y = (1 - curve_t_uniformization) * start_point.y + curve_t_uniformization * end_point.y
        result_z = (1 - curve_t_uniformization) * start_point.z + curve_t_uniformization * end_point.z
        return result_x,result_y,result_z



genCanva = Canva()
genCanva.fileName = "curvepkg1"
genCanva.windowName = "Generator"
genCanva.loadPicture("font.png")
try:
    genCanva.readCurves("curve1")
except:
    print("curve1 not found")
genCanva.linkNameWithCallBack()

while 1:
    key = cv2.waitKey(0)
    genCanva.keyProcess(key)
